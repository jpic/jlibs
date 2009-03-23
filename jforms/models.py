# {{{ django deps
from django.db import models
from django.db import models as db_models
from django.forms import models
from django import forms
# }}}
# {{{ app deps
from widgets import  *
# }}}
# {{{ userapp deps
from django.conf import settings
# }}}

class ModelForm(models.ModelForm):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if hasattr(db_field, 'rel') and hasattr(db_field.rel, 'to'):
            if isinstance(db_field, models.ManyToManyField):
                widget = jforms.ManyToManySearchInput
            if isinstance(db_field, models.ForeignKey):
                widget = jforms.ForeignKeySearchInput

            jsearch_fields = self.get_jsearch_fields(db_field.rel.to)

            if jsearch_fields:
                kwargs['widget'] = widget(db_field.rel, jsearch_fields)
        
        return super(ModelForm, self).formfield_for_dbfield(db_field, **kwargs)

    def get_jsearch_fields(self, model):
        if not hasattr(self, 'jsearch_fields'):
            return None
        
        if model not in self.jsearch_fields:
            return None

        jsearch_fields = self.jsearch_fields[model]

        if not isinstance(jsearch_fields, (list, tuple)):
            jsearch_fields = (jsearch_fields,)

        return jsearch_fields
