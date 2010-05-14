#! /usr/bin/env python
# Dmitry Chichkov <dchichkov@gmail.com>

import irclib, httplib
import sys, re, cPickle
from time import time, sleep


def on_connect(connection, event):
    print "Welcomed on irc.wikimedia.org"
    if irclib.is_channel("#en.wikipedia"):
        connection.join("#en.wikipedia")
    else:
        print "Error: #en.wikipedia is not a channel. "
        sys.exit(0)

def on_join(connection, event):
    print ("Joined:", event.arguments() [ 0 ])

# Private messages
def on_priv_message ( connection, e ):
    print e.source().split ( '!' ) [ 0 ] + ': ' + e.arguments() [ 0 ]
    sys.stdout.flush();
     

# Public messages
def on_pub_message ( connection, e ):
    # print e.source().split ( '!' ) [ 0 ] + ': ' + e.arguments()[0]
    # sys.stdout.flush();
    cPickle.dump(e.arguments()[0], FILE)
    c.request('PUT', '/i', e.arguments()[0], {'CONTENT-TYPE' : 'octet/stream'})
    print c.getresponse()
    

def on_disconnect(connection, event):
    print "Error: received on_disconnect"
    sys.exit(0)



if __name__ == "__main__":
    # test mode
    if len(sys.argv) == 2:        
        try:
            c = httplib.HTTPConnection('localhost:8080')
            FILE = open(sys.argv[1], 'rb')            
            while True:
                print cPickle.load(FILE)
                c.request('PUT', '/i', cPickle.load(FILE), {'CONTENT-TYPE' : 'octet/stream'})
                c.getresponse().read()
                sleep(0.1)
                #raw_input(c.getresponse().read())
        except EOFError, e: pass            
        sys.exit(0)

        
    # irclib.DEBUG = True
    nickname = "Dc987devel"
    
    irc = irclib.IRC(); 
    irc.add_global_handler("welcome", on_connect)
    irc.add_global_handler('privmsg', on_priv_message )
    irc.add_global_handler('pubmsg', on_pub_message )
    irc.add_global_handler("disconnect", on_disconnect)
    
    c = None; w = None;
    try:
        w = irc.server().connect("irc.wikimedia.org", 6667, nickname)
        c = httplib.HTTPConnection('localhost:8080')
        FILE = open('irc.en.wikipedia.%s.pkl' % time(), 'wb')
        
    except irclib.ServerConnectionError, x:
        print x
        sys.exit(1)
    
    except Exception, e:
        print e
        sys.exit(1)
    
    
    try:
        irc.process_forever()
        
    except KeyboardInterrupt:
        if w: w.quit("Ctrl-C at console")
        if c: c.close()
        print "Quit IRC."
    
    except Exception, e:
        if w: w.quit("Exception")
        if c: c.close()
        print("%s: %s" % (e.__class__.__name__, e.args))
        raise 
     
    
