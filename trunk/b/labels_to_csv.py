import sys
from labels import k, ids, labels, labels_shortcuts, labeler, good_labels, bad_labels
import pan10_vandalism_test_collection; k.append(gold = pan10_vandalism_test_collection.g)
#import pan10_vandalism_test_labels; k.append(known = pan10_vandalism_test_collection.g)
import pan_wvc_10_gold; k.append(known = pan_wvc_10_gold.g);
import pan_wvc_10_labels; k.append(verified = pan_wvc_10_labels.verified)#, known = pan_wvc_10_labels.known)
import wrdse10_dchichkov_rocket_annotations as wrdse; k.append(known = wrdse.known, verified = wrdse.verified);


# 26864258 27932250 V 0.92
# 28689695 87188208 R 0.50
# 85047080 85047157 V 0.67
# 80637222 91249168 R 0.43

for revid, oldid in k.gold.iteritems():
    known = k.is_known(revid)
    if known == 'good': print oldid, revid, 'R', k.info_string(revid)
    elif known == 'bad': print oldid, revid, 'V', k.info_string(revid)
    else: print >> sys.stderr, oldid, revid
