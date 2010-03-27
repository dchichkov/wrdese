#!/usr/bin/python
# -*- coding: utf-8  -*-

# TODO:
# consecutive edits as one edit
# self-reverts

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
import pprint
from collections import defaultdict, namedtuple

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


def dump_dictionary(name, d):
    sorted_d = sorted(results.items(), key=lambda t: t[1])


def dump_cstats(stats, ids):
    for v in ids.values():
        v.sort()

    wikipedia.output("===================================================================================")
    pp = pprint.PrettyPrinter(width=140)
    wikipedia.output("Stats:\n%s" % pp.pformat(stats))
    wikipedia.output("Revision IDs: ids = \n%s" % pp.pformat(ids))
    wikipedia.output("===================================================================================")



# -------------------------------------------------------------------------
# returns: reverts_info
# -1  : regular revision
# -2 : between duplicates, by single user (reverted, most likely bad)
# -3 : between duplicates, by other users (reverted, questionable)
# -4 : between duplicates, (revert that was reverted. revert war.)
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
                wikipedia.output("Revert war: revision %d is a duplicate of %d was later reverted to %d" % (i, reverts_info[i], reverted_to)) 
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

    # Tracking blankings and near-blankings
    # Establishing user ratings for the user whitelists
    user_score = defaultdict(int)
    total_time = total_size = 0
    prev = edit_info[0]
    for i, e in enumerate(edit_info):
        if(e.size * i < total_size * 0.2):          # new page is smaller than 20% of the average
            user_score[e.username] -= 5
            if(reverts_info[i] < -1):               # and it was reverted
                user_score[e.username] -= 10
        else:
            if(e.username != prev.username):
                if(reverts_info[i] > -2):     user_score[e.username] += 1       # regular edit or revert
                elif(reverts_info[i] == -2):   user_score[e.username] -= 2      # reverted edit
            else:
                if(reverts_info[i] > -1):   user_score[e.username] += 2         # likely self-refert
        
        delta_utc = e.utc - prev.utc
        if(delta_utc * i > total_time):          # prev edition has managed longer than usual
            wikipedia.output("Revision (%d, %d). Boosting user %s(%d)" % (i - 1, i, prev.username, user_score[prev.username]))
            wikipedia.output("    %s" % prev.comment)
            wikipedia.output("    %s" % e.comment)
            user_score[prev.username] += 1

        total_size += e.size
        total_time += (e.utc - prev.utc)
        prev = e

#    sorted_users = sorted(user_score.items(), key=lambda t: t[1])
#    for u in sorted_users:
#        wikipedia.output("[%d] %s" % (u[1], u[0]))
# 
#    rev_info = reverts_info
#    for i in xrange(total_revisions):
#        score = user_score[edit_info[i].username]
#        if(score < 0 and rev_info[i] > -1):             # probable bad
#            wikipedia.output("Detected unusual (%d) edit by user %s (%d)" % (rev_info[i], edit_info[i].username, score))
#            rev_info[i] = -5
#        elif(score > 4 and rev_info[i] < 0):               # whitelist
#            rev_info[i] = 0
#        elif(score > 2 and rev_info[i] == -2):             # unusual to be reverted
#            wikipedia.output("Detected unusual (%d) edit by user %s (%d)" % (rev_info[i], edit_info[i].username, score))
#            rev_info[i] = -6

    # marking initial revision scores
    rev_score_info = [0] * total_revisions
    for i in xrange(total_revisions):
        if(reverts_info[i] == -2):      rev_score_info[i] = -2
        elif(reverts_info[i] < -2):     rev_score_info[i] = -1

    # adjusting revision scores with user reputation scores
    for i in xrange(total_revisions):
        score = user_score[edit_info[i].username];
        if(score > 10): score = 10
        if(score < -10): score = -10
        rev_score_info[i] += score
            
    return (rev_score_info, reverts_info, user_score)


def mark(value, function):
    if(function(value)): 
        return "\03{lightgreen}%s\03{default}" % value
    return "\03{lightred}%s\03{default}" % value
        

def analyse_crm114(xmlFilenames, rev_score_info, reverts_info, user_score):
    # stats
    ids = defaultdict(list)
    stats = defaultdict(lambda:defaultdict(int))
    human_responses = 0
 
    # CRM114
    c = crm114.Classifier( "data", [ "good", "bad" ] ) 
    i = 0
    for xmlFilename in xmlFilenames:
        #for i in reverts:
        #    wikipedia.output("Revision %d (%d)" % (i[0], i[1]));
        dump = xmlreader.XmlDump(xmlFilename, allrevisions=True)
        revisions = dump.parse()
        prev = None
        for e in revisions:
            score_numeric = rev_score_info[i]                   
            score = ('good', 'bad')[score_numeric < 0]   # current analyse_reverts score
            revid = int(e.revisionid)
            known = k.is_known_as_good_or_bad(revid)     # previous score (some human verified)
            verified = k.is_known_as_verified(revid)     # if not Empty: human verified

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
                    diff = difflib.ndiff(prev.text.split(), e.text.split())
                    for delta in diff:
                        if   delta[:1] == '+': edit.append('+' + delta[2:])
                        elif delta[:1] == '-': edit.append('-' + delta[2:])
                        else: continue
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
                
                if(score != known):
                    wikipedia.output("\n\n\n\n\n\n\n >>>  Revision %d (%s, %s) by %s(%s): %s %s : \03{lightblue}%s\03{default}   <<< " %   \
                         (i, mark(reverts_info[i], lambda x:x!=-2), mark(score_numeric, lambda x:x>-1), e.username,                         \
                            mark(user_score[e.username], lambda x:x>-1), e.timestamp, revid, e.comment))
                    wikipedia.output("Score is %s." % mark(score, lambda x:x=='good'))
                    if(known): wikipedia.output("Known as %s." % mark(known, lambda x:x=='good'))
                    if(verified): wikipedia.output("Verified as %s." % mark(verified, lambda x:x[:3]!='bad'))
                    wikipedia.output("CRM114 thinks it is: %s, prob was:%f %s" % (mark(crm114_answer, lambda x:x=='good'), probability, falseString))
                    
                    wikipedia.output("Diff: http://en.wikipedia.org/w/index.php?diff=prev&oldid=%d" % revid)
                    wikipedia.showDiff(prev.text, e.text)
                    wikipedia.output(" \03{lightblue}%s\03{default}" % edit_text[:500])
                    
                    uncertain = score_numeric < 1 or reverts_info[i] != -1 or falseString
                    if(_retrain_arg or (uncertain and not known)):
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
                        known = score

                # Collecting stats               
                ids[known].append(revid)
                if(verified): ids[verified].append(revid)
                stats['Revision analysis score ' + crm114_answer + ' on known'][known] += 1
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
        if arg.startswith('-train'): _train_arg = True
            
            
    if(not pattern_arg):            # work: lightblue lightgreen lightpurple lightred
        wikipedia.output('Usage: ./r.py \03{lightblue}-xml:\03{default}path/Wikipedia-Single-Page-Dump-*.xml')
        return

    xmlFilenames = sorted(locate(pattern_arg))
    wikipedia.output(u"Files: \n%s\n\n" % xmlFilenames)
    mysite = wikipedia.getSite()

    # analyse_tokens_lifetime(xmlFilenames)
    (rev_score_info, reverts_info, user_score) = analyse_reverts(xmlFilenames)
    analyse_crm114(xmlFilenames, rev_score_info, reverts_info, user_score)


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

