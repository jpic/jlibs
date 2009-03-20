# Done only in create_default_form():
# from django import forms

class FilterWrapper(dict):
    def __init__(self, queryset=None, url='/', form=None):
        self.queryset = queryset
        self.url = url
        self.form = form

        if not self.form:
            self.form = self.get_default_form()

    def parse_request(self, request):
        for name, filter in self.items():
            filter.parse_request(name, request)

    def filter_url(self):
        url = self.url

        for name, filter in self.items():
            url = filter.filter_url(name, url)
    
    def filter_queryset(self):
        if not self.queryset:
            raise Exception('Cannot filter a None queryset')

        for name, filter in self.items():
            filter.filter_queryset(name, queryset)

    def get_default_form(self)
        from django.forms import Form as DjangoForm
        return DjangoForm()
