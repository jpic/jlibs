from django.conf.urls.defaults import *

# Add this to your urls.urlpatterns
# (r'^jforms/', include('jforms.urls')),

urlpatterns = patterns('',
    (r'^search/', 'jforms.views.search'),
)
