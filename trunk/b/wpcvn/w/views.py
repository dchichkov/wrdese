# Create your views here.

import wpcvn.settings as settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers

import secret
from aes_encryption import EncodeAES, DecodeAES

import marshal, re
from ordereddict import OrderedDict
from collections import defaultdict
from operator import itemgetter
from time import time
from pprint import pprint
import sys



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
    return HttpResponse(simplejson.dumps({'ip' : request.META['REMOTE_ADDR']}), 
                        mimetype='application/json')


def wid(request):
    guid = request.POST.get('guid','')
    wid = __guids.setdefault(guid, {'wid':''})
    wid['utc'] = time()
    print wid
    return HttpResponse(simplejson.dumps(wid), 
                        mimetype='application/json')



def users(request):
    data = [ [p['nick'], p['utc']] 
            for p in __users.values()]
    
    json = simplejson.dumps({
        'sEcho': request.GET.get('sEcho','1'),
        'iTotalRecords': len(data),
        'iTotalDisplayRecords': len(data),
        'aaData': data})
    return HttpResponse(json, mimetype='application/json')


# default responce - prencode ajax / cash ajax for later use
def w(request):
    if settings.DEBUG:
        print 'iDisplayStart: %s' % request.POST.get('iDisplayStart','')
        print 'iDisplayLength: %s' % request.POST.get('iDisplayLength','')
        print 'sSearch: %s' % request.POST.get('sSearch','')
        print 'bEscapeRegex: %s' % request.POST.get('bEscapeRegex','')
        print 'iColumns: %s' % request.POST.get('iColumns','')
        print 'iSortingCols: %s' % request.POST.get('iSortingCols','')
        print 'iSortCol_0: %s' % request.POST.get('iSortCol_0','')
        print 'sSortDir_0: %s' % request.POST.get('sSortDir_0','')
        print 'sEcho: %s' % request.POST.get('sEcho','')
        print 'nick: %s' % request.POST.get('nick','')
        print 'wid: %s' % request.POST.get('wid','')
        sys.stdout.flush()

    # Authentication: use wid if available, use nick if available
    user = None
    wid = request.POST.get('wid','')
    nick = request.POST.get('nick','')
    sSearch = request.POST.get('sSearch','')
    iSortingCols = request.POST.get('iSortingCols', '')
    iSortCol = int(request.POST.get('iSortCol_0', '0'))
    bSortDir = (request.POST.get('sSortDir_0', 'asc') == 'desc')
    start = int(request.POST.get('iDisplayStart',''))
    length = int(request.POST.get('iDisplayLength',''))
    
    
    if wid and wid in __users:
        user = __users[wid]
    elif wid and DecodeAES(secret.cipher, wid):
        user = __users.setdefault(wid, {'nick' : DecodeAES(secret.cipher, wid), 'confirmed' : True})
    elif nick:
        user = __users.setdefault(nick, {'nick' : nick, 'confirmed' : False})
        
    if(user): user['utc'] = time()               

    
    # Fill data, apply search and sorting parameters
    if sSearch:
        data = [ [p['utc'], p['reputation'], p['views'], p['url'], p['user'], p['page'], p['summary'] ] 
                for p in __recent.values() if p['user'].startswith(sSearch) or p['page'].startswith(sSearch)]
    else:
        data = [ [p['utc'], p['reputation'], p['views'], p['url'], p['user'], p['page'], p['summary'] ] 
                for p in __recent.values()]
        
    if iSortingCols == '1':
        data.sort(key = itemgetter(iSortCol), reverse = bSortDir)

    json = simplejson.dumps({
        'sEcho': request.POST.get('sEcho','1'),
        'iTotalRecords': len(__recent),
        'iTotalDisplayRecords': len(data),
        'aaData': data[start:start+length]})
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

    if d['summary'] in __guids:
        guid = d['summary']
        print "Wow. We have a match. User:", d['user'], "Reputation:", reputation
        __guids[guid]['reputation'] = reputation
        __guids[guid]['nick'] = d['user']
        if(reputation and reputation > 2):
            __guids[guid]['wid'] = EncodeAES(secret.cipher, d['user'])
 
    if(reputation == None):
        return HttpResponse()       # TODO
    
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
    
    for p, r in __recent.iteritems():
        if(r['expire'] < utc):
            del __recent[p]
    sys.stdout.flush()
    return HttpResponse()




# "/home/dmitry/b/p/filtered.reputations-enwiki-20100130.none.full"
if settings.DEBUG:
    __user_reputations = read_reputations("/home/dmitry/b/p/ratings-pan-wvc-10.merged")
else:
    __user_reputations = read_reputations("/home/dmitry/b/p/reputations-enwiki-20100130.none.full.merged")
    
__users = OrderedDict()
__recent = OrderedDict()
__guids = {}


re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

