import os
import sys
sys.path.append('/home/dmitry/b/whelf')
sys.path.append('/home/dmitry/b')
sys.path.append('/home/dmitry/b/pywikipedia')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
print "*************** STARTING AN INSTANCE ****************"
print sys.path
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
