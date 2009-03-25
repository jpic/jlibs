State
~~~~~

poc

Applications
~~~~~~~~~~~~

jsearch
=======

Overview
--------

The search engine converts input to forms and querysets.

It can parse the following types of input:
- get,
- post.

It can generate:
- forms,
- querysets.

It starts being useful ootb when provided the following elements:
- a base queryset,
- filters.

Some basic view helpers are also provided.

Filter class
------------

parse_request( name, request )
    Tryes to find a relevant filter value in a `request` object, using `name`.

filter_url( name, url = '/' )
    Adds it name and value to `url`, in a form that it can parse, then return the resulting url.

filter_form( name, form = django.forms.Form )
    Adds its form field to `form` with `name`.

filter_queryset( name, queryset )
    Adds its filter to `queryset` using field `name`.

FilterWrapper class
-------------------

The FilterWrapper extends the built-in `dict` type, and is intended to wrap around a set of named filters::

    # Step 0: defining the wrapper
    filter_wrapper = jsearch.FilterWrapper(
        queryset = Users.objects.all(), # optionnal (default: none)
        url = '/',                      # default
        form = django.forms.Form,       # default
    )

    # Adding fields ...
    filter_wrapper['last_name'] = jsearch.ValueFilter()

    # Step 1: parsing a request
    filter_wrapper.parse_request( request )

    # Create a form, search permalink (url) and resulting queryset
    form      = filter_wrapper.filter_form()
    queryset  = filter_wrapper.filter_queryset()
    permalink = filter_wrapper.filter_url()

Example view
------------

This example shows how to create a basic user search engine::

    from django.contrib.auth import models as authmodels
    from django.shortcuts import render_to_response
    from django.template.context import RequestContext

    import jsearch

    def search(self, request):
        # Defining the wrapper as the 'engine'
        engine = jsearch.FilterWrapper(
            queryset = authmodels.objects.all(),
            url      = '/user/search/',
        )

        engine['first_name'] = jsearch.ValueFilter()
        engine['group']      = jsearch.QuerySetChoicesFilter(
            authmodels.Group.objects.all()
        )

        # Parsing input, to set values to submitted filters
        engine.parse_request(request)

        # In general, the same template should be usable all the time
        return render_to_response(
            'jsearch_template.html',
            { 'jsearch_engine': engine },
            context_instance = RequestContext( request )
        )

This template should support the above view::

    <form action="{{ jsearch_engine.url }}" method="post">
        {{ jsearch_engine.filter_form }}
        <input type="submit" />
    </form>

    <p><a href="{{ jsearch_engine.filter_url }}">Research permalink</a></p>

    <ul>
    {% for result in jsearch_engine.filter_queryset %}
        <li>{{ result }}</li>
    {% endfor %}
    </ul>

jforms
======

Overview
--------

Yet another app that allows making usable forms.

Basically, it is providing convenient widgets and adding abstraction layers to using them.

ModelChoiceWidget class
-----------------------

Extends django.forms.HiddenInput.

Critical attributes:
- either `rel` or `model`,
- `search_field`,

rel attribute
`````````````

ForeignKey or ManyToMany case::

    # Get the django.db.models.fields.related.ManyToOneRel object
    YourModel._meta.get_field('fk_field_name').rel

    # Get the django.db.models.fields.related.ManyToManyRel object
    YourModel._meta.get_field('m2m_field_name').rel

model attribute
```````````````

If `rel` is not set, then `model` should be set to the model class.

search_fields attribute
```````````````````````

A list of fields in any of the following forms:

- '^field_name': lookup with istartwith,
- '=field_name': lookup with iexact,
- '@field_name': lookup with search,
- 'field_name' : lookup with icontains.

ModelMultipleChoiceField
------------------------

Differences with ModelChoiceField:

- allows the user to select a list of models,
- extends django.forms.SelectMultiple.

Form class
----------

Extends django.forms.Form and provides an `autocomplete_factory` class method, which returns a field using a jforms.Model(Multiple)ChoiceField.

ModelForm class
---------------

- Extends django.forms.Form.
- Sets the `form` class-attribute to jforms.Form.
- Overloads the `formfield_for_dbfield` method to automatically use `jforms.autocomplete_factory` with the `jsearch_fields` class attribute.

jadmin
======

Overview
--------

It extends `django.contrib.admin` making it more useable for very large projects.

`jadmin.AdminSite` allows making a tree-ish navigation menu to replace `breadcrumbs`.

Provides a subclass of `django.contrib.admin.options.ModelAdmin`, making FK and M2M fields using jforms widget.

`jadmin.ModelAdmin` embeds `jsearch` into `changelist_view`, to provide a more usable search engine.

There is also a hack to get `django` to support field-level constraints, which is also maintained, but lets you on your own - sorry about that.

Search engine usage
-------------------

Get jQuery autocomplete for FK and M2M fields in the admin::

    import jadmin

    class FooAdmin(jadmin.ModelAdmin):
        # For the ajax autocomplete widget
        jrelation_search_fields = {
            SomeRelatedModel: 'some_related_model_field',
            OtherRelatedModel: ('foofield', 'barfield'),
        }
        # For the changelist_view jsearch engine
        jsearch_fields = ('fk_field_name', 'm2m_field_name', 'other_field')

    admin.site.register(FooModel, FooAdmin)

The `search` block of template `admin/change_list.html` should be overloaded to use the context variable `jsearch`::

    {% extends 'admin/change_list.html' %}

    {% block extrahead %}
    {{ media }}
    {{ block.super }}
    {% endblock %}

    {% block search %}
    <!-- Super the block to get the basic search field provided by django -->
    {{ block.super }}

    <form action="" method="post">
    {{ jsearch.filter_form }}
    
    <input type="submit" />
    </form>
    {% endblock %}

Navigation menu usage
---------------------

Example yourapp/sites/__init__.py, it isn't supposed to be used as-is but prooves the concept::

    # vim: set fileencoding=utf8 :
    import jadmin
    
    class AdminSite(jadmin.AdminSite):
        def get_menu_structure(self):
            return {
                u"root level 0": {
                    u"submenu 00": '/admin/foo',
                    u"submenu 01": '/admin/bar',
                },
                u"root level 1: '/admin/other',
            }

    admin = AdminSite()

    # Hack to register all installed apps ModelAdmin
    from django.contrib import admin as django_admin
    django_admin.site = admin
    # This should not be done in urls.py when dealing
    # with multiple AdminSite
    django_admin.autodiscover()

    # Register our models, we just need to load it
    import sites.admin as immo_admin_config

Example yourapp/sites/admin.py::

    # vim: set fileencoding=utf8 :
    from sites import admin as site
    import jadmin
    import models

    site.register(models.FooModel)

Examples urls.py::

    from django.conf.urls.defaults import *

    from yourproject.yourapp import sites

    urlpatterns = patterns('',
        r'^admin/', include(sites.admin.urls)),
    )

Versions
~~~~~~~~

0_alpha0: custom search engine, custom relations widgets.
0_alpha1: replace breadcrumbs with a tree-ish jquery (overridable) navigation.
0_alpha2: "public" site, not allowing changes, not requiring request.user.is_staff.
0_alpha3: jhtml tabular layout renderer for public site change_view.
0_beta0: works for me.
