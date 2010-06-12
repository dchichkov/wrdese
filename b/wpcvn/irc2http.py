#! /usr/bin/env python
#
# Example program using ircbot.py.
#
# Joel Rosdahl <joel@rosdahl.net>

"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  


"""

import sys, httplib, cPickle
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from time import time, sleep

import secret
from aes_encryption import EncodeAES, DecodeAES


class Irc2Http(SingleServerIRCBot):
    def __init__(self, channel, nickname, ircServer, ircPort=6667, httpConnection=None):
        SingleServerIRCBot.__init__(self, [(ircServer, ircPort)], nickname, nickname)
        self.channel = channel
        self.wbotid=  EncodeAES(secret.botcipher, channel)
        self.httpConnection = httpConnection

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

        headers = { "Connection:" : "Keep-alive",
                    "Content-type": "octet/stream",
                    #"X-Channel": self.channel,
                    #"X-Bot-Name": e.source().split ('!') [0],
                    #"X-Auth": self.wbotid 
                    }

        # forward it to HTTP
        if(self.httpConnection):
            try:
                self.httpConnection.request('PUT', '/s/i', e.arguments()[0], headers)
                self.httpConnection.getresponse().read()
            except Exception, e:
                try:
                    print "Exception:", e
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
        print r"Usage: irc2http.py <IRC ircServer[:ircPort] <channel> <nickname> <httpServer[:httpPort]>"
        print r"Usage: irc2http.py <dump> <httpServer[:httpPort]>"
        print r"Example: ./irc2http.py irc.freenode.net \#cvn-wp-en Dc987bot localhost:80"
        print r"Example: ./irc2http.py irc.wikimedia.org \#en.wikipedia Dc987bot localhost:80"
        print r"Example: ./irc2http.py irc.freenode.net.1274487004.74.pkl localhost:8080"
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
