#!/usr/bin/python
# -*- coding: utf-8  -*-


"""
REQ: pywikipedia (>= r8139, May 2010) in your PYTHONPATH, configured and running
     http://pywikipediabot.sourceforge.net/

Usage: verify-wiki-dump-print-empty.py enwiki-20100312-pages-meta-history.xml.7z
"""


__license__ = """
Copyright (C) 2010 Dmitry Chichkov.

This work is licensed under the Creative Commons Attribution-Share Alike 3.0
Unported License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to
Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
"""

__version__='$Id: verify-wiki-dump-print-empty.py 7909 2010-02-05 06:42:52Z Dc987 $'


# pywikipedia (>= r8139) in your PYTHONPATH, configured and running 
import wikipedia, xmlreader, time, sys
NNN = 313797035  # total number of revisions number (used for ETA calculations)


def main():
    if len(sys.argv) < 2:
        print "Usage: verify-wiki-dump-print-empty.py enwiki-20100312-pages-meta-history.xml.7z"
        sys.exit(1)

    _xml1_arg = sys.argv[1];
    wikipedia.output(u"\nFile1: %s" % (_xml1_arg))
    mysite = wikipedia.getSite()

    revisions = xmlreader.XmlDump(_xml1_arg, allrevisions=True).parse()
   
    N = 0; start = time.time(); bid = None;
    N_empty = 0;
    for e in revisions:
        N += 1; 
        if(len(e.text) == 0): 
            N_empty += 1
            wikipedia.output("* EMPTY N %d N_empty %d Page1 %s, Revision %s, Timestamp %s Title %s. Comment %s" % 
                (N, N_empty, e.id, e.revisionid, e.timestamp, e.title, e.comment))

        if(e.id != bid):          # next page....
            bid = e.id; drt = (time.time() - start) / 3600;
            wikipedia.output("N = %d, N_empty = %d, T %f ETA %f : %s %s %s" %
                (N, N_empty, drt, (NNN - N) * drt / N, e.id, e.revisionid, e.title))
            
    wikipedia.output("%f seconds, N = %d, N_empty = %d" % (time.time() - start, N, N_empty))


if __name__ == "__main__":
    main()
