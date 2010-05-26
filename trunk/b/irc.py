#! /usr/bin/env python
#
# Example program using ircbot.py.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  


"""

import sys, cPickle
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from time import time, sleep
import re


class Irc2Http(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, http):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.http = http
        # self.re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

        r_bits = r'(^C(^B)?(?P<flags>\S+)(^C|^B)? )'
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
                FILE = open(server, 'rb')
                while True:
                    (t, e) = cPickle.load(FILE)
                    self.on_pubmsg(None, e)
                    # sleep(0.1)
            except EOFError, e:
                FILE.close()
                return
            except Exception, e:
                print("Exception at %s: %s" % (e.__class__.__name__, e.args))
                FILE.close()
                return


        # real irc
        self.FILE = open('%s.%s.pkl' % (server, time()), 'wb')    

        try:
            self.start()
        except KeyboardInterrupt:
            self.connection.quit("Ctrl-C at console")
            self.FILE.close()
            print "Quit IRC."
        except Exception, e:
            self.connection.quit("Unhandled Exception")
            self.FILE.close();
            print("Exception at %s: %s" % (e.__class__.__name__, e.args))        
            raise 


    def on_nicknameinuse(self, c, e):
        print("on_nicknameinuse")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("on_welcome", c, e)
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        if(self.FILE): cPickle.dump((time(), e), self.FILE)        
        
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
        try:
            self.httpConnection.request('PUT', '/s/b', d, {'CONTENT-TYPE' : 'octet/stream'})
            self.httpConnection.getresponse()
        except Exception, e:
            try:
                print e
                print "Warning: httpConnection disconnect/connect."
                httpConnection.close()
                httpConnection.connect()
            except:
                print "Warning: Exception during httpConnection disconnect/connect."
                pass
        return

def serverport(s, default):
    """ extract and initialize IRC server/port """

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = default

    return (server, port)


def main():
    if len(sys.argv) == 3:
        channel = nickname = ""
        ircServer = ircPort = ""
    elif len(sys.argv) == 4 and sys.argv[2][0] == '#':
        channel = sys.argv[2]
        nickname = sys.argv[3]
        (ircServer, ircPort) = serverport(sys.argv[1], 6667)
    else:
        print r"Usage: irc.py <IRC server[:port] <channel> <nickname> <HTTP server[:port]>"
        print r"Usage: irc.py <dump> <HTTP server[:port]>"
        print r"Example: ./irc.py irc.freenode.net \#cvn-wp-en Dc987test localhost:80"
        print r"Example: ./irc.py irc.freenode.net.1274487004.74.pkl localhost:8080"
        return

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
