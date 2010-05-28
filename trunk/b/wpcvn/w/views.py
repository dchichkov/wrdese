# Create your views here.
import wpcvn.settings as settings
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers

import secret
from aes_encryption import EncodeAES, DecodeAES
from reputations import read_reputations

import marshal, re
from ordereddict import OrderedDict
from operator import itemgetter
from time import time
from pprint import pprint
import sys


# Settings
MAX_LABEL_LENGTH = 14
MAX_NICK_LENGTH = 16
MAX_WID_LENGTH = 256
MAX_GUID_LENGTH = 48

MAX_USERS = 100
MAX_RECENT = 1000

# Globals
class SharedState:
    """Beware of threads"""
    expiration_check = 0
    users = OrderedDict()
    filtered = OrderedDict()
    recent = OrderedDict()
    guids = {}
    re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))
    if settings.DEBUG:
        user_reputations = read_reputations("/home/dmitry/b/p/ratings-pan-wvc-10.merged")
    else:
        user_reputations = read_reputations("/home/dmitry/b/p/reputations-enwiki-20100130.none.full.merged")

S = SharedState()


# AJAX WEB sub-requests

def user_from_wid_nick(request):
    """Extract wid and nick from the request"""

    print 'nick: %s' % request.POST.get('nick','')
    print 'wid: %s' % request.POST.get('wid','')
    sys.stdout.flush()

    user = None
    wid = request.POST.get('wid','')[:MAX_WID_LENGTH]
    nick = request.POST.get('nick','')[:MAX_NICK_LENGTH]

    if wid and wid in S.users:
        user = S.users[wid]
    elif wid and DecodeAES(secret.cipher, wid):
        user = S.users.setdefault(wid, {'nick' : DecodeAES(secret.cipher, wid), 'confirmed' : True})
    elif nick:
        user = S.users.setdefault(nick, {'nick' : nick, 'confirmed' : False})

    if(user): user['utc'] = time(); user['expire'] = time() + 60 * 5

    return user


# AJAX WEB requests

def click(request):
    """Nick viewing the page (patrolling)"""    
    user = user_from_wid_nick(request)
    page = request.POST.get('page','')
    print "Clicked Page: %s" % page
    if page in S.filtered:
        if(user and user['confirmed']): S.filtered[page]['patrolled'] += "<u>" + user['nick'] + "</u>" + "<br>"
        elif(user and not user['confirmed']): S.filtered[page]['patrolled'] += user['nick'] + "<br>"
        else: S.filtered[page]['patrolled'] += "Anonymous<br>"
        S.filtered[page]['expire'] = time() + 60 * 15       # 15 minutes       
    return HttpResponse()


def ip(request):
    return HttpResponse(simplejson.dumps({'ip' : request.META['REMOTE_ADDR']}), 
                        mimetype='application/json')

def karma(request):
    username = request.GET.get('username','')
    reputation = S.user_reputations.get(username)
    return HttpResponse(simplejson.dumps({'username' : username, 'karma' : reputation}),
                        mimetype='application/json')


def wid(request):
    guid = request.POST.get('guid','')[:MAX_GUID_LENGTH]
    wid = S.guids.setdefault(guid, {'wid':''})
    wid['expire'] = time() + 60
    return HttpResponse(simplejson.dumps(wid), 
                        mimetype='application/json')



