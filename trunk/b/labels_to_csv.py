import sys
from labels import k, ids, labels, labels_shortcuts, labeler, good_labels, bad_labels
import pan10_vandalism_test_collection; k.append(gold = pan10_vandalism_test_collection.g)
import ids1277202682; k.append(known = ids1277202682.known, verified = ids1277202682.verified)
#import pan10_vandalism_test_labels; k.append(known = pan10_vandalism_test_collection.g)
#import pan_wvc_10_gold; k.append(known = pan_wvc_10_gold.g);
#import pan_wvc_10_labels; k.append(verified = pan_wvc_10_labels.verified)#, known = pan_wvc_10_labels.known)
#import wrdse10_dchichkov_rocket_annotations as wrdse; k.append(known = wrdse.known, verified = wrdse.verified);


# 26864258 27932250 V 0.92
# 28689695 87188208 R 0.50
# 85047080 85047157 V 0.67
# 80637222 91249168 R 0.43

good = 0; bad = 0; unknown = 0;
for revid, oldid in k.gold.iteritems():
    known = k.is_known(revid)
    if known == 'good':
        good += 1
        if k.verified[revid].endswith('?'): print oldid, revid, 'R', 0.2
        else: print oldid, revid, 'R', 0.0
    elif known == 'bad': 
        bad += 1
        if k.verified[revid].endswith('?'): print oldid, revid, 'V', 0.8
        else: print oldid, revid, 'V', 1.0
    else: 
        unknown += 1
        print oldid, revid, 'R', 0.2

print >> sys.stderr, 'good', good, 'bad', bad, 'unknown', unknown
