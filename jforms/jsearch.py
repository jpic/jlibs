from django.db import models

import jforms
import jsearch

class ModelSearch(jsearch.ModelSearch):
    def get_form_class(self):
        return models.modelform_factory(
            self.model_class,
            form_class = jforms.ModelForm,
            fields=self.search_fields,
        )
