class ModelDealer(object):
    def __init__(self, model=None, model_class=None):
        self._model = model
        self._model_class = model_class
        
    def model_class(self):
        if self._model:
            self._model_class = self._model_class
        if not self._model_class:
            self._model_class = self.get_model_class()
        return self._model_class
    model_class = property(model_class)

    def model(self):
        if not self._model:
            self._model = self.get_model()        
        return self._model
    model = property(model)

    def get_model(self):
        return self._model_class()

class FormFieldDealer(object):
    def __init__(self, formfield=None, formfield_class=None):
        self._formfield = formfield
        self._formfield_class = formfield_class
        
        if self._formfield:
            self._formfield_class = self._formfield.__class__

    def formfield_class(self):
        if self._formfield:
            self._formfield_class = self._formfield_class
        if not self._formfield_class:
            self._formfield_class = self.get_formfield_class()
        return self._formfield_class
    formfield_class = property(formfield_class)

    def formfield(self):
        if not self._formfield:
            self._formfield = self.get_formfield()        
        return self._formfield
    formfield = property(formfield)

    def get_formfield(self):
        return self._form_class()

class FormDealer(object):
    def __init__(self, form=None, form_class=None):
        self._form = form
        self._form_class = form_class
        
        if self._form:
            self._form_class = self._form.__class__

    def get_form_class(self):
        from django.forms import Form as DjangoForm
        return DjangoForm

    def form_class(self):
        if self._form:
            self._form_class = self._form_class
        if not self._form_class:
            self._form_class = self.get_form_class()
        return self._form_class
    form_class = property(form_class)

    def get_form(self):
        if not self.request:
            return self.form_class()
        else:
            return self.form_class(self.request.POST)

    def form(self):
        if not self._form:
            self._form = self.get_form()        
        return self._form
    form = property(form)


