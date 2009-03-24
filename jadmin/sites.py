from django.contrib import admin

class AdminSite(admin.AdminSite):
    #def index(self, request, extra_context=None):
    #    return super(Admin2, self).index(request, {'foo': '*bar*'})
    pass
admin.site = AdminSite()
