# Create your views here.

import whelf.settings as settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers


import r
from ordereddict import OrderedDict
from time import time

#r._reputations_arg = "/home/dmitry/b/p/ratings-pan-wvc-10.merged"
r._reputations_arg = "/home/dmitry/b/p/filtered.reputations-enwiki-20100130.none.full"
r._output_arg = None
user_reputations = r.read_reputations()
__recent = OrderedDict()
__utc = time()


import re
from pprint import pprint
re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

print __utc



def click(request):
    page = request.raw_post_data
    if page in __recent:
        __recent[page]['views'] += 1
    return HttpResponse()

def web(request):
    if False and settings.DEBUG:
        print 'iDisplayStart: %s' % request.POST.get('iDisplayStart','')
        print 'iDisplayLength: %s' % request.POST.get('iDisplayLength','')
        print 'sSearch: %s' % request.POST.get('sSearch','')
        print 'bEscapeRegex: %s' % request.POST.get('bEscapeRegex','')
        print 'iColumns: %s' % request.POST.get('iColumns','')
        print 'iSortingCols: %s' % request.POST.get('iSortingCols','')
        print 'sEcho: %s' % request.POST.get('sEcho','')
    
    data = [ [p['utc'], p['reputation'], p['views'], p['url'], p['user'], p['page'], p['summary'] ] for p in __recent.values()]
    # print data
    
    json = simplejson.dumps({
        'sEcho': request.POST.get('sEcho','1'),
        'iTotalRecords': len(data),
        'iTotalDisplayRecords': len(data),
        'aaData': data})
    return HttpResponse(json, mimetype='application/json')


def irc(request):
    match = re_edit.match(request.raw_post_data)

    if not match:
            print "Warning: Regexp does not match (raw): ", request.raw_post_data
            return HttpResponse()
    try:
        msg = unicode(request.raw_post_data,'utf-8')
    except UnicodeDecodeError:
        print "Exception: UnicodeDecodeError"
        return HttpResponse()

    match = re_edit.match(msg)
    if not match:
        print "Warning: Regexp does not match (unicode)"
        return HttpResponse()
    
    
    d = match.groupdict()
    reputation = user_reputations.get(d['user'])
    if(reputation == None):     # TODO
        return HttpResponse()
    
    
    page = d['page']
    __utc = time()
    if(reputation < 1):
        d['reputation'] = reputation
        d['utc'] = __utc
        d['expire'] = __utc + 1000
        d['views'] = 0
        __recent[page] = d
    elif(page in __recent):
        d['reputation'] = reputation
        d['utc'] = __utc
        d['expire'] = __utc + 60
        d['views'] = 0
        __recent[page] = d
    
    # print(page, reputation)
    # pprint(__recent)

    for p, r in __recent.iteritems():
        if(r['expire'] < __utc):
            del __recent[p]
    
    return HttpResponse()

