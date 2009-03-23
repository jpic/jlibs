import operator
from django.db import models
from django.contrib.auth.models import Message
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str

def search(request):
    query = request.GET.get('q', None)
    app_label = request.GET.get('app_label', None)
    model_name = request.GET.get('model_name', None)

    if app_label and model_name and query:
        def construct_search(field_name):
            # use different lookup methods depending on the notation
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        model = models.get_model(app_label, model_name)

        if not hasattr(model, 'can_search') \
            or not model.can_search(request.user):
            return HttpResponseForbidden()

        if hasattr(model, 'get_search_fields'):
            search_fields = model.get_search_fields()

        qs = model._default_manager.all()

        for bit in query.split():
            or_queries = [models.Q(**{construct_search(
                smart_str(field_name)): smart_str(bit)})
                    for field_name in search_fields.split(',')]
            other_qs = QuerySet(model)
            other_qs.dup_select_related(qs)
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            qs = qs & other_qs
        
        data = ''.join([u'%s|%s\n' % (f.__unicode__(), f.pk) for f in qs])
        
        return HttpResponse(data)
    
    return HttpResponseNotFound() 
