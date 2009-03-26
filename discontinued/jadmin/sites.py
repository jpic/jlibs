from django.contrib import admin
import jadmin

class AdminSite(admin.AdminSite):    
    def register(self, model_or_iterable, admin_class=None, **options):
        if not admin_class:
            admin_class = jadmin.ModelAdmin

        super(AdminSite, self).register(model_or_iterable, admin_class, **options)
    def get_public_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = patterns('')
        # Add in each model's views.
        for model, model_admin in self._registry.iteritems():
            if isinstance(model_admin, jadmin.ModelAdmin):
                urlpatterns += patterns('',
                    url(r'^%s/%s/' % (model._meta.app_label, model._meta.module_name),
                     include(model_admin.public_urls))
                )
        return urlpatterns
    
    def public_urls(self):
        return self.get_public_urls()
    public_urls = property(public_urls)
        
admin.site = AdminSite()
