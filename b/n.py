#!/usr/bin/python
# -*- coding: utf-8  -*-



import nltk


train = [(dict(a=0), 'y'), (dict(a=20), 'y'), (dict(a=35), 'y'),
     (dict(a=75), 'x'), (dict(a=80), 'x'), (dict(a=95), 'x'), (dict(a=100), 'x')]
print train[1][0]['a']
print type(train[1][0]['a'])
quit()
test = [(dict(a=5)), (dict(a=20)), (dict(a=97)), (dict(a=99)), ]

classifier = nltk.MaxentClassifier.train(train)
for t in test:
    pdist = classifier.prob_classify(t)
    print '%s: p(x) = %.4f p(y) = %.4f' % (t, pdist.prob('x'), pdist.prob('y'))
classifier.show_most_informative_features()

quit()

def test_maxent(algorithms):
     classifiers = {}
     for algorithm in nltk.classify.MaxentClassifier.ALGORITHMS:
         if algorithm.lower() == 'megam' or algorithm.lower() == 'tadm':
             continue
         classifiers[algorithm] = nltk.MaxentClassifier.train(
             train, algorithm, trace=0, max_iter=1000)
     print ' '*11+''.join(['      test[%s]  ' % i
                           for i in range(len(test))])
     print ' '*11+'     p(x)  p(y)'*len(test)
     print '-'*(11+15*len(test))
     for algorithm, classifier in classifiers.items():
         print '%11s' % algorithm,
         for featureset in test:
             pdist = classifier.prob_classify(featureset)
             print '%8.2f%6.2f' % (pdist.prob('x'), pdist.prob('y')),
         print
test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS)

