#!/usr/bin/python
# -*- coding: utf-8  -*-


from difflib import SequenceMatcher, ndiff, Differ
from collections import defaultdict
from ordereddict import OrderedDict



# diff = Differ(None, lambda x: x == ' ').compare('other text'.split(), 'random text'.split())
# diff = ndiff('other text'.split(), 'random text'.split(), None, lambda x: x == ' ')
# print '\n'.join(diff)




a = "/* some comment */ other text a very long one really ".split() 
b = "random text a very long one really /* some comment */".split()
print "a = '%s'" % a
print "b = '%s'" % b

cruncher = SequenceMatcher(None, a, b)
dseqs = defaultdict(int)
for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
    print("---------------------------")
    print(tag, alo, ahi, blo, bhi)
    print("'%s'" % a[alo:ahi])
    print("'%s'" % b[blo:bhi])
    if(tag == 'insert' or tag == 'replace'): 
        for t in b[blo:bhi]: 
            dseqs[t] += 1
            print("+%s" % t)            
    if(tag == 'delete' or tag == 'replace'):
        for t in a[alo:ahi]:
            dseqs[t] -= 1                        
            print("-%s" % t)

for t, v in dseqs.items():
    if(v > 0): print("+++%s" % t)
    elif(v < 0): print("---%s" % t)



print "==========================================="

d = OrderedDict()
for t in a:
    d[t] = d.setdefault(t, 0) - 1
    
for t in b:
    d[t] = d.setdefault(t, 0) + 1

text = ""
for t, v in d.items():
    if(v > 0): text += " +++%s" % t
    elif(v < 0): text += " ---%s" % t
print(text)




