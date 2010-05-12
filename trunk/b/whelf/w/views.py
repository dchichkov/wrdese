# Create your views here.

from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers


def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def ajax_table(request):
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
        'iTotalRecords': 2,
        'iTotalDisplayRecords': 2,
        'aaData': [['mark','m'],['nicki','f']]})
    return HttpResponse(json, mimetype='application/json')

