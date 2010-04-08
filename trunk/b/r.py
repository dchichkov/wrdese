#!/usr/bin/python
# -*- coding: utf-8  -*-

#retrain:
# 205.175.123.113
# 68.45.27.72
# 68.221.207.176
# 64.113.165.254

# TODO:
# consecutive edits as one edit
# self-reverts: reverted edit is bad. no reputation change.
# categorize 'bad' edits, based on reverts comments
# use 'rv', 'revert', 'vandal', 'rvv' as revert/vandalism idintifiers
# tokens lifetime - use relative lifetime


# diff: 
# * remove heads/tails
# * notice article/sections removal/replacements
# * mark edit position (begining, middle, end)
# * detect/resist copyedits
# * keep tokens order
# * detect duplications, etc

# 'Revision analysis score bad on known': {'bad': 257, 'good': 14},
# 'Revision analysis score good on known': {'bad': 21, 'good': 707}}


"""
This bot goes over multiple revisions and tries bayesian approach to detect spam/vandalism.

Current code:
    In the history: detects reverts, reverted edits, revert wars.
    Calculate tokens 'lifetime' statistics. Can be used to differentiate between ham/spam tokens/edits.   
    Calculate page diffs. 
    Uses CRM114 (text categorization engine: http://crm114.sourceforge.net) to detect bad/good edits.



These command line parameters can be used to specify which pages to work on:
Example: ./r.py -xml:path/Wikipedia-2010031201*.xml

&params;
    -xml           Retrieve information from a local XML dump(s) (pages-articles
                   or pages-meta-current, see http://download.wikimedia.org).
                   Argument can be given as "-xml:filename_pattern".

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""

__version__='$Id: r.py 7909 2010-02-05 06:42:52Z Dc987 $'

import re, sys, time, calendar, difflib, string, math, hashlib, os, fnmatch
import pprint, ddiff
from collections import defaultdict, namedtuple
from ordereddict import OrderedDict

# pywikipedia (trunk 2010/03/15) in your PYTHONPATH, configured and running 
import wikipedia, pagegenerators, xmlreader, editarticle

# apt-get apt-get install python-numpy python-scipy 
import numpy as np
from scipy import stats

# CRM114, crm.py module by Sam Deane
import crm114   

# known good, known bad revisions
import k

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}

# Summary messages in different languages
# NOTE: Predefined replacement tasks might use their own dictionary, see 'fixes'
# in fixes.py.
msg = {
    'ar':'.....: ..... ..... .....',
    'cs':'Robot odstranil odkaz na náv .lá',
    'de':'Bot: Entferne Selbstlinks',
    'en':'Robot: Removing selflinks',
    'es':'Bot: Eliminando enlaces al mismo artílo',
    'fr':'Robot: Enlè autoliens',
    'he':'...: .... ....... .. ... .....',
    'h':'Bot: Ömagukra mutatóvatkozák eltálísa',
    'ja':'....... ........',
    'ksh':'Bot: Ene Lengk vun de Sigg op sesch sellver, erus jenumme.',
    'nl':'Bot: verwijzingen naar pagina zelf verwijderd',
    'nn':'robot: fjerna sjønkjer',
    'no':'robot: fjerner selvlenker',
    'pl':'Robot automatycznie usuwa linki zwrotne',
    'pt':'Bot: Retirando link para o próo artigo',
    'r':'...: ...... .........-...... . ....... ... ',
    'zh':'...:......',
}

# Command line arguments
_retrain_arg = None
_train_arg = None
_show_diffs_arg = None


def locate(pattern):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    (root, pattern) = os.path.split(pattern)
    if not root: root = os.curdir
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)



def timestamp_to_time(timestamp):
    '''Wikipedia format timestamp to unix time'''
    year = int(timestamp[0:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    hour = int(timestamp[11:13])
    min = int(timestamp[14:16])
    sec = int(timestamp[17:19])
    return calendar.timegm((year, month, day, hour, min, sec))



# generates token 'lifetime' statistics. how long in history token has generally managed to stay 
def analyse_tokens_lifetime(xmlFilenames):
    # stats.describe([1,2,3]): N, (min, max), mean, variance, (sqewness, coefficient of excess kurtosis) 
    # print(stats.describe([15, 47, 51, 99, 86, 86, 86, 86, 86, 22, 22, 22, 22, 22, 22, 51, 51, 51, 51, 51, 51, 54, 54, 54, 54, 54, 54, 55, 55, 55, 55, 55, 55, 11, 11, 11, 11, 11, 11, 431, 431, 431, 431]))
    
    data = defaultdict(list)
    prev = None
    for xmlFilename in xmlFilenames:
        dump = xmlreader.XmlDump(xmlFilename, allrevisions=True)
        revisions = dump.parse()

        for e in revisions:
            #wikipedia.output("Page Revision: %s (%s) %s\n" % (e.timestamp, timestamp_to_time(e.timestamp), e.comment))
            if prev:
                dTime = timestamp_to_time(e.timestamp) - timestamp_to_time(prev.timestamp);
                tokens = prev.text.split()
                for token in tokens:
                    if(len(token) > 40): token = token[40]
                    data[token].append(dTime)
            prev = e

    results = {} 
    for token, v in data.iteritems():
        ldescr = stats.describe(v)
        RSD = math.sqrt(ldescr[3])
        if np.isnan(RSD): RSD = 0
        results[token] = (ldescr[2], RSD, ldescr[0])

    # for token, v in results.iteritems():
    #   wikipedia.output("Token: %s %s" % (token, v))
        
    sorted_results = sorted(results.items(), key=lambda t: t[1][0])
    for v in sorted_results:
        print("[%d] %d +/- %d sec. : %s" % (v[1][2], v[1][0], v[1][1], v[0].encode('utf-8')))
        # wikipedia.output("[%d] %d +/- %d sec. : %s" % (v[1][2], v[1][0], v[1][1], v[0]))


# remove more junk symbols?
def test_ndiff(xmlFilenames):
    i = 0
    t0 = time.time()
    for xmlFilename in xmlFilenames:
        dump = xmlreader.XmlDump(xmlFilename, allrevisions=True)
        revisions = dump.parse()
        prev = None
        for e in revisions:
            wikipedia.output("Revision %d: %s by %s Comment: %s" % (i, e.timestamp, e.username, e.comment))
            wikipedia.output("Diff: http://en.wikipedia.org/w/index.php?diff=prev&oldid=%d" % int(e.revisionid))           
            if prev:
                edit = []
                if(e.text and prev.text):
                    diff = difflib.ndiff(prev.text.split(), e.text.split())
                    ip = 0; im = 0
                    for delta in diff:
                        if   delta[:1] == '+': edit.append('+' + delta[2:]); ip += 1
                        elif delta[:1] == '-': edit.append('-' + delta[2:]); im += 1
                        else: continue
                    wikipedia.output(" \03{lightblue}%s\03{default}\n" % ' '.join(edit))
                    
                    
                    a = prev.text.split(" \t\n[]"); b = e.text.split(" \t\n[]")
                    diff = ddiff.ddiff_v2(a, b)
                    text = ""
                    for d in diff:
                        text += mark(d, lambda x:x[0]=='+')
                        text += ' '
                    wikipedia.output(text)
            prev = e
            i += 1
    wikipedia.output("%f seconds" % (time.time() - t0))





def dump_dictionary(name, d):
    sorted_d = sorted(results.items(), key=lambda t: t[1])


def dump_cstats(stats, ids):
    for v in ids.values():
        v.sort()

    wikipedia.output("===================================================================================")
    pp = pprint.PrettyPrinter(width=140)
    wikipedia.output("stats = \\\n%s" % pp.pformat(stats))
    wikipedia.output("ids = \\\n%s" % pp.pformat(ids))
    wikipedia.output("===================================================================================")



# -------------------------------------------------------------------------
# returns: (rev_score_info, reverts_info, user_reputation)

# reverts_info
# -1  : regular revision
# -2 : between duplicates, by single user (reverted, most likely bad)
# -3 : between duplicates, by other users (reverted, questionable)
# -4 : between duplicates, (revert that was reverted. revert war.)
# -5 : self-revert
# >=0: this revision is a duplicate of
# -------------------------------------------------------------------------
def analyse_reverts(xmlFilenames):    
    EditInfo = namedtuple('EditInfo', 'username, comment, size, utc')
    rev_hashes = defaultdict(list)      # Filling md5 hashes map (md5 -> [list of revision indexes]) for nonempty
    user_revisions = defaultdict(int)   # Filling nuber of nonempty revisions made by user
    edit_info = []
    total_size = total_revisions = 0
    for xmlFilename in xmlFilenames:
        dump = xmlreader.XmlDump(xmlFilename, allrevisions=True)
        revisions = dump.parse() 
        
        for e in revisions:
            # calculate page text hashes and duplicates lists 
            if(e.text):
                m = hashlib.md5()
                m.update(e.text.encode('utf-8'))
                rev_hashes[m.digest()].append(total_revisions)  # total_revisions is just an index really
                user_revisions[e.username] += 1;
            
            edit_info.append(EditInfo(e.username, e.comment, len(e.text), timestamp_to_time(e.timestamp)))
            total_revisions += 1

    # Marking duplicates_info
    # (-1): regular revision
    #  >=0: this revision is a duplicate of
    duplicates_info = [-1] * total_revisions
    for m, indexes in rev_hashes.iteritems():
        if len(indexes) > 1:
            for i in indexes:
                duplicates_info[i] = indexes[0]

    reverts_info = duplicates_info
    # Marking (-2, -4, >=0)
    # -2 : between duplicates, by single user (reverted, most likely bad)
    # -4 : between duplicates, (revert that was reverted. revert war.)        
    # ------------------------------------------------------------------
    # Revision 54 (-1)      User0    Regular edit
    # Revision 55 (55)      User1    Regular edit
    # Revision 56 (-2)      User2    Vandalizm
    # Revision 57 (-2)      User2    Vandalizm
    # Revision 58 (-2)      User3    Correcting vandalizm, but not quite
    # Revision 59 (55)      User4    Revert to Revision 55

    reverted_to = -1
    for i in reversed(xrange(total_revisions)):
        if(reverted_to != -1):            
            if(reverts_info[i] == -1): reverts_info[i] = -2
            elif(reverts_info[i] != reverted_to):
                # wikipedia.output("Revert war: revision %d is a duplicate of %d was later reverted to %d" % (i, reverts_info[i], reverted_to)) 
                reverts_info[i] = -4
        elif(reverts_info[i] >= 0): reverted_to = reverts_info[i]  
        if(i == reverted_to): reverted_to = -1   
    
    # Marking (-3) : between duplicates, by other users (reverted, questionable)
    # Revision 54 (-1)  ->   (-1)                User0    Regular edit
    # Revision 55 (55)  ->   (55)                User1    Regular edit
    # Revision 56 (-2)  ->   (-2)                User2    Vandalizm
    # Revision 57 (-2)  ->   (-2)                User2    Vandalizm
    # Revision 58 (-2)  ->   (-3)                User3    Correcting vandalizm, but not quite
    # Revision 59 (55)  ->   (55)                User4    Revert to Revision 55
    username = None
    for i in xrange(total_revisions):
        if(reverts_info[i] == -2): 
            if(username == None): username = edit_info[i].username
            elif (username != edit_info[i].username): reverts_info[i] = -3
        else: username = None

    # Marking (-5) : self-reverts
    # Revision 54 (-1)  ->   (-1)                User0    Regular edit
    # Revision 55 (55)  ->   (55)                User1    Regular edit
    # Revision 56 (-2)  ->   (-2)                User1    Self-reverted edit
    # Revision 59 (55)  ->   (55)                User4    Revert to Revision 55
    username = None
    for i in reversed(xrange(total_revisions)):
        if(reverts_info[i] > -1 and username == None):
            username = edit_info[i].username
        elif(reverts_info[i] == -2 and username == edit_info[i].username):
            reverts_info[i] = -5
        else: username = None



    # Tracking blankings and near-blankings
    # Establishing user ratings for the user whitelists
    users_reputation = defaultdict(int)
    total_time = total_size = 0
    prev = edit_info[0]
    for i, e in enumerate(edit_info):
        if(e.size * i < total_size):                                        # new page is smaller than the average
            users_reputation[e.username] -= 1
            if(reverts_info[i] == -2):                                      # and it was reverted
                users_reputation[e.username] -= 10
        elif(e.username != prev.username):
            if(reverts_info[i] > -2): users_reputation[e.username] += 1       # regular edit 
            if(reverts_info[i] == -2): users_reputation[e.username] -= 2      # reverted edit
        
        delta_utc = e.utc - prev.utc
        if(delta_utc * i > total_time):              # prev edition has managed longer than usual
            #wikipedia.output("Revision (%d, %d). Boosting user %s(%d)" % (i - 1, i, prev.username, users_reputation[prev.username]))
            #wikipedia.output("    %s" % prev.comment)
            #wikipedia.output("    %s" % e.comment)
            users_reputation[prev.username] += 1

        if(e.comment and len(e.comment) > 80):        # we like long comments
            #wikipedia.output("Revision (%d, %d). Boosting user %s(%d)" % (i - 1, i, e.username, users_reputation[e.username]))
            #wikipedia.output("    %s" % e.comment)
            users_reputation[e.username] += 1
            
        total_size += e.size
        total_time += (e.utc - prev.utc)
        prev = e

    #sorted_users = sorted(users_reputation.items(), key=lambda t: t[1])
    #for u in sorted_users:
    #    wikipedia.output("[%d] %s" % (u[1], u[0]))

 
    # marking initial revision scores
    # adjusting revision scores with user reputation scores
    rev_score_info = [0] * total_revisions
    for i in xrange(total_revisions):
        rev_score_info[i]= users_reputation[edit_info[i].username];
        if(reverts_info[i] == -2):      rev_score_info[i] += -2     # reverted
        elif(reverts_info[i] == -5):    rev_score_info[i] = -5      # self-reverted
        elif(reverts_info[i] < -2):     rev_score_info[i] += -1     
        elif(reverts_info[i] > -1):     rev_score_info[i] += 1

    #for i, e in enumerate(edit_info):
    #    wikipedia.output(">>>  Revision %d (%s, %s) by %s(%s): %s %s : \03{lightblue}%s\03{default}   <<< " %   \
    #                     (i, mark(reverts_info[i], lambda x:x>-2), mark(rev_score_info[i], lambda x:x>-1), e.username,  \
    #                        mark(users_reputation[e.username], lambda x:x>-1), e.utc, e.size, e.comment))


    return (rev_score_info, reverts_info, users_reputation, edit_info)


def mark(value, function):
    if(function(value)): 
        return "\03{lightgreen}%s\03{default}" % value
    return "\03{lightred}%s\03{default}" % value

def urri(ri):
    if(ri > -1): return 'revert'
    return ('self_revert', 'revert_war', 'questionable', 'reverted', 'regular')


def analyse_maxent(xmlFilenames, rev_score_info, reverts_info, users_reputation, edit_info):

    # Tracking blankings and near-blankings
    # Establishing user ratings for the user whitelists
    user_features = defaultdict(lambda: defaultdict(int))                 # TODO: optimize!
    edit_features = [defaultdict(int)] * len(edit_info)                                   #

    def add_feature(f):
        user_features[e.username][f] += 1
        edit_features[i][f] += 1

    total_time = total_size = 0
    prev = edit_info[0]
    for i, e in enumerate(edit_info):
        rii = reverts_info[i]

        if(e.size * i < total_size):                                        # new page is smaller than the average
            add_feature('smaller_than_average')
            if(rii == -2):                                                  # and it was reverted
                add_feature('smaller_and_reverted')

        if(e.size < prev.size): add_feature('smaller')
        elif(e.size > prev.size): add_feature('larger')
        else: add_feature('same_size')

        if(e.username != prev.username): 
            add_feature('different_user')
            add_feature('different_user_' + urri(rii))
        else: 
            add_feature('same_user')
            add_feature('same_' + urri(rii))

        delta_utc = e.utc - prev.utc                                        # prev edition has managed longer than usual
        if(delta_utc * i > total_time): add_feature('accepted')

        if(e.comment): add_feature('comment')
        else: add_feature('no_comment')
        if(e.comment and len(e.comment) > 80): add_feature('long_comment')

        total_size += e.size
        total_time += (e.utc - prev.utc)
        prev = e

    for uf in user_features.values():
        for f, i in uf.iteritems():
            uf[f] = math.trunc(math.log(abs(i) + 1, math.pi/2)) * ((-1, 1)[i > 0])
    
    pp = pprint.PrettyPrinter(width=140)
    wikipedia.output("stats = \\\n%s" % pp.pformat(user_features))
    wikipedia.output("stats = \\\n%s" % pp.pformat(edit_features))



def analyse_crm114(xmlFilenames, rev_score_info, reverts_info, users_reputation):
    # stats
    ids = defaultdict(list)
    stats = defaultdict(lambda:defaultdict(int))
    human_responses = 0
 
    p = re.compile(r'\W+')
    # p = re.compile(r'\s+')

    # CRM114
    c = crm114.Classifier( "data", [ "good", "bad" ] ) 
    i = 0
    prev = None
    for xmlFilename in xmlFilenames:
        #for i in reverts:
        #    wikipedia.output("Revision %d (%d)" % (i[0], i[1]));
        dump = xmlreader.XmlDump(xmlFilename, allrevisions=True)
        revisions = dump.parse()
        for e in revisions:
            score_numeric = rev_score_info[i]                   
            score = ('good', 'bad')[score_numeric < 0]              # current analyse_reverts score
            revid = int(e.revisionid)
            known = k.is_verified_or_known_as_good_or_bad(revid)    # previous score (some human verified)
            verified = k.is_known_as_verified(revid)                # if not Empty: human verified

            #wikipedia.output("Revision %d (%d): %s by %s Comment: %s" % (i, score, e.timestamp, e.username, e.comment))
            if prev:
                diff_time = timestamp_to_time(e.timestamp) - timestamp_to_time(prev.timestamp);               
                edit = []
                if(diff_time < 60): edit.append('ELFsuperfast')
                elif(diff_time < 3600): edit.append('ELFfast')
                elif(diff_time < 3600*24): edit.append('ELFregular')
                else: edit.append('ELFstable')
                # edit.append('ELFtitle')       
                # edit.append(e.title)
                # edit.append('ELFusername')       
                # edit.append(e.username)
                edit.append('ELFusername:' + e.username)
                if(e.ipedit): edit.append("ELFipedit")
                if(e.editRestriction): edit.append("ELFeditRest")
                if(e.moveRestriction): edit.append("ELFmoveRest")
                #edit.append(e.redirect)
                if(e.comment):
                    edit.append('ELFcomment')
                    edit.append(e.comment)
                else: edit.append('ELFnoComment')

                if(e.text and prev.text):                    
                    diff = ddiff.ddiff_v2(p.split(prev.text), p.split(e.text))
                    for d in diff: 
                        edit.append(d)

                elif(e.text and not prev.text): edit.append('ELFrevblank')
                elif(prev.text and not e.text): edit.append('ELFblanking')
                else: edit.append('ELFblank')
                
                edit_text = ' '.join(edit)
                #wikipedia.output(edit_text);
                
                # Run CRM114
                (crm114_answer, probability) = c.classify(edit_text.encode('utf-8'))

                # Human verification
                if(crm114_answer == 'bad' and score == 'good'):  
                    falseString = " >>> \03{lightpurple}FALSE POSITIVE\03{default} <<<"
                elif(crm114_answer == 'good' and score == 'bad'): 
                    falseString = "  >>> \03{lightpurple}False Negative\03{default} <<<"
                else: falseString = ""
                
                # if the retrain arg is set to true, username or the revision id
                retrain = (_retrain_arg == True) or (_retrain_arg == e.username) or (_retrain_arg == revid)

                if(score != known or (not verified and falseString) or retrain):
                    wikipedia.output("\n\n\n\n\n\n\n >>>  Revision %d (%s, %s) by %s(%s): %s %s : \03{lightblue}%s\03{default}   <<< " %   \
                         (i, mark(reverts_info[i], lambda x:x!=-2), mark(score_numeric, lambda x:x>-1), e.username,                         \
                            mark(users_reputation[e.username], lambda x:x>-1), e.timestamp, revid, e.comment))
                    wikipedia.output("Score is %s." % mark(score, lambda x:x=='good'))
                    if(known): wikipedia.output("Known as %s." % mark(known, lambda x:x=='good'))
                    if(verified): wikipedia.output("Verified as %s." % mark(verified, lambda x:x[:3]!='bad'))
                    wikipedia.output("CRM114 thinks it is: %s, prob was:%f %s" % (mark(crm114_answer, lambda x:x=='good'), probability, falseString))
                    
                    wikipedia.output("Diff: http://en.wikipedia.org/w/index.php?diff=prev&oldid=%d" % revid)
                    if(_show_diffs_arg):
                        wikipedia.showDiff(prev.text, e.text)
                    wikipedia.output(" \03{lightblue}%s\03{default}" % edit_text)
                    
                    # uncertain = score_numeric < 1 or reverts_info[i] != -1 or falseString
                    uncertain = falseString
                    if((uncertain and not verified) or retrain):
                        if not known or not verified: known = score     # keep verified answer by default
                        answer = wikipedia.inputChoice(u'Do you want to mark this revision as %s (Yes)?' % \
                                    mark(known, lambda x:x=='good'), ['Yes', 'No', 'Constructive'], ['Y', 'N', 'C'], 'Y')
                        if answer == 'n':
                            wikipedia.output(" \03{lightpurple}***** Wow! *****\03{default} \03{lightgreen}Thank you for correcting me.\03{default}")                                                        
                            known = ('good', 'bad')[known == 'good']                 # inverting/correcting
                        
                        if answer == 'c':
                            known = 'good'
                            verified = 'constructive (corrected by user)'
                        else:                                                    
                            verified = known + (' (corrected by user)', ' (verified by user)')[known == score]
                            
                        wikipedia.output("Marked as %s" % mark(verified, lambda x:x[:3]!='bad'))
                        human_responses += 1
                    else:
                        if(not verified): known = score

                # Collecting stats               
                ids[known].append(revid)
                stats['Revision analysis score ' + score + ' on known'][known] += 1
                if(verified): 
                    ids[verified].append(revid)
                    stats['Revision analysis score ' + score + ' on verified'][verified] += 1
                if(i > 500):
                    stats['CRM114 answered ' + crm114_answer + ' on known'][known] += 1
                    stats['CRM114 answered ' + crm114_answer + ' on score'][score] += 1

                # training CRM114
                if(probability < 0.75 or crm114_answer != known):
                    c.learn(known, edit_text.encode('utf-8'))
                    stats['CRM114 trained'][known] += 1
                    # wikipedia.output("\03{lightpurple}Training %s\03{default}", known)
                 
                if(i % 100 == 0 or human_responses > 5):
                    human_responses = 0
                    dump_cstats(stats, ids)
                    

            prev = e
            i += 1
    dump_cstats(stats, ids)    


def main():
    global _retrain_arg, _train_arg
    pattern_arg = None
    for arg in wikipedia.handleArgs():
        if arg.startswith('-xml') and len(arg) > 5: pattern_arg = arg[5:]
        if arg.startswith('-retrain'): _retrain_arg = True
        if arg.startswith('-retrain') and len(arg) > 9: _retrain_arg = arg[9:]
        if arg.startswith('-train'): _train_arg = True
            
            
    if(not pattern_arg):            # work: lightblue lightgreen lightpurple lightred
        wikipedia.output('Usage: ./r.py \03{lightblue}-xml:\03{default}path/Wikipedia-Single-Page-Dump-*.xml')
        return

    xmlFilenames = sorted(locate(pattern_arg))
    wikipedia.output(u"Files: \n%s\n\n" % xmlFilenames)
    mysite = wikipedia.getSite()

    # test_ndiff(xmlFilenames)
    # analyse_tokens_lifetime(xmlFilenames)
    (rev_score_info, reverts_info, users_reputation, edit_info) = analyse_reverts(xmlFilenames)
    # analyse_maxent(xmlFilenames, rev_score_info, reverts_info, users_reputation, edit_info)
    analyse_crm114(xmlFilenames, rev_score_info, reverts_info, users_reputation)


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

