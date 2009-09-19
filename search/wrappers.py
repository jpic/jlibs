from django import forms
from django.db.models.query import QuerySet

from exceptions import *
from jlibs import options as joptions

class FilterWrapper(joptions.FormOption, dict):
    def __init__(self, queryset=None, url='/', form=None, form_class=None, \
        auto_add_missing_filters=True):
        self.queryset = queryset
        self.url = url
        self.auto_add_missing_filters = auto_add_missing_filters

        super(FilterWrapper, self).__init__(form=form, form_class=form_class)

    def parse_request(self, request):
        if not self.auto_add_missing_filters and not self.form_class \
            and not len(self.keys()):
            raise Exception('Not parsing a request before filters are added, unless auto_add_missing_filters and form_class with fields ')

        self.request = request

        if self.auto_add_missing_filters:
            self.add_missing_fields()

        for name, filter in self.items():
            filter.parse_request(name, request)

        return self

    def filter_url(self):
        url = self.url

        for name, filter in self.items():
            url = filter.filter_url(name, url)
  
        return url

    def filter_queryset(self):
        if not isinstance(self.queryset, QuerySet):
            raise NoneQuerysetException()

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
