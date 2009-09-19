from django.forms import models

from jlibs import options as joptions

import wrappers
import filters

class ModelSearch(wrappers.FilterWrapper, joptions.ModelOption):
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
        return models.modelform_factory(self.model_class, fields=self.search_fields,
            formfield_callback=self.formfield_for_dbfield)

    @classmethod
    def formfield_for_dbfield(form, field):
        formfield = field.formfield()
        if formfield:
            formfield.required = False
        return formfield

    def add_missing_fields(self):
        if self.auto_add_missing_filters:
            for name, field in self.form.fields.items():
                if name not in self.keys():
                    self[name] = self.filter_for_formfield(name, field)

    def filter_for_formfield(self, name, field):
        if isinstance(field, models.ModelChoiceField):
            return filters.ValueFilter(formfield=field, queryset_filter_type='exact')
        else:
            return filters.ValueFilter(formfield=field)
    
    def get_search_fields(self):
        fields = []
        # Get as many fields as possible here!
        return fields
