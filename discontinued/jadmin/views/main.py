from django.contrib.admin.views import main as admin
from django.core.urlresolvers import reverse
from django.contrib.admin.util import quote

class PublicList(admin.ChangeList):
    def url_for_result(self, result):
        name = '%spublic_%s_%s_details' % (
            self.model_admin.public_site_name,
            self.opts.app_label,
            self.opts.module_name
        )

        url = reverse(name, args=[quote(getattr(result, self.pk_attname))])
        return url