def users(request):
    data = [ [p['nick'], p['utc'], p['confirmed']] 
            for p in S.users.values()]
    
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
        sys.stdout.flush()

    # Authentication: use wid if available, use nick if available
    sSearch = request.POST.get('sSearch','')
    iSortingCols = request.POST.get('iSortingCols', '')
    iSortCol = int(request.POST.get('iSortCol_0', '0'))
    bSortDir = (request.POST.get('sSortDir_0', 'asc') == 'desc')
    start = int(request.POST.get('iDisplayStart',''))
    length = int(request.POST.get('iDisplayLength',''))
    
    user = user_from_wid_nick(request)
    
    # Fill data, apply search and sorting parameters
    if sSearch:
        data = [ [p['utc'], p['patrolled'], p['labels'], p['url'], p['user'], p['reputation'], p['page'], p['summary'] ] 
                for p in S.filtered.values() if p['user'].startswith(sSearch) or p['page'].startswith(sSearch)]
    else:
        data = [ [p['utc'], p['patrolled'], p['labels'], p['url'], p['user'], p['reputation'], p['page'], p['summary'] ] 
                for p in reversed(S.filtered.values())]
        
    if iSortingCols == '1':
        data.sort(key = itemgetter(iSortCol), reverse = bSortDir)

    json = simplejson.dumps({
        'sEcho': request.POST.get('sEcho','1'),
        'iTotalRecords': len(S.filtered),
        'iTotalDisplayRecords': len(data),
        'aaData': data[start:start+length]})
    return HttpResponse(json, mimetype='application/json')


def irc(request):
    expiration_check();

    match = S.re_edit.match(request.raw_post_data)

    if not match:
            print "Warning: Regexp does not match (raw): ", request.raw_post_data
            return HttpResponse()
    try:
        msg = unicode(request.raw_post_data,'utf-8')
    except UnicodeDecodeError:
        print "Exception: UnicodeDecodeError"
        return HttpResponse()

    match = S.re_edit.match(msg)
    if not match:
        print "Warning: Regexp does not match (unicode)"
        return HttpResponse()
    
    d = match.groupdict()
    reputation = S.user_reputations.get(d['user'])

    # Autoconfirmation stuff
    if d['summary'] in S.guids:
        guid = d['summary']
        print "Wow. We have a match. User:", d['user'], "Reputation:", reputation
        S.guids[guid]['reputation'] = reputation
        S.guids[guid]['nick'] = d['user']
        if(reputation and reputation > 50):
            S.guids[guid]['wid'] = EncodeAES(secret.cipher, d['user'])
 
    if(d['user'] in ['SineBot', ]):
        return HttpResponse()       # TODO
    
    if(reputation == None):         # HACK
        reputation = 0.0

    page = d['page']
    utc = time()
    d['reputation'] = reputation
    d['utc'] = utc
    d['expire'] = utc + 15 * 60   # 15 minutes
    d['patrolled'] = ""
    d['labels'] = ""
    S.recent[page] = d

    if(reputation < 0):
        d['expire'] = utc + 60 * 60   # 1 hour
        S.filtered[page] = d
    elif(page in S.filtered):
        if(d['reputation'] > S.filtered[page]['reputation']):
            d['labels'] = "WPCVN: likely patrolled<br>"
        S.filtered[page] = d
    
    return HttpResponse()

def labels(request):
    if settings.DEBUG:
        print 'page: %s' % request.POST.get('page','')
        print 'user: %s' % request.POST.get('user','')
        print 'label: %s' % request.POST.get('label','')

    page = request.POST.get('page','')
    if page in S.recent:
        d = S.recent[page]
        if d['user'] == request.POST.get('user',''):
            d['expire'] = time() + 60 * 60   # 1 hour
            d['labels'] += 'MiszaBot: ' + request.POST.get('label','')[:MAX_LABEL_LENGTH] + '<br>'
            S.filtered[page] = d
            print "Success: ", "Page = ", page, "User = ", d['user'], "Labels: ", d['labels']  
        else:
            print "Warning mismatching user name: ", "Page = ", page, "User = ", d['user']
    else:
        print "Warning page is not recent: ", "Page = ", page
                               
    
    sys.stdout.flush()
    return HttpResponse()


# check records expiration every 30 seconds
def expiration_check():
    if(time() < S.expiration_check): return
    S.expiration_check = time() + 60
     
    utc = time()   
    for t in [S.users, S.filtered, S.recent, S.guids]:
       for p, r in t.iteritems(): 
           if(r['expire'] < utc): del t[p]

