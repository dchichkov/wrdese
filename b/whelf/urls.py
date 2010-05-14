from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^w$', 'w.views.web'),
    (r'^i$', 'w.views.irc'),
    (r'^c$', 'w.views.click'),

    (r'^m/(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': './media'}),
    (r'^(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': './media'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
)
