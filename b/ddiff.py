#!/usr/bin/python
# -*- coding: utf-8  -*-

# Dumb Diff Module

from difflib import SequenceMatcher, ndiff, Differ
from collections import defaultdict
from ordereddict import OrderedDict

def ddiff_v1(a, b):
    cruncher = SequenceMatcher(None, a, b)
    d = OrderedDict()
    for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
        if(tag == 'insert' or tag == 'replace'): 
            for t in b[blo:bhi]: 
                d[t] = d.setdefault(t, 0) + 1
        if(tag == 'delete' or tag == 'replace'):
            for t in a[alo:ahi]:
                d[t] = d.setdefault(t, 0) - 1                
    for t, v in d.items():
        if(v > 0): yield '+' + t
        elif(v < 0): yield '-' + t


def ddiff_v2(a, b):
    ahi = len(a); bhi = len(b)          # find last matching 
    while ahi > 0 and bhi > 0:
        ahi -= 1; bhi -= 1;
        if(a[ahi] != b[bhi]): ahi += 1; bhi += 1; break
    
    d = OrderedDict()
    ait = iter(a); bit = iter(b); hi = min(ahi, bhi) 
    for i in xrange(hi):                     
        at = ait.next(); bt = bit.next()
        if(at == bt): continue
        d[at] = d.setdefault(at, 0) - 1
        d[bt] = d.setdefault(bt, 0) + 1
        
    for i in xrange(hi, ahi):
        at = ait.next();
        d[at] = d.setdefault(at, 0) - 1
        
    for i in xrange(hi, bhi):
        bt = bit.next()
        d[bt] = d.setdefault(bt, 0) + 1

    for t, v in d.items():
        if(v > 0): yield '+' + t
        elif(v < 0): yield '-' + t



if __name__ == "__main__":
    a = "HEAD The quick /**/ brown fox jumps over the lazy dog. TAIL".split() 
    b = "HEAD The quick brown fox FUN jumps over the /**/ lazy dog. TAIL".split()
    print "a = '%s'" % a
    print "b = '%s'" % b

    import unittest
    class DefaultTests(unittest.TestCase):
        def test_ddiff_v1(self):
            """verify that ddiff_v1 works"""
            print "\n"
            for d in ddiff_v1(a, b): print d

        def test_ddiff_v2(self):
            """verify that ddiff_v2 works"""
            print "\n"
            for d in ddiff_v2(a, b): print d

        def test_ndiff(self):
            """results from the ndiff"""
            print "\n"
            for d in ndiff(a, b): print d

    suite = unittest.TestLoader().loadTestsFromTestCase(DefaultTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
