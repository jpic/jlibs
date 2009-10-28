from django import forms

class QuerysetForm(forms.Form):
    def filter_queryset(self, queryset):
        return queryset
