#! /usr/bin/env python
#
# Example program using irclib.py.
#
# This program is free without restrictions; do anything you like with
# it.
#
# Joel Rosdahl <joel@rosdahl.net>

import irclib
import sys, re
import r


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
    # Respond to a 'hello' message
    if e.arguments() [ 0 ].lower().find ( 'hello' ) == 0:
        connection.privmsg ( e.source().split ( '!' ) [ 0 ], 'Hello.' )
    else:
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
        print e.target() + '> ' + e.source().split ( '!' )[ 0 ] + ': ' + e.arguments() [ 0 ]
        return    
    
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
    if(reputation != None and reputation < 0):
        # print d['user'], '(', reputation , ')', d['page'], d['url']
        c.privmsg("#cvn-wp-en-reputation", ("Reputation %s. " % reputation)  +  e.arguments()[0])
    return

def on_disconnect(connection, event):
    print "Error: received on_disconnect"
    sys.exit(0)


if len(sys.argv) != 3:
    print "Usage: testbot <nickname> reputations.pkl"
    sys.exit(1)

nickname = sys.argv[1]
r._reputations_arg = sys.argv[2]
r._output_arg = None
user_reputations = r.read_reputations()
re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

# irclib.DEBUG = True
irc = irclib.IRC()
try:
    c = irc.server().connect("irc.freenode.net", 6667, nickname)
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
    c.quit("Ctrl-C at console")
    w.quit("Ctrl-C at console")
    print "Quit IRC."

except Exception, e:
    c.quit("Exception")
    w.quit("Exception")
    print("%s: %s" % (e.__class__.__name__, e.args))
    raise 
 
