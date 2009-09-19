from django.forms import models as form_models
from django.db import models
from django.contrib import admin
from django import template
from django.conf.urls.defaults import patterns
from django.utils.functional import update_wrapper

from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote

from django.conf import settings

import jsearch
import jforms

class ModelAdmin(admin.ModelAdmin):
    def get_menu(self):
        return self.admin_site.get_menu()

    def get_urls(self):        
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^autocomplete/$',
                wrap(self.autocomplete_view),
                name='%sadmin_%s_%s_autocomplete' % info),
        ) + super(ModelAdmin, self).get_urls()
        return urlpatterns

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        Adds jmenu to context before super'ing.
        """
        context.update({'jmenu': self.get_menu()})

        response = super(ModelAdmin, self).render_change_form(request, context, add, change, form_url, obj)
        return response

    def changelist_view(self, request, extra_context=None):
        self.search_engine = self.create_search_engine(request)
        self.search_engine.parse_request(request)

        extra_context = {
            'jsearch': self.search_engine,
            'jmenu': self.get_menu(),
        }

        extra_context.update({'jmenu': self.get_menu()})

        opts = self.model._meta
        app_label = opts.app_label

        return super(ModelAdmin, self).changelist_view(request, extra_context)

    def queryset(self, request):
        return self.search_engine.filter_queryset()

    def delete_view(self, request, object_id, extra_context=None):
        """
        Add jmenu to the context and super
        """
        if not extra_context:
            extra_context = {}
        extra_context['jmenu'] = self.get_menu()
        return super(ModelAdmin, self).delete_view(request, object_id, extra_context)
    def history_view(self, request, object_id, extra_context=None):
        """
        Add jmenu to the context and super
        """
        if not extra_context:
            extra_context = {}
        extra_context['jmenu'] = self.get_menu()
        return super(ModelAdmin, self).history_view(request, object_id, extra_context)

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

            info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
            name = '%sadmin_%s_%s_autocomplete' % info

            autocomplete_url = reverse(name)
   
            if jrelation_search_fields:
                kwargs['widget'] = widget(db_field.rel, jrelation_search_fields, autocomplete_url=autocomplete_url)
        
        field = super(ModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        return field

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
