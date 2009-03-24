from django.contrib import admin

class AdminSite(admin.AdminSite):
    pass

admin.site = AdminSite()
