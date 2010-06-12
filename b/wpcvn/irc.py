#! /usr/bin/env python
#
# Example program using ircbot.py.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  


"""

import sys, re, httplib, urllib, cPickle, simplejson
from django.core import serializers
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from time import time, sleep


class Irc2Http(SingleServerIRCBot):
    def __init__(self, channel, nickname, ircServer, ircPort=6667, httpConnection=None):
        SingleServerIRCBot.__init__(self, [(ircServer, ircPort)], nickname, nickname)
        self.channel = channel
        self.httpConnection = httpConnection
        # self.re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

        r_bits = r'(^C(^B)?(?P<flags>\S+?)(^C|^B)? )'
        r_user = r'(\[\[User:(?P<user>.+?)\]\],? )'
        r_label = r'((^C|^B)(?P<label>.+?)(^C|^B) )'
        r_page = r'(\[\[(?P<page>.+?)\]\] )'
        r_bytes = r'((^B^C)?\((?P<bytes>[+-]?\d+?)\)(^B)?(^C)? )'
        r_diff = r'(^CDiff:^C (?P<url>\S+) )'
        r_summary = r'("(?P<summary>.*)"?)'       
        rs = r_bits + '?' + r_user + r_label + r_page + r_bytes + '?' + r_diff + '?' + '(reason )?' + '(^C)?' + r_summary
        self.re_edit = re.compile(rs.replace('^B', '\002').replace('^C', '\003\d\d').replace('^U', '\037'))
        # cPickle.dump(rs, open('test.pkl', 'wb'))

        self.re_list = re.compile(r'Added (?P<user>.+?) to (?P<list>\S+), ("(?P<summary>.*)")\. Expires (?P<utc>.* UTC)')

        # use file as a source and fake IRC
        self.FILE = None
        while channel == '':
            try:
                FAKE = open(ircServer, 'rb')
                while True:
                    (t, e) = cPickle.load(FAKE)
                    self.on_pubmsg(None, e)
                    sleep(0.2)
            except EOFError, e:
                FAKE.close()
                return
            except Exception, e:
                print("Exception at %s: %s" % (e.__class__.__name__, e.args))
                FAKE.close()
                return


        # real irc
        # self.FILE = open('%s.%s.pkl' % (ircServer, time()), 'wb')    

        try:
            self.start()
        except KeyboardInterrupt:
            self.connection.quit("Ctrl-C at console")
            if self.FILE: self.FILE.close()
            print "Quit IRC."
        except Exception, e:
            self.connection.quit("Unhandled Exception")
            if self.FILE: self.FILE.close();
            print("Exception at %s: %s" % (e.__class__.__name__, e.args))        
            raise 


    def on_nicknameinuse(self, c, e):
        print("on_nicknameinuse")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("on_welcome", c, e)
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        if self.FILE: cPickle.dump((time(), e), self.FILE)        
        
        match = self.re_edit.match(e.arguments()[0])
        if(e.source().split ('!') [0] != 'MiszaBot'):
            return

        if not match:
                for re in [self.re_list, ]:
                    if re.match(e.arguments()[0]): return                
                print "\n\n\nWarning: Regexp does not match (raw): "
                print e.source().split ( '!' ) [ 0 ], 'len = ', len(e.arguments()[0]) 
                cPickle.dump(e.arguments()[0], sys.stdout)
                return
        try:
            msg = unicode(e.arguments()[0],'utf-8')
        except UnicodeDecodeError:
            print "\n\n\nException: UnicodeDecodeError"
            print e.source().split ( '!' ) [ 0 ], 'len = ', len(e.arguments()[0])
            return

        match = self.re_edit.match(msg)
        if not match:
            print "\n\n\nWarning: Regexp does not match (unicode)"
            print e.source().split ( '!' ) [ 0 ], 'len = ', len(e.arguments()[0])
            return
        
        # print "\n\n\n************* Regexp match."
        # print e.source().split ( '!' ) [ 0 ], 'len = ', len(e.arguments()[0])
        # cPickle.dump(e.arguments()[0], sys.stdout)
        d = match.groupdict()

        if not len(d):
            print "\n\n\nWarning: Empty match"
            print e.source().split ( '!' ) [ 0 ], 'len = ', len(e.arguments()[0])
            return


        # forward it to HTTP
        if(self.httpConnection):
            try:
                # params = simplejson.dumps(d)
                # headers = {"Content-type": "application/json", "Content-length":str(len(jsonString)) }
                params = urllib.urlencode( dict([(k, v.encode('utf-8')) for k, v in d.iteritems() if v]) )                
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"} #  charset=UTF-8                
                # params = serializers.serialize("xml", d)
                # headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                self.httpConnection.request('POST', '/s/l', params, headers)
                self.httpConnection.getresponse()
            except Exception, e:
                try:
                    print e
                    print "Warning: httpConnection disconnect/connect."
                    self.httpConnection.close()
                    self.httpConnection.connect()
                except KeyboardInterrupt:
                    raise
                except:
                    print "Warning: Exception during httpConnection disconnect/connect."
                    pass
        return


def main():
    if len(sys.argv) == 3:
        channel = nickname = ""
    elif len(sys.argv) == 5 and sys.argv[2][0] == '#':
        channel = sys.argv[2]
        nickname = sys.argv[3]
    else:
        print r"Usage: irc.py <IRC ircServer[:ircPort] <channel> <nickname> <httpServer[:httpPort]>"
        print r"Usage: irc.py <dump> <httpServer[:httpPort]>"
        print r"Example: ./irc.py irc.freenode.net \#cvn-wp-en wpcvn.com__bot localhost:80"
        print r"Example: ./irc.py irc.wikimedia.org \#en.wikipedia wpcvn.com__bot localhost:80"
        print r"Example: ./irc.py irc.freenode.net.1274487004.74.pkl localhost:8080"
        return

    # extract and initialize IRC ircServer/ircPort (or .pkl)
    s = sys.argv[1].split(":", 1)
    ircServer = s[0]
    if len(s) == 2:
        try:
            ircPort = int(s[1])
        except ValueError:
            print "Error: Erroneous ircPort."
            sys.exit(1)
    else:
        ircPort = 6667


    httpConnection = None;
    try:
        httpConnection = httplib.HTTPConnection(sys.argv[-1])
    except Exception, e:
        print e
        print "Will try to reconnect to " + sys.argv[-1] + " later."
        sleep(1)        

    bot = Irc2Http(channel, nickname, ircServer, ircPort, httpConnection)

if __name__ == "__main__":
    main()
