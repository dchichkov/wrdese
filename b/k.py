#!/usr/bin/python
# -*- coding: utf-8  -*-


from collections import defaultdict
from bisect import bisect
from pprint import pprint

from d import ids
# sorting it, required
for v in ids.values():
    v.sort()


# unnoticed bad
# '7060009', '51041574', '51041574'

# questionable (undercorrected)
# '22844172', '39716432', '47930699'

def in_sorted_list(l, v):
    if(len(l) < 5): return v in l
    else: return l[bisect(l, v) - 1] == v

def is_known(id):
    for k, l in ids.items():
        if in_sorted_list(l, id): return k
    return None

def is_known_as(id, classification):
    return in_sorted_list(ids[classification], id)

def is_known_as_verified(id):
    for k, l in ids.items():
        if k == 'good': continue
        if k == 'bad': continue
        if in_sorted_list(l, id): return k
    return None

def is_known_as_good_or_bad(id):
    if in_sorted_list(ids['good'], id): return 'good'
    if in_sorted_list(ids['bad'], id): return 'bad'
    return None


def is_verified_or_known_as_good_or_bad(id):
    verified = is_known_as_verified(id)
    if(verified): return ('good', 'bad')[verified[:3] == 'bad']
    return is_known_as_good_or_bad(id)



if __name__ == "__main__":
    import unittest

    class DefaultTests(unittest.TestCase):
        def test_pprint(self):
            int_ids = defaultdict(list)
            for k, l in ids.items():
                for id in l:
                    int_ids[k].append(int(id))
            for v in int_ids.values():
                v.sort()                   
            print("\nids = \n")
            pprint(int_ids, width=140)

        def test_known_as(self):
            """verify that is_known_as works"""
            test_cases = 0
            for k, l in ids.items():
                for id in l:
                    if not is_known_as(id, k):
                        print "FAILED(a) at k = %s id = %s" % (k, id)
                        self.fail()
                    if is_known_as(id, 'good') and is_known_as(id, 'bad'):
                        print "FAILED(b) at id = %s" % (k, id)
                        self.fail()
                    test_cases += 1
            print "(%d)" % test_cases

        def test_known_as_verified(self):
            """verify that is_known_as_verified and is_known_as_good_or_bad works and check dataset for errors"""
            test_cases = 0
            for k, l in ids.items():
                for id in l:
                    verified = is_known_as_verified(id)
                    known = is_known_as_good_or_bad(id)
                    if verified and not known:
                        print "FAILED(c) at k = %s id = %s, verified = %s, known = %s" % (k, id, verified, known)
                        self.fail()
                    elif verified and known == 'good':
                        if verified.find('good') < 0 and verified.find('constructive') < 0:
                            print "Warning(c) at k = %s id = %s, verified = %s, known = %s" % (k, id, verified, known)
                    elif verified and known:
                        if verified.find(known) < 0:
                            print "Warning(d) at k = %s id = %s, verified = %s, known = %s" % (k, id, verified, known)
                    test_cases += 1
            print "(%d)" % test_cases

        def test_is_verified_or_known_as_good_or_bad(self):
            """verify that is_verified_or_known_as_good_or_bad works and check dataset for errors"""
            test_cases = 0
            for k, l in ids.items():
                for id in l:
                    verified = is_known_as_verified(id)
                    known = is_verified_or_known_as_good_or_bad(id)
                    if verified and not known:
                        print "FAILED(c) at k = %s id = %s, verified = %s, known = %s" % (k, id, verified, known)
                        self.fail()
                    elif verified and known == 'good':
                        if verified.find('good') < 0 and verified.find('constructive') < 0:
                            print "FAILED(c) at k = %s id = %s, verified = %s, known = %s" % (k, id, verified, known)
                            self.fail()
                    elif verified and known:
                        if verified.find(known) < 0:
                            print "FAILED(d) at k = %s id = %s, verified = %s, known = %s" % (k, id, verified, known)
                            self.fail()
                    test_cases += 1
            print "(%d)" % test_cases


        def test_duplicates(self):
            """verify that lists don't have any duplicates and sorted in the correct order"""
            test_cases = 0
            for k, l in ids.items():
                prev = 0
                for id in l:
                    if prev >= id:
                        print "FAILED(c) at k = %s id = %s" % (k, id)
                        self.fail()
                    prev = id
                    test_cases += 1
            print "(%d)" % test_cases
 
    suite = unittest.TestLoader().loadTestsFromTestCase(DefaultTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

