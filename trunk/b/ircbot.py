#! /usr/bin/env python
# Dmitry Chichkov <dchichkov@gmail.com>

import irclib
import sys, re, cPickle
from time import time
import r

from pprint import pprint
from ordereddict import OrderedDict
from time import time


def on_connect(connection, event):
    if connection == w:
        print "Welcomed on irc.wikimedia.org"
        if irclib.is_channel("#en.wikipedia"):
            connection.join("#en.wikipedia")
        else:
            print "Error: #en.wikipedia is not a channel. "
            sys.exit(0)
            
    if connection == c:            
        print "Welcomed on irc.freenode.net"
        connection.join("#cvn-wp-en-reputation")        
    
def on_join(connection, event):
    print ("Joined:", event.arguments() [ 0 ])

# Private messages
def on_priv_message ( connection, e ):
    print e.source().split ( '!' ) [ 0 ] + ': ' + e.arguments() [ 0 ]
    sys.stdout.flush();
    try:
        msg = unicode(e.arguments()[0],'utf-8')
    except UnicodeDecodeError:
        connection.privmsg ( e.source().split ( '!' ) [ 0 ], 'Exception: UnicodeDecodeError.' )
        print "Exception: UnicodeDecodeError"
        return

    reputation = user_reputations.get(msg)
    if(reputation == None): reputation = "User not found. (If user was created before 2010 please report this as a bug.)"
    connection.privmsg ( e.source().split ( '!' ) [ 0 ], "User %s reputation: %s" % (msg, reputation) )
    return
     

# Public messages
def on_pub_message ( connection, e ):
    if connection == c:
        print e.source().split ( '!' ) [ 0 ] + ': ' + e.arguments()[0]
        sys.stdout.flush();
        return    
    
    cPickle.dump(e.arguments()[0], FILE)   
    match = re_edit.match(e.arguments()[0])

    if not match:
            # print "Warning: Regexp does not match (raw): ", e.arguments()[0]
            return
    try:
        msg = unicode(e.arguments()[0],'utf-8')
    except UnicodeDecodeError:
        print "Exception: UnicodeDecodeError"
        return

    match = re_edit.match(msg)
    if not match:
        print "Warning: Regexp does not match (unicode)"
        return
    

    d = match.groupdict()
    reputation = user_reputations.get(d['user'])

    if(reputation == None):     # TODO
        return

    page = d['page']
    __utc = time()

    if(reputation < 10):
        d['reputation'] = reputation
        d['utc'] = __utc
        d['expire'] = __utc + 60*60
        __recent[page] = d
    elif(page in __recent):
        d['reputation'] = reputation
        d['utc'] = __utc
        d['expire'] = __utc + 60
        __recent[page] = d
    
    print(page, reputation)
    pprint(__recent)


    for p, r in __recent.iteritems():
        if(r['expire'] < __utc):
            del p
    pprint(__recent)

    if(c and reputation < 2):
        # print d['user'], '(', reputation , ')', d['page'], d['url']
        c.privmsg("#cvn-wp-en-reputation", ("Reputation: %s. " % reputation)  +  e.arguments()[0])
    return

def on_disconnect(connection, event):
    print "Error: received on_disconnect"
    sys.exit(0)


if len(sys.argv) < 3:
    print "Usage: testbot <nickname> reputations.pkl"
    sys.exit(1)

nickname = sys.argv[1]
r._reputations_arg = sys.argv[2]
r._output_arg = None
user_reputations = r.read_reputations()
re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))
FILE = open('irc.en.wikipedia.%s.pkl' % time(), 'wb')
__recent = OrderedDict()
__utc = time()




# irclib.DEBUG = True
irc = irclib.IRC(); c = None; w = None;
try:
    # c = irc.server().connect("irc.freenode.net", 6667, nickname)
    w = irc.server().connect("irc.wikimedia.org", 6667, nickname)
    
except irclib.ServerConnectionError, x:
    print x
    sys.exit(1)

irc.add_global_handler("welcome", on_connect)
irc.add_global_handler('privmsg', on_priv_message )
irc.add_global_handler('pubmsg', on_pub_message )
irc.add_global_handler("disconnect", on_disconnect)

try:
    irc.process_forever()
    
except KeyboardInterrupt:
    if c: c.quit("Ctrl-C at console")
    if w: w.quit("Ctrl-C at console")
    print "Quit IRC."

except Exception, e:
    if c: c.quit("Exception")
    if w: w.quit("Exception")
    print("%s: %s" % (e.__class__.__name__, e.args))
    raise 
 
