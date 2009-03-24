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
