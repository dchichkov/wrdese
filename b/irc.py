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
import re

import r

class TestBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, user_reputations, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.user_reputations = user_reputations
        self.re_edit = re.compile(r'^C14\[\[^C07(?P<page>.+?)^C14\]\]^C4 (?P<flags>.*?)^C10 ^C02(?P<url>.+?)^C ^C5\*^C ^C03(?P<user>.+?)^C ^C5\*^C \(?^B?(?P<bytes>[+-]?\d+?)^B?\) ^C10(?P<summary>.*)^C'.replace('^B', '\002').replace('^C', '\003').replace('^U', '\037'))

    def on_nicknameinuse(self, c, e):
        print("on_nicknameinuse")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("on_welcome", c, e)
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        match = self.re_edit.match(e.arguments()[0])

        if not match:
                # print "Warning: Regexp does not match (raw): ", e.arguments()[0]
                return
        try:
            msg = unicode(e.arguments()[0],'utf-8')
        except UnicodeDecodeError:
            print "Exception: UnicodeDecodeError"
            return

        match = self.re_edit.match(msg)
        if not match:
            print "Warning: Regexp does not match (unicode)"
            return
        
        d = match.groupdict()
        reputation = self.user_reputations.get(d['user'])
        if(reputation != None and reputation < 0):
            print d['user'], '(', reputation , ')', d['page'], d['url']
        return

def main():
    if len(sys.argv) != 5:
        print "Usage: testbot <server[:port]> <channel> <nickname> reputations.pkl"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]
    r._reputations_arg = sys.argv[4]
    r._output_arg = None
    user_reputations = r.read_reputations()
 

    bot = TestBot(channel, nickname, server, user_reputations, port)
    bot.start()

if __name__ == "__main__":
    main()
