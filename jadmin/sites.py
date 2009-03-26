# vim: set fileencoding=utf8 :
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote
from django.contrib import admin
from jadmin import menus

class AdminSite(admin.AdminSite):
    class Media:
        js = (
            'jquery.min.js',
            'jmenu/jquerycssmenu.js',
        )

    def get_menu(self):
        menu = menus.Menu()
        f = menus.MenuFactories(self.get_menu_structure())
        return f.menu

    def __init__(self, *args, **kwargs):
        super(AdminSite, self).__init__(*args, **kwargs)
        self.info = (self.name,)

    def get_model_info(self, model):
        return self.info + (model._meta.app_label, model._meta.module_name,)

    def get_changelist_urlname(self, model):
        name = '%sadmin_%s_%s_changelist' % self.get_model_info(model)
        return name

    def get_add_urlname(self, model):
        name = '%sadmin_%s_%s_add' % self.get_model_info(model)
        return name

    def get_history_urlname(self, model):
        name = '%sadmin_%s_%s_history' % self.get_model_info(model)
        return name

    def get_delete_urlname(self, model):
        name = '%sadmin_%s_%s_delete' % self.get_model_info(model)
        return name

    def get_change_urlname(self, model):
        name = '%sadmin_%s_%s_change' % self.get_model_info(model)
        return name

    def index(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context['jmenu'] = self.get_menu()
        print self.get_menu().render()
        return super(AdminSite, self).index(request, extra_context)

admin.site = AdminSite()
