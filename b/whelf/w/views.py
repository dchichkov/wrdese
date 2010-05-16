# Create your views here.

import whelf.settings as settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers

import marshal, re
from ordereddict import OrderedDict
from collections import defaultdict
from time import time
from pprint import pprint


def read_reputations(_reputations_arg):
    print("Reading %s..." % _reputations_arg)
    FILE = open(_reputations_arg, 'rb')
    user_reputations = defaultdict(int)
    start = time()
    try:
        while True:
            (u,r) = marshal.load(FILE)
            user_reputations[u] += r
    except IOError, e:
        raise
    except EOFError, e:
        print("Done reading %s. Read time: %f. Total users: %d" % (_reputations_arg, time() - start, len(user_reputations)))
    return user_reputations



def click(request):
    page = request.raw_post_data
    if page in __recent:
        __recent[page]['views'] += 1
    return HttpResponse()


def ip(request):
    return HttpResponse({'ip' : request.META['REMOTE_ADDR'], 'host' : request.META['REMOTE_HOST']} )


def web(request):
    if settings.DEBUG:
        print 'iDisplayStart: %s' % request.POST.get('iDisplayStart','')
        print 'iDisplayLength: %s' % request.POST.get('iDisplayLength','')
        print 'sSearch: %s' % request.POST.get('sSearch','')
        print 'bEscapeRegex: %s' % request.POST.get('bEscapeRegex','')
        print 'iColumns: %s' % request.POST.get('iColumns','')
        print 'iSortingCols: %s' % request.POST.get('iSortingCols','')
        print 'sEcho: %s' % request.POST.get('sEcho','')
    
    data = [ [p['utc'], p['reputation'], p['views'], p['url'], p['user'], p['page'], p['summary'] ] 
            for p in __recent.values()]

    start = int(request.POST.get('iDisplayStart',''))
    length = int(request.POST.get('iDisplayLength',''))
    
    json = simplejson.dumps({
        'sEcho': request.POST.get('sEcho','1'),
        'iTotalRecords': len(data),
        'iTotalDisplayRecords': len(data),
        'aaData': data[start:length]})
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
    reputation = __user_reputations.get(d['user'])
    if(reputation == None):     # TODO
        return HttpResponse()
    
    
    page = d['page']
    utc = time()
    if(reputation < 10):
        d['reputation'] = reputation
        d['utc'] = utc
        d['expire'] = utc + 1000
        d['views'] = 0
        __recent[page] = d
    elif(page in __recent):
        d['reputation'] = reputation
        d['utc'] = utc
        d['expire'] = utc + 60
        d['views'] = 0
        __recent[page] = d
    
    # print(page, reputation)
    # pprint(__recent)

    for p, r in __recent.iteritems():
        if(r['expire'] < utc):
            del __recent[p]
    
    return HttpResponse()




# "/home/dmitry/b/p/filtered.reputations-enwiki-20100130.none.full"
__user_reputations = read_reputations("/home/dmitry/b/p/ratings-pan-wvc-10.merged")
__recent = OrderedDict()

re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

