#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
Dumb Diff: 
  While ugly, it's efficient and works well on Wiki articles.
  Irnores copyedits
  Keeps tokens order
  Returns edit position
  Detects duplications
  Removes matching heads/tails

Algorithm:
 1. cut same head, same tail
 2. put A into the OrderedDict
 3. remove B from the OrderedDict
 4. dump nonzero result
 
 Typical usage (two stages):
  al = e.text.splitlines()
  bl = e.text.splitlines()
  (d, dposl) = ddiff.ddiff_v3(al, bl)    # calculate ddiff for lines
  
  a = []; b = [];  ilA = 0; ilR = 0;     # merge and tokenize
  for line, v in d.items():
      if(v > 0): b.extend(line.split()); ilA += 1
      elif(v < 0): a.extend(line.split()); llB += 1

  (d, dpost) = ddiff.ddiff(a, b);    # calculate ddiff for tokens
  itA = 0; itR = 0;
  for token, v in d.items():
      if(v > 0): itA += 1            # +token
      elif(v < 0): itR += 1          # -token
"""


__version__ = "0.0.0a1"

__license__ = """
Copyright (C) 2010 Dmitry Chichkov.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from ordereddict import OrderedDict

def ddiff(a, b):
    ahi = len(a); bhi = len(b)          # find last matching 
    while ahi > 0 and bhi > 0:
        ahi -= 1; bhi -= 1;
        if(a[ahi] != b[bhi]): ahi += 1; bhi += 1; break
    
    d = OrderedDict()
    ait = iter(a); bit = iter(b); lo = hi = min(ahi, bhi) 
    for i in xrange(hi):                     
        at = ait.next(); bt = bit.next()
        if(at == bt): continue
        if(lo == hi): lo = i 
        d[at] = d.setdefault(at, 0) - 1
        d[bt] = d.setdefault(bt, 0) + 1
        
    for i in xrange(hi, ahi):
        at = ait.next();        
        d[at] = d.setdefault(at, 0) - 1
        
    for i in xrange(hi, bhi):
        bt = bit.next()
        d[bt] = d.setdefault(bt, 0) + 1
        
    return (d, (lo, ahi, bhi))



if __name__ == "__main__":
    import unittest
    from difflib import SequenceMatcher, ndiff, Differ

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
        (d, dpos) = ddiff(a, b)
        for t, v in d.items():
            if(v > 0): yield '+' + t
            elif(v < 0): yield '-' + t

    a = "HEAD. The quick /**/ brown fox jumps over the lazy dog. TAIL".split() 
    b = "HEAD. The quick brown fox FUN FUN FUN jumps over the /**/ lazy dog. TAIL".split()
    print "a = '%s'" % a
    print "b = '%s'" % b

    class DefaultTests(unittest.TestCase):
        def test_ddiff(self):
            print "\n"
            d = ddiff(a, b)
            c = (OrderedDict([('/**/', 0), ('brown', 0), ('fox', 0), ('FUN', 3), 
                              ('jumps', 0), ('over', 0), ('the', 0)]), (3, 9, 12))
            print d
            self.assertEqual(d, c)
            
        def test_ddiff_v1(self):
            """verify that ddiff_v1 works"""
            print "\n"
            for d in ddiff_v1(a, b): print d
            self.assertEqual(d, "+FUN")

        def test_ddiff_v2(self):
            """verify that ddiff_v2 works"""
            print "\n"
            for d in ddiff_v2(a, b): print d
            self.assertEqual(d, "+FUN")

        def test_ndiff(self):
            """results from the ndiff"""
            print "\n"
            for d in ndiff(a, b): print d

    suite = unittest.TestLoader().loadTestsFromTestCase(DefaultTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
