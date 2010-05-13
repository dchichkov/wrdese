#!/usr/bin/python
# -*- coding: utf-8  -*-
import nltk
import maxent, megam
#import nltk.classify.maxent as maxent
#import nltk.classify.megam as megam
from collections import defaultdict
from pprint import pformat


def test_typed_megam(name, train, test):
    print '\n\n\n========================================================================='
    print 'Testing ', name
    print '========================================================================='

    enc = maxent.TypedMaxentFeatureEncoding.train(train, alwayson_features=True)

    for fs in train:
        s = ""; 
        for f, v in fs[0].iteritems(): s += " : %s = %4s " % (f, v)
        print("Featureset", s, " Class: ", fs[1] , "Encoding is: ", enc.encode(fs[0], fs[1]))

    # for fid in xrange(0,2): print enc.describe(fid)

    megam.config_megam('./megam_i686.opt')
    classifier = maxent.MaxentClassifier.train(train, algorithm='megam', min_lldelta=1e-7, \
                    encoding=enc, bernoulli=False, max_iter=100,trace=2)
    
    for t in test:
        pdist = classifier.prob_classify(t)
        classified = ('small', 'BIG')[pdist.prob('BIG') > pdist.prob('small')]
        s = ""; ss = "";
        for f, v in t.iteritems(): s += " : %s = %4s " % (f, v)
        print 'Test %s classified as %s [P(small) = %.4f, p(BIG) = %.4f]' \
            % (s, classified, pdist.prob('small'), pdist.prob('BIG'))
        classifier.explain(t)
        print
    classifier.show_most_informative_features() 


train = [(dict(a=0), 'small'), (dict(a=20), 'small'), (dict(a=35), 'small'),
     (dict(a=75), 'BIG'), (dict(a=80), 'BIG'), (dict(a=95), 'BIG'),
    (dict(a=100), 'BIG')]

test = [(dict(a=10)), (dict(a=25)), (dict(a=50)), (dict(a=70)), (dict(a=90))]
test_typed_megam("Integer features", train, test)



train = [(dict(a=0.0), 'small'), (dict(a=0.20), 'small'), (dict(a=0.35), 'small'),
     (dict(a=0.75), 'BIG'), (dict(a=0.80), 'BIG'), (dict(a=0.95), 'BIG'),
    (dict(a=0.100), 'BIG')]

test = [(dict(a=0.10)), (dict(a=0.25)), (dict(a=0.50)), (dict(a=0.70)), (dict(a=0.90))]
test_typed_megam("Float features", train, test)



train = [(dict(a=0, b=False), 'small'), (dict(a=20), 'small'), (dict(a=35, b=False), 'small'),
     (dict(a=75), 'BIG'), (dict(a=80), 'BIG'), (dict(a=95), 'BIG'),
    (dict(a=100, b=True), 'BIG')]

test = [(dict(a=10)), (dict(a=25)), (dict(a=50)), (dict(a=70)), (dict(a=90)),
        (dict(a=10, b=False)), (dict(a=25, b=False)), (dict(a=50, b=False)), (dict(a=70, b=False)), (dict(a=90, b=False)),
        (dict(a=10, b=True)), (dict(a=25, b=True)), (dict(a=50, b=True)), (dict(a=70, b=True)), (dict(a=90, b=True))]

test_typed_megam("Mixed integer and binary features", train, test)



train = [(dict(a=0, b=0), 'small'), (dict(a=20), 'small'), (dict(a=35, b=0), 'small'),
     (dict(a=75), 'BIG'), (dict(a=80), 'BIG'), (dict(a=95), 'BIG'),
    (dict(a=100, b=1), 'BIG')]

test = [(dict(a=10)), (dict(a=25)), (dict(a=50)), (dict(a=70)), (dict(a=90)),
        (dict(a=10, b=0)), (dict(a=25, b=0)), (dict(a=50, b=0)), (dict(a=70, b=0)), (dict(a=90, b=0)),
        (dict(a=10, b=1)), (dict(a=25, b=1)), (dict(a=50, b=1)), (dict(a=70, b=1)), (dict(a=90, b=1))]

test_typed_megam("Mixed integer and integer features", train, test)



train = [(dict(a=0.0, b=False), 'small'), (dict(a=0.20), 'small'), (dict(a=0.35, b=False), 'small'),
     (dict(a=0.75), 'BIG'), (dict(a=0.80), 'BIG'), (dict(a=0.95), 'BIG'),
    (dict(a=0.100, b=True), 'BIG')]

test = [(dict(a=0.10)), (dict(a=0.25)), (dict(a=0.50)), (dict(a=0.70)), (dict(a=0.90)),
        (dict(a=0.10, b=False)), (dict(a=0.25, b=False)), (dict(a=0.50, b=False)), (dict(a=0.70, b=False)), (dict(a=0.90, b=False)),
        (dict(a=0.10, b=True)), (dict(a=0.25, b=True)), (dict(a=0.50, b=True)), (dict(a=0.70, b=True)), (dict(a=0.90, b=True))]

test_typed_megam("Mixed float and binary features", train, test)




train = [(dict(a=0.0, b='sFALSE'), 'small'), (dict(a=0.20), 'small'), (dict(a=0.35, b='sFALSE'), 'small'),
     (dict(a=0.75), 'BIG'), (dict(a=0.80), 'BIG'), (dict(a=0.95), 'BIG'), (dict(a=0.100, b='sTRUE'), 'BIG')]

test = [(dict(a=0.10)), (dict(a=0.25)), (dict(a=0.50)), (dict(a=0.70)), (dict(a=0.90)),
        (dict(a=0.10, b='sFALSE')), (dict(a=0.25, b='sFALSE')), (dict(a=0.50, b='sFALSE')), 
        (dict(a=0.70, b='sFALSE')), (dict(a=0.90, b='sFALSE')),
        (dict(a=0.10, b='sTRUE')), (dict(a=0.25, b='sTRUE')), (dict(a=0.50, b='sTRUE')), 
        (dict(a=0.70, b='sTRUE')), (dict(a=0.90, b='sTRUE'))]

test_typed_megam("Mixed float and string features", train, test)



