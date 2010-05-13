# Create your views here.

import whelf.settings as settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers


def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def web(request):
    if settings.DEBUG:
        print 'iDisplayStart: %s' % request.POST.get('iDisplayStart','')
        print 'iDisplayLength: %s' % request.POST.get('iDisplayLength','')
        print 'sSearch: %s' % request.POST.get('sSearch','')
        print 'bEscapeRegex: %s' % request.POST.get('bEscapeRegex','')
        print 'iColumns: %s' % request.POST.get('iColumns','')
        print 'iSortingCols: %s' % request.POST.get('iSortingCols','')
        print 'sEcho: %s' % request.POST.get('sEcho','')
    json = simplejson.dumps({
        'sEcho': request.POST.get('sEcho','1'),
        'iTotalRecords': 100,
        'iTotalDisplayRecords': 100,
        'aaData': [['mark','m']] * 100})
    return HttpResponse(json, mimetype='application/json')


def irc(request):
    if settings.DEBUG:
        print 'DEBUG POST: %s' % request.POST
