from django.contrib import admin

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

admin.site = AdminSite()
