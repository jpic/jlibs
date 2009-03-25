from django.contrib import admin
from jadmin import menus

class AdminSite(admin.AdminSite):
    class Media:
        css = {
            'all': (
                'style.css',
            ),
        }
        js = (
            'jquery.min.js',
            'jmenu/jquerycssmenu.js',
        )

    def get_menu(self):
        menu = menus.Menu()
        f = menus.MenuFactories(self.get_menu_structure())
        return f.menu

admin.site = AdminSite()
