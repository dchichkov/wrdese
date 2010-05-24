from django.conf.urls.defaults import *

import os,sys

if 'APACHE_PID_FILE' in os.environ:
    URL_PREFIX = r'^'
else:
    URL_PREFIX = r'^s/'


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # IRC/Apache:
    (URL_PREFIX + r'i$', 'w.views.irc'),    
                       
    # Web/Apache:
    (URL_PREFIX + r'w$', 'w.views.w'),
    (URL_PREFIX + r'users$', 'w.views.users'),
    (URL_PREFIX + r'b$', 'w.views.bots'),
    (URL_PREFIX + r'c$', 'w.views.click'),
    (URL_PREFIX + r'ip$', 'w.views.ip'),
    (URL_PREFIX + r'wid$', 'w.views.wid'),
    
    

    (r'^m/(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': './media'}),
    (r'^(?P<path>index.html)$', 'django.views.static.serve',
       {'document_root': './media'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
)
