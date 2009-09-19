from django import forms

import joptions

class BaseFilter(joptions.FormFieldOption):
    def __init__(self,
        queryset_filter_type='iexact', value=None,
        formfield = None, formfield_class = None,
        url_name_value_separator=':', restrict_request_method=()):
        """
        >>> from django import forms
        >>> formfield_fixture = forms.CharField()
        >>> f = BaseFilter(
        ... queryset_filter_type='test0',
        ... formfield=formfield_fixture,
        ... value='test1',
        ... url_name_value_separator='~',
        ... restrict_request_method=('post',)
        ... )
        >>> f.queryset_filter_type
        'test0'
        >>> f.formfield == formfield_fixture
        True
        >>> f.value
        'test1'
        >>> f.url_name_value_separator 
        '~'
        >>> f.restrict_request_method 
        ('post',)
        >>> try:
        ...     failed = False
        ...     fail = BaseFilter(formfield='foo')
        ... except Exception:
        ...     failed = True
        >>> failed
        True
        """
        super(BaseFilter, self).__init__(formfield, formfield_class)

        if restrict_request_method:
            for method in restrict_request_method:
                if method not in ('post', 'get'):
                    raise Exception('restrict_request_method may not hold anything else than "post" and/or "get"')

        self.queryset_filter_type = queryset_filter_type
        self.value = value
        self.url_name_value_separator = url_name_value_separator
        self.restrict_request_method = restrict_request_method

    def filter_form(self, name, form):
        """
        >>> from django import forms
        >>> form = forms.Form()
        >>> formfield_fixture = forms.CharField()
        >>> class BaseFilterMock(BaseFilter):
        ...     def create_formfield(self):
        ...         return self.formfield_fixture
        ...     
        >>> mock = BaseFilterMock()
        >>> mock.formfield_fixture = formfield_fixture
        >>> mock.filter_form('foo', form)
        >>> formfield_fixture == form.fields['foo']
        True
        >>> has_formfield = BaseFilter(formfield=formfield_fixture)
        >>> mock.filter_form('bar', form)
        >>> form.fields['bar'] == formfield_fixture
        True
        """
        if not self.formfield:
            self.formfield = self.create_formfield()

        form.fields[name] = self.formfield

        return form

    def filter_url(self, name, url = '/'):
        """
        >>> class BaseFilterMock(BaseFilter):
        ...     def create_urlfilter(self, name):
        ...         return 'foo%sbar' % name
        ... 
        >>> f = BaseFilterMock()
        >>> f.filter_url('test', '/unit')
        '/unit'
        >>> f.value = 'somevalue'
        >>> f.filter_url('test', '/unit')
        '/unit/footestbar/'
        """
        if self.value == None:
            return url

        if not url[-1] == '/':
            url += '/'

        return '%s%s/' % (url, self.create_urlfilter(name))
    
    def filter_queryset(self, name, queryset):
        """
        >>> raise Exception("filter_queryset *NOT* tested")
        """
        if self.value:
            # Credits: habnabit from #python@freenode
            return queryset.filter( **{ '%s__%s' % (name, self.queryset_filter_type): self.value} )
        else:
            return queryset
   
    def parse_request(self, name, request):
        """
        >>> from django.http import HttpRequest
        >>> request = HttpRequest()
        >>> request.method = 'POST'
        >>> class BaseFilterMock(BaseFilter):
        ...     def __init__(self, **kwargs):
        ...         self.post_parsed = self.get_parsed = False
        ...         super(BaseFilterMock, self).__init__(**kwargs)
        ...     def parse_get(self, request):
        ...         self.get_parsed = True
        ...     def parse_post(self, request):
        ...         self.post_parsed = True
        ... 
        >>> m = BaseFilterMock()
        >>> m.post_parsed 
        False
        >>> m.get_parsed 
        False
        >>> m.parse_request(request)
        >>> m.get_parsed
        True
        >>> m.post_parsed
        True
        >>> m = BaseFilterMock()
        >>> request.method = 'GET'
        >>> m.parse_request(request)
        >>> m.post_parsed
        False
        >>> m.get_parsed
        True
        >>> m = BaseFilterMock(restrict_request_method=('get',))
        >>> request.method = 'GET'
        >>> m.parse_request(request)
        >>> m.post_parsed
        False
        >>> m.get_parsed
        False
        >>> m = BaseFilterMock(restrict_request_method=('post',))
        >>> request.method = 'POST'
        >>> m.parse_request(request)
        >>> m.post_parsed
        False
        >>> m.get_parsed
        True
        """
        print "Anything in post?", request.POST
        if 'get' not in self.restrict_request_method:
            self.parse_get(name, request)

        if 'post' not in self.restrict_request_method \
            and request.method == 'POST':
            self.parse_post(name, request)

    def get_formfield(self):
        return self.formfield_class(initial=self.value)

    def get_formfield_class(self):
        return forms.CharField

    def parse_post(self, name, request):
        """
        >>> k = 'bar'
        >>> v = 'foo'
        >>> from django.http import HttpRequest
        >>> request = HttpRequest()
        >>> f = ValueFilter()
        >>> f.parse_post(k, request)
        >>> f.value
        >>> request.POST[v] = k
        >>> f.parse_post(k, request)
        >>> f.value
        >>> request.POST[k] = v
        >>> f.parse_post(k, request)
        >>> f.value
        'foo'
        """
        print "Parsing post for", name
        if name in request.POST and request.POST[name]:
            print "Found some nvalue in post for", name, request.POST[name]
            self.value = self.formfield.clean(request.POST[name])

