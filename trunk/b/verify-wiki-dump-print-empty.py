#!/usr/bin/python
# -*- coding: utf-8  -*-


"""
"""

__version__='$Id: .py 7909 2010-02-05 06:42:52Z Dc987 $'


# pywikipedia (trunk 2010/03/15) in your PYTHONPATH, configured and running 
import wikipedia, xmlreader, time, sys
NNN = 313797035 


def main():
#    _xml1_arg = None; _xml2_arg = None
#    for arg in wikipedia.handleArgs():
#        if arg.startswith('-xml1') and len(arg) > 6: _xml1_arg = arg[6:]
#        if arg.startswith('-xml2') and len(arg) > 6: _xml2_arg = arg[6:]
    if len(sys.argv) < 2:
        print "Usage: verify-wiki-dump.py enwiki-20100312-pages-meta-history.xml.7z"
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
                (N, N_empty, drt, (NNN - N) / N * drt, e.id, e.revisionid, e.title))
            
    wikipedia.output("%f seconds, N = %d, N_empty = %d" % (time.time() - start, N, N_empty))


if __name__ == "__main__":
#    try:
        main()
#    finally:
#        wikipedia.stopme()

