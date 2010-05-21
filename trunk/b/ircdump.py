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

class TestBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, FILE, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.FILE = FILE

    def on_nicknameinuse(self, c, e):
        print("on_nicknameinuse")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print("on_welcome", c, e)
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        cPickle.dump(e.arguments()[0], self.FILE)
        print e.arguments()[0]
        return

def main():
    if len(sys.argv) != 5:
        print "Usage: testbot <server[:port]> <channel> <nickname> <output.pkl>"
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
    channel = '#' + sys.argv[2]
    nickname = sys.argv[3]
    FILE = open(sys.argv[4], 'wb')

    bot = TestBot(channel, nickname, server, FILE, port)
    bot.start()

if __name__ == "__main__":
    main()