class ValueFilter(BaseFilter):
    def create_urlfilter(self, name):
        """
        >>> f = ValueFilter()
        >>> f.create_urlfilter('foo')
        >>> f.value='bar'
        >>> f.create_urlfilter('foo')
        'foo:bar'
        """
        if self.value:
            return '%s%s%s' % (name, self.url_name_value_separator, self.value)

    def get_formfield_class(self):
        """
        >>> f = ValueFilter()
        >>> f.create_formfield().__class__.__name__
        'CharField'
        >>> f.create_formfield().initial
        >>> f = ValueFilter(value='bar')
        >>> f.create_formfield().__class__.__name__
        'CharField'
        >>> f.create_formfield().initial
        'bar'
        """
        return forms.CharField

    def parse_get(self, name, request):
        """
        >>> from django.http import HttpRequest
        >>> request = HttpRequest()
        >>> request.path = '/foo/bar/'
        >>> f = ValueFilter()
        >>> f.parse_get('foo', request)
        >>> f.value
        >>> request.path = '/foo:bar/'
        >>> f.parse_get('foo', request)
        >>> f.value
        'bar'
        """
        for part in request.path.split('/'):
            position = part.find(self.url_name_value_separator)
            if part.find(name) == 0 and position > 0:
                self.value = part[position+1:]
    
#class SingleInputMultiValueFilter(BaseFilter):
#    def __init__(self, *args,
#        # input_value_separator=',', # syntax restriction
#        **kwargs):
#        if 'input_value_separator' in kwargs:
#            self.input_value_separator = kwargs['input_value_separator']
#            kwargs.pop('input_value_separator')
#        else:
#            self.input_value_separator = ','
#        
#        super(SingleInputMultiValueFilter, self).__init__(*args, **kwargs)
#
#        if not self.value:
#            self.value = []
#
#    def create_urlfilter(self, name):
#        if len(self.value):
#            return '%s%s%s' % (name, self.url_name_value_separator, \
#                self.url_name_value_separator.join(self.value))
#
#    def create_formfield(self):
#        join_string = self.input_value_separator + ' '
#        return forms.CharField(initial=join_string.join(self.value))
#
#    def parse_get(self, name, request):
#        for part in request.path.split('/'):
#            if part.find(name) == 0:
#                if part.count(self.url_name_value_separator) > 0:
#                    values = part.split(self.url_name_value_separator)
#                    values.remove(name)
#                    self.value = values
#
#    def parse_post(self, request):
#        if name in request.POST:
#            for value in request.POST[name].split(','):
#                self.value.append(value.strip())
#
#class BooleanFilter(BaseFilter):
#    def parse_get(self, request):
#        for part in request.path.split('/'):
#            if part == name:
#                self.value = True
#            elif part == '!'+name:
#                self.value = False
#            else:
#                self.value = None
#
#    def filter_queryset(self, q):
#        if self.value in (True, False):
#            q = q.filter(**{ '%s__%s' % (self.queryset_field_descriptor, self.queryset_filter_type): self.value})
#        return q
#
#    def create_formfield(self):
#       return forms.BooleanField(initial=self.value)
#
#    def parse_post(self, request):
#        if name in request.POST and request.POST[name]:
#            self.value = True
#        else:
#            self.value = None
#
#class ChoicesFilter(SingleInputMultiValueFilter):
#    def __init__(self, urlname, queryset_field_descriptor = None, queryset_filter_type = 'in', choices = [] ):
#        super(ChoicesFilter, self).__init__(urlname, queryset_field_descriptor, queryset_filter_type)
#        self.choices = choices
#    def to_field(self):
#        field = forms.MultipleChoiceField(choices = self.choices, initial = self.value)
#        return field
#    def parse_input(self, request):
#        if name in request.POST:
#            # tip about getlist: zerok from #django@freenode
#            for id in request.POST.getlist(name):
#                for choice in self.choices:
#                    if choice[0] == id:
#                        self.value.append( choice[0] )
#
#class QuerySetChoicesFilter(ChoicesFilter):
#    def __init__(self, urlname, queryset, queryset_field_descriptor = None, queryset_filter_type = 'in'):
#        self.choices = self.get_choices( queryset )
#        super(QuerySetChoicesFilter, self).__init__( urlname, queryset_field_descriptor, queryset_filter_type, self.choices )
#    def get_choices(self, queryset):
#        choices = []
#        from django.template.defaultfilters import slugify
#        for object in queryset:
#            choices.append( ( slugify(str(object)) , object ) )
#        return choices
#    def to_queryset(self, q):
#        values = []
#        for value in self.value:
#            for choice in self.choices:
#                if choice[0] == value:
#                    object = choice[1]
#                    values.append( object.id )
#        if values:
#            q = q.filter( **{ '%s__%s' % (self.queryset_field_descriptor, self.queryset_filter_type): values} )
#        return q
#

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__": _test()
