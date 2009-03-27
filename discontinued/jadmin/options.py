from django.forms import models as form_models
from django.db import models
from django.contrib import admin
from django.shortcuts import render_to_response
from django import template

from django.conf import settings

import jsearch
import jforms

class ModelAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('jautocomplete/jquery.autocomplete.css',)
        }
        js = (
            'jquery.min.js',
            'jautocomplete/lib/jquery.bgiframe.min.js',
            'jautocomplete/lib/jquery.ajaxQueue.js',
            'jautocomplete/jquery.autocomplete.js',
            'js/php.min.js',
            '/media/js/urlify.js',
        )
    
    # Custom templates (designed to be over-ridden in subclasses)
    public_search_template = None

    def __init__(self, *args, **kwargs):
        print 'FIXME: jadmin.ModelAdmin.public_site.name hack'
        self.public_site_name = 'hack'
        super(ModelAdmin, self).__init__(*args, **kwargs)

    def get_public_urls(self):
        from django.conf.urls.defaults import patterns, url
        
        info = self.public_site_name, self.model._meta.app_label, self.model._meta.module_name
        
        urlpatterns = patterns('',
            url(r'^$',
                self.public_list_view,
                name='%spublic_%s_%s_list' % info),
            url(r'^(.+)/$',
                self.public_details_view,
                name='%spublic_%s_%s_details' % info),
        )

        return urlpatterns

    def public_urls(self):
        return self.get_public_urls()
    public_urls = property(public_urls)

    def public_details_view(self, request, object_id, extra_context=None):
        pass

    def public_list_view(self, request, extra_context=None):
        from jadmin.views.main import PublicList
        opts = self.model._meta
        app_label = opts.app_label

        # Allow overriding the public search engine
        if hasattr(self, 'create_public_search_engine'):
            self.search_engine = self.create_public_search_engine(request)
        # Use the changelist one by default
        else:
            self.search_engine = self.create_search_engine(request)
        
        # Parse the request at this point any way
        self.search_engine.parse_request(request)

        # PublicList extends ChangeList but calls for yourModel.url()
        from jadmin.views.main import PublicList
        try:
            cl = PublicList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        
        # Allow overriding the context
        context = {
            'jsearch': self.search_engine,
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
        }
        context.update(extra_context or {})

        # Allow overriding the template
        template_file = self.public_search_template or [
            "jadmin/%s/%s/public_search.html" % (app_label, opts.object_name.lower()),
            "jadmin/%s/public_search.html" % app_label,
            "jadmin/public_search.html"
        ]

        # Render to response
        return render_to_response(template_file,
            context, context_instance=template.RequestContext(request)) 

    def changelist_view(self, request, extra_context=None):
        self.search_engine = self.create_search_engine(request)
        self.search_engine.parse_request(request)

        extra_context = {
            'jsearch': self.search_engine,
        }

        return super(ModelAdmin, self).changelist_view(request, extra_context)

    def queryset(self, request):
        return self.search_engine.filter_queryset()

    def create_search_engine(self, request):
        form_class = form_models.modelform_factory(
            self.model,
            fields = self.get_jsearch_fields(request),
            formfield_callback = self.formfield_for_dbfield
        )

        engine = jsearch.ModelSearch(
            model_class = self.model,
            queryset = super(ModelAdmin, self).queryset(request),
            search_fields = self.get_jsearch_fields(request),
            form_class = form_class
        )
        return engine

    def get_jsearch_fields(self, request):
        if hasattr(self, 'jsearch_fields'):
            return self.jsearch_fields

        return None

    def formfield_for_dbfield(self, db_field, **kwargs):
        if hasattr(db_field, 'rel') and hasattr(db_field.rel, 'to'):
            if isinstance(db_field, models.ManyToManyField):
                widget = jforms.ManyToManySearchInput
            if isinstance(db_field, models.ForeignKey):
                widget = jforms.ForeignKeySearchInput

            jrelation_search_fields = self.get_jrelation_search_fields(db_field.rel.to)

            if jrelation_search_fields:
                kwargs['widget'] = widget(db_field.rel, jrelation_search_fields)
        
        return super(ModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_jrelation_search_fields(self, model):
        if not hasattr(self, 'jrelation_search_fields'):
            return None
        
        if model not in self.jrelation_search_fields:
            return None

        jrelation_search_fields = self.jrelation_search_fields[model]

        if not isinstance(jrelation_search_fields, (list, tuple)):
            jrelation_search_fields = (jrelation_search_fields,)

        return jrelation_search_fields

#class TabularInline(admin.TabularInline):
#    form = jforms.ModelForm
#
#class StackedInline(admin.StackedInline):
#    form = jforms.ModelForm
