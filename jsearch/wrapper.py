from django import forms
from django.forms import models

import jdealers
from jsearch.filters import *

class FilterWrapper(jdealers.FormDealer, dict):
    def __init__(self, queryset=None, url='/', form=None, form_class=None, \
        auto_add_missing_filters=True):
        self.queryset = queryset
        self.url = url
        self.auto_add_missing_filters = auto_add_missing_filters

        super(FilterWrapper, self).__init__(form=form, form_class=None)

    def parse_request(self, request):
        if not self.auto_add_missing_filters and not self.form_class \
            and not len(self.keys()):
            raise Exception('Not parsing a request before filters are added, unless auto_add_missing_filters and form_class with fields ')

        self.request = request

        if self.auto_add_missing_filters:
            self.add_missing_fields()

        for name, filter in self.items():
            print name, filter
            filter.parse_request(name, request)

        return self

    def filter_url(self):
        url = self.url

        for name, filter in self.items():
            self.url = filter.filter_url(name, url)
  
        return self.url

    def filter_queryset(self):
        if not self.queryset:
            raise Exception('Cannot filter a None queryset')

        for name, filter in self.items():
            self.queryset = filter.filter_queryset(name, self.queryset)

        return self.queryset

    def filter_form(self):
        for name, filter in self.items():
            if name not in self.form.fields:
                filter.filter_form(name, self.form)
            else:
                filter._formfield = self.form.fields[name]

        return self.form

    def add_missing_fields(self):
        if self.auto_add_missing_filters:
            for name, field in self.form.fields.items():
                if name not in self.keys():
                    self[name] = ValueFilter(formfield=field)

class ModelSearch(FilterWrapper, jdealers.ModelDealer):
    def __init__(self, **kwargs):
        if not 'model' in kwargs and not 'model_class' in kwargs \
            and not hasattr(self, 'get_model_class') \
            and not hasattr(self, 'get_model'):
            raise Exception('Need either a model or model_class')

        if 'model' in kwargs:
            self._model = kwargs.pop('model')
            self._model_class = self._model.__class__
        elif 'model_class' in kwargs:
            self._model = None
            self._model_class = kwargs.pop('model_class')

        if 'search_fields' in kwargs:
            self.search_fields = kwargs.pop('search_fields')
        else:
            self.search_fields = self.get_search_fields()

        super(ModelSearch, self).__init__(**kwargs)

    def get_form_class(self):
        return models.modelform_factory(self.model_class, fields=self.search_fields)

    def add_missing_fields(self):
        if self.auto_add_missing_filters:
            for name, field in self.form.fields.items():
                if name not in self.keys():
                    self[name] = self.filter_for_formfield(name, field)

    def filter_for_formfield(self, name, field):
        if isinstance(field, models.ModelChoiceField):
            return ValueFilter(formfield=field, queryset_filter_type='exact')
        else:
            return ValueFilter(formfield=field)
    
    def get_search_fields(self):
        fields = []
        # Get as many fields as possible here!
        return fields
