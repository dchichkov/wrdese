#!/usr/bin/python
# -*- coding: utf-8  -*-

# How comes rep["217.42.224.103"] = -1???


#retrain BAD: 167750423, 285306288

# 167750423

# TODO:
# consecutive edits as one edit
# self-reverts: reverted edit is bad. no reputation change.
# tokens lifetime - use relative lifetime
# switch to F1-score


# Users with bad reputation can do good edits:
# * self reverts
# * partial self reverts
# * regular edits
# *  

# Information extraction from user comments
#  * usernames (self, other) and revision id's in the comment
#  * 'undid', 'rvv', 'rv', 'revert', 'vandal', etc in the comment
#  * categorize 'bad' edits, based on reverts comments
#     use 'rv', 'revert', 'vandal', 'rvv' as revert/vandalism idintifiers
#  



# Edit labels:
#    * 'bad' - automatically identified edits that generally require a revert (some human verified)
#    * 'good' - automatically identified good faith edits (some human verified)
#
# Additional extra information (revisions in these lists are already in the 'good' or 'bad'):
#    * 'good (corrected by user)' - good edits (automatically identified, corrected by a human)
#    * 'constructive (corrected by user)' - good edits, questionably good edits, partial vandalism reverts, etc. (human corrections)
#    * 'bad (corrected by user)' - bad edits (automatically identified, corrected by a human)
#    * 'bad (verified by user)' - bad edits (automatically identified, verified by a human)
#    * 'good (verified by user)' - good edits (automatically identified, verified by a human)


# Edit by:
# vandal, regular

# Whose edit was it:
# self, other user

# Possible extra labels:
# 'rv'   - reverting no consensus
# 'rwar' - reverting edit warring
# 'rvv'  - reverting vandalism  
# 'rself' - self reverting

# 'rpart' - partial revert 


# 'vins' - vandal inserted nonsence or graffiti
# 'vdel' - vandal deleted content or blanked a page
# 'vr' - vandal reverted a page
# 'vrself' - vandal did a self revert
# 'vgood' - vandal did a constructive edit


# Taxonomy: from "Detecting Wikipedia Vandalism with Active Learning and Statistical Language Models"
# Possible labels: misinformation, mass delete, partial delete, offensive, spam, nonsense
# 
# Actions: change, insert, delete, and revert
# Types of change: format, content
#
# Common v types: blanking, large-scale editing, graffitti, misinformaiton,
#                image attack, link spam, irregular formatting


# Future releases/datasets:
# 1. More detailed edit label: regular; vandalism; revert of v.; partial revert of v.
# 2. Detailed v. labeling: graffiti; blanking; nonsense; joke, link-spam; revert; misinformation; image-attack; formatting.
# 3. Detailed regular edits labeling: correction, insertion, deletion, copyedit, formatting, revert, revert war, etc.
# 4. Article condition before and after the edit: vandalized, normal.
# 5. Datasets featuring the entire article history.


# Possible features:
# large-scale editing
# ratio of upper-case letters
# time of the day
# maximum length of a word in the new edit
# edit position (infobox, top, regular, bottom)
# image insertion or change
# changing named entities

# +1 (next), -1 (prev) revisions features



# ==================================================================================
# belief propagation
#
# (user reputation) -> {edit, edit, edit}
#        negative for self-reverts
#
# (user reputation) -> {previous edit, previous edit}
#           negative for reverts
#
# edit -> user reputation
#

# 1) Mark edits based on heuristics
# 2) Calculate reputation based on heuristics
# 3) Mark edits based on reputation
# 4) Adjust reputations
# Repeat 3/4



"""
This bot goes over multiple revisions and tries bayesian approach to detect spam/vandalism.

Current code:
    In the history: detects reverts, reverted edits, revert wars.
    Calculate tokens 'lifetime' statistics. Can be used to differentiate between ham/spam tokens/edits.   
    Calculate page diffs. 
    Uses CRM114 (text categorization engine: http://crm114.sourceforge.net) to detect bad/good edits.



These command line parameters can be used to specify which pages to work on:
Example: ./r.py -xml:path/Wikipedia-2010031201*.xml.7z

&params;
    -xml           Retrieve information from a local XML dump(s) (pages-articles
                   or pages-meta-current, see http://download.wikimedia.org).
                   Argument can be given as "-xml:filename_pattern".

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""

__version__='$Id: r.py 7909 2010-02-05 06:42:52Z Dc987 $'

import re, sys, time, calendar, difflib, string, math, hashlib, os, fnmatch, marshal
import pprint, ddiff
from collections import defaultdict, namedtuple
from ordereddict import OrderedDict

# pywikipedia (trunk 2010/03/15) in your PYTHONPATH, configured and running 
import wikipedia, pagegenerators, xmlreader, editarticle

# CRM114, crm.py module by Sam Deane
import crm114   

# known good, known bad revisions
import wicow08r_chin_microsoft_annotation as k
#import pan_wvc_10_gold as k
#import k

NNN = 313797035 # total revisions in the dump


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
_verbose_arg = None

# Human iteractions
_human_responses = 0

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


# TODO:
# * remove more junk symbols?
def compute_pyc(xmlFilenames):
    ''' use _verbose_arg to display verbose output
        use _output_arg to output diffs, md5s and metainfo to .pyc file'''

    if(_output_arg):
        FILE = open(_output_arg, 'wb')

    # separators between tokens
    p = re.compile(r'\, |\. |\s+')

    total_revisions = 0; start = time.time(); full_info = None; fake_id = -1; prev_title = None;
    al = []; bl = []; bid = None; asndiff = []; bsndiff = []; bndiffid = None
    for xmlFilename in xmlFilenames:
        dump = xmlreader.XmlDump(xmlFilename, allrevisions=True)
        revisions = dump.parse()
        for e in revisions:
            total_revisions += 1
            try:
                id = int(e.id)
                prev_title = None
            except:                 # process pages without id
                if(e.title != prev_title): fake_id -= 1;
                prev_title = e.title
                id = fake_id;

            if(id == bid):          # still analyzing the same page....
                al = bl             # bl - previous revision text (split into lines)
            else: 
                al = []; bid = id; drt = (time.time() - start) / 3600;
                wikipedia.output("R %d T %f ETA %f : %d %s %s %s" % 
                    (total_revisions, drt, (NNN - total_revisions) / total_revisions * drt, id, e.id, e.revisionid, e.title))
            bl = e.text.splitlines()

            # merge (removed, added) lines and split them into tokens (a, b)
            # a - tokens from the al (removed), b - tokens from the bl (added)
            # ilA - number of added (new) lines, 
            # ilR - number of removed lines
            (d, dposl) = ddiff.ddiff(al, bl)     # calculate ddiff for lines
            a = []; b = []; ilA = 0; ilR = 0; ilM = 0;
            for t, v in d.items():
                if(v > 0 and ilA < 5): b.extend(p.split(t)); ilA += 1
                elif(v < 0 and ilR < 5): a.extend(p.split(t)); ilR += 1
                else: ilM += 1

            if(_output_arg):
                (d, dposw) = ddiff.ddiff(a, b); iwA = 0; iwR = 0; iwM = 0
                diff = []
                for t, v in d.items():
                    if(v > 0 and iwA < 50): diff.append((t, v)); iwA += 1
                    elif(v < 0 and iwR < 50): diff.append((t, v)); iwR += 1
                    else: iwM += 1

                # calculate page text hashes (have nothing to do with diffs)
                digest = None
                if(e.text):
                    m = hashlib.md5(e.text.encode('utf-8'))
                    digest = m.digest()

                try:
                    full_info = (id, int(e.revisionid), e.username, e.comment, e.title, 
                            len(e.text), timestamp_to_time(e.timestamp), digest, e.ipedit,
                            e.editRestriction, e.moveRestriction, e.isredirect,
                            len(al), len(bl), dposl[0], dposl[1], dposl[2], 
                            ilA, ilR, iwA, iwR, ilM, iwM, diff)
                    marshal.dump(full_info, FILE)
                except:
                    wikipedia.output("Error at: %s %s %s %s" % (e.id, e.revisionid, e.title, e.timestamp))   
            
            if(_verbose_arg):
                if(id == bndiffid): asndiff = bsndiff     # previous revision text
                else: asndiff = []; bndiffid = id         # previous revision was from a different page!                
                bsndiff = e.text.split()
                ip = 0; im = 0; edit = [];
                for delta in difflib.ndiff(asndiff, bsndiff):
                    if   delta[:1] == '+': edit.append('+' + delta[2:]); ip += 1
                    elif delta[:1] == '-': edit.append('-' + delta[2:]); im += 1
                    else: continue                 
                
                wikipedia.output("\n-------------------------------------------------------------------------------")
                wikipedia.output("Revision %d: %s by %s Comment: %s" % (total_revisions, e.timestamp, e.username, e.comment))
                wikipedia.output("Diff: http://en.wikipedia.org/w/index.php?diff=%d" % int(e.revisionid))
                wikipedia.output(" \03{lightblue}%s\03{default}\n" % ' '.join(edit))
                show_diff(full_info)
                wikipedia.output("Full: %s" % str(full_info))

    wikipedia.output("%f seconds" % (time.time() - start))





def dump_dictionary(name, d):
    sorted_d = sorted(results.items(), key=lambda t: t[1])


def dump_cstats(stats, ids):
    for v in ids.values():
        v.sort()

    wikipedia.output("===================================================================================")
    pp = pprint.PrettyPrinter(width=140)
    wikipedia.output("ids = \\\n%s" % pp.pformat(ids))
    wikipedia.output("stats = \\\n%s" % pp.pformat(stats))
    wikipedia.output("===================================================================================")



def display_pyc():
    FILE = open(_pyc_arg, 'rb')
    total_revisions = 0; total_pages = 0; 
    start = time.time()
    try:
        while True:
            info = marshal.load(FILE)
            total_revisions += 1
            if(_verbose_arg): wikipedia.output(str(info))
    except IOError, e:
        raise
    except EOFError, e:
        wikipedia.output("Revision %d. Analysis time: %f" % (total_revisions, time.time() - start))



class FullInfo(object):
    __slots__ = ('i', 'reverts_info', 'rev_score_info',
                 'id', 'revid', 'username', 'comment', 'title', 'size', 'utc', 'md5', 'ipedit',
                 'al', 'bl', 'lo', 'ahi', 'bhi', 'ilA', 'ilR', 'iwA', 'iwR', 'diff'
                  )

    def __init__(self, args):
        (self.id, self.revid, self.username, self.comment, self.title,
        self.size, self.utc, self.md5, self.ipedit,
        self.al, self.bl, self.lo, self.ahi, self.bhi,
        self.ilA, self.ilR, self.iwA, self.iwR, self.diff) = args

        self.reverts_info = -1
        self.rev_score_info = 0



def read_pyc():
    wikipedia.output("Reading %s..." % _pyc_arg)
    FILE = open(_pyc_arg, 'rb')
    start = time.time()    
    try:
        info = FullInfo(marshal.load(FILE))     # load first in order to  
        revisions = []; id = info.id;           # initialize id from info.id
        revisions.append(info)
        while True:
            info = FullInfo(marshal.load(FILE))
            if(id != info.id):
                yield revisions
                revisions = []
                id = info.id
            revisions.append(info)
    except IOError, e:
        raise
    except EOFError, e:
        wikipedia.output("Done reading %s. Read time: %f." % (_pyc_arg, time.time() - start))

    yield revisions


def filter_pyc():
    total_pages = 0
    FILE = open(_output_arg, 'wb')
    start = time.time()
    total_pages = 0; total_revisions = 0;
    filtered_pages = 0; filtered_revisions = 0;

    for revisions in read_pyc():
        total_pages += 1;
        total_revisions += len(revisions)
        if(total_pages%100 == 0):
            wikipedia.output("Page %d. Revs %d. Filtered Pages %d. Filtered Revs %d. Analysis time: %f. ETA %f Hours." %
                (total_pages, total_revisions, filtered_pages, filtered_revisions, time.time() - start,
                 (NNN - total_revisions) / total_revisions * (time.time() - start) / 3600 ))
        
        for e in revisions:
            known = k.is_known_as_verified(e.revid)
            if known: break
        if not known: continue
        k.g[e.revid] = 'known'
        for e in revisions:
            full_info = (e.id, e.revid, e.username, e.comment, e.title,
                e.size, e.utc, e.md5, e.ipedit,
                e.al, e.bl, e.lo, e.ahi, e.bhi,
                e.ilA, e.ilR, e.iwA, e.iwR, e.diff)
            marshal.dump(full_info, FILE)
            filtered_revisions += 1
        filtered_pages += 1

    print k.g


def read_reputations():
    wikipedia.output("Reading %s..." % _reputations_arg)
    FILE = open(_reputations_arg, 'rb')
    user_reputations = defaultdict(int)
    start = time.time()
    try:
        while True:
            (u,r) = marshal.load(FILE)
            user_reputations[u] += r
    except IOError, e:
        raise
    except EOFError, e:
        wikipedia.output("Done reading %s. Read time: %f. Total users: %d" % (_reputations_arg, time.time() - start, len(user_reputations)))

    if(_output_arg):
        FILE = open(_output_arg, 'wb')
        for u, r in user_reputations.iteritems():
            marshal.dump((u, r), FILE)

    return user_reputations




def display_last_timestamp(xmlFilenames):
    total_revisions = 0
    for xmlFilename in xmlFilenames:
        revisions = xmlreader.XmlDump(xmlFilename, allrevisions=True).parse()
        for e in revisions:
            total_revisions += 1
    
    wikipedia.output("Total revision analyzed: %d" % total_revisions)
    if(total_revisions): wikipedia.output("Timestamp of the last revision: %s" % e.timestamp)
    
def special_export(title)
    headers = {'User-Agent': 'PythonWikipediaBot/1.0'} # Needs to fool Wikipedia so it will give us the file
    params = urllib.urlencode({'title': 'Special:Export','pages': 'User:Dc987test', 'action': 'submit', 'limit': 100, }
    req = urllib2.Request(url='http://en.wikipedia.org/w/index.php',data=params, headers=headers)
    f = urllib2.urlopen(req)
    print f.read()



# -------------------------------------------------------------------------
# initializes: revisions[].reverts_info

# reverts_info
# -1  : regular revision
# -2 : between duplicates, by single user (reverted, most likely bad)
# -3 : between duplicates, by other users (reverted, questionable)
# -4 : between duplicates, (revert that was reverted. revert war.)
# -5 : self-revert
# >=0: this revision is a duplicate of
# -------------------------------------------------------------------------
def analyse_reverts(revisions):
    rev_hashes = defaultdict(list)      # Filling md5 hashes map (md5 -> [list of revision indexes]) for nonempty
    user_revisions = defaultdict(int)   # Filling nuber of nonempty revisions made by user
    total_revisions = len(revisions)

    for i, e in enumerate(revisions):
        # calculate page text hashes and duplicates lists 
        if(e.md5):
            rev_hashes[e.md5].append(i)
            user_revisions[e.username] += 1;
        e.i = i

    # Marking duplicates_info
    # (-1): regular revision
    #  >=0: this revision is a duplicate of
    for m, indexes in rev_hashes.iteritems():
        if len(indexes) > 1:
            for i in indexes:
                revisions[i].reverts_info = indexes[0]

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

    reverted_to = None
    for e in reversed(revisions):
        if(reverted_to != None):            
            if(e.reverts_info == -1): e.reverts_info = -2
            elif(e.reverts_info != reverted_to):
                # wikipedia.output("Revert war: revision %d is a duplicate of %d was later reverted to %d" % (i, reverts_info[i], reverted_to)) 
                e.reverts_info = -4
        elif(e.reverts_info >= 0): reverted_to = e.reverts_info
        if(e.i == reverted_to): reverted_to = None
    
    # Marking (-3) : between duplicates, by other users (reverted, questionable)
    # Revision 54 (-1)  ->   (-1)                User0    Regular edit
    # Revision 55 (55)  ->   (55)                User1    Regular edit
    # Revision 56 (-2)  ->   (-2)                User2    Vandalizm
    # Revision 57 (-2)  ->   (-2)                User2    Vandalizm
    # Revision 58 (-2)  ->   (-3)                User3    Correcting vandalizm, but not quite
    # Revision 59 (55)  ->   (55)                User4    Revert to Revision 55
    username = None
    for e in revisions:
        if(e.reverts_info == -2): 
            if(username == None): username = e.username
            elif (username != e.username): e.reverts_info = -3
        else: username = None

    # Marking (-5) : self-reverts
    # Revision 54 (-1)  ->   (-1)                User0    Regular edit
    # Revision 55 (55)  ->   (55)                User1    Regular edit
    # Revision 56 (-2)  ->   (-2)                User1    Self-reverted edit
    # Revision 59 (55)  ->   (55)                User4    Revert to Revision 55
    username = None
    for e in reversed(revisions):
        if(e.reverts_info > -1 and username == None):
            username = e.username
        elif(e.reverts_info == -2 and username == e.username):
            e.reverts_info = -5
        else: username = None


# -------------------------------------------------------------------------
# returns: user_reputation
# initializes: revisions[].rev_score_info
# -------------------------------------------------------------------------
def analyse_reputations(revisions):
    # Tracking blankings and near-blankings
    # Establishing user ratings for the user whitelists
    user_reputations = defaultdict(int)
    total_time = total_size = 0
    prev = revisions[0]
    for i, e in enumerate(revisions):
        if(e.size * i < total_size):                                        # new page is smaller than the average
            user_reputations[e.username] -= 1
            if(e.reverts_info == -2):                                      # and it was reverted
                user_reputations[e.username] -= 10
        elif(e.username != prev.username):
            if(e.reverts_info > -2): user_reputations[e.username] += 1       # regular edit 
            if(e.reverts_info == -2): user_reputations[e.username] -= 2      # reverted edit
        
        delta_utc = e.utc - prev.utc
        if(delta_utc * i > total_time):              # prev edition has managed longer than usual
            #wikipedia.output("Revision (%d, %d). Boosting user %s(%d)" % (i - 1, i, prev.username, user_reputations[prev.username]))
            #wikipedia.output("    %s" % prev.comment)
            #wikipedia.output("    %s" % e.comment)
            user_reputations[prev.username] += 1

        if(e.comment and len(e.comment) > 80):        # we like long comments
            #wikipedia.output("Revision (%d, %d). Boosting user %s(%d)" % (i - 1, i, e.username, user_reputations[e.username]))
            #wikipedia.output("    %s" % e.comment)
            user_reputations[e.username] += 1
            
        total_size += e.size
        total_time += (e.utc - prev.utc)
        prev = e

    #sorted_users = sorted(user_reputations.items(), key=lambda t: t[1])
    #for u in sorted_users:
    #    wikipedia.output("[%d] %s" % (u[1], u[0]))

    # marking initial revision scores
    # adjusting revision scores with user reputation scores
    for e in revisions:
        e.rev_score_info = user_reputations[e.username];
        if(e.reverts_info == -2):      e.rev_score_info -= 2     # reverted
        elif(e.reverts_info == -5):    e.rev_score_info = -5      # self-reverted
        elif(e.reverts_info < -2):     e.rev_score_info -= 1     
        elif(e.reverts_info > -1):     e.rev_score_info += 1

    #for i, e in enumerate(edit_info):
    #    wikipedia.output(">>>  Revision %d (%s, %s) by %s(%s): %s %s : \03{lightblue}%s\03{default}   <<< " %   \
    #                     (i, mark(reverts_info[i], lambda x:x>-2), mark(rev_score_info[i], lambda x:x>-1), e.username,  \
    #                        mark(user_reputations[e.username], lambda x:x>-1), e.utc, e.size, e.comment))

    return user_reputations



def mark(value, function):
    if(function(value)): 
        return "\03{lightgreen}%s\03{default}" % value
    return "\03{lightred}%s\03{default}" % value

def urri(ri):
    if(ri > -1): return 'revert'
    return ('self_revert', 'revert_war', 'questionable', 'reverted', 'regular')[ri]

def show_diff(e):
        text = "";
        marker = [' *', 
                  ' +', ' ++', ' +++', ' ++++', ' +++++',
                  ' -----', ' ----', ' ---', ' --', ' -']
        for (t, v) in e.diff:
            if(v > 5): v = 5
            elif(v < -5): v = -5
            text += mark(marker[v] + t, lambda x:x[1]=='-');

        wikipedia.output(text)
        wikipedia.output("Old: %s lines. New: %s lines." % (e.al, e.bl))
        wikipedia.output("Added: %d lines, %d words" % (e.ilA, e.iwA))
        wikipedia.output("Removed: %d lines, %d words" % (e.ilR, e.iwR))
        wikipedia.output("Diff position: lo = %d, ahi = %d, bhi = %d" % (e.lo, e.ahi, e.bhi))



def collect_stats(stats, ids, user_reputations, e, prev, score, uncertain, extra):
    global _retrain_arg, _train_arg, _human_responses
    score_numeric = e.rev_score_info                   
    revid = e.revid
    known = k.is_verified_or_known_as_good_or_bad(revid)    # previous score (some human verified)
    verified = k.is_known_as_verified(revid)                # if not Empty: human verified
    # if the retrain arg is set to true, username or the revision id
    retrain = (_retrain_arg == True) or (_retrain_arg and ((_retrain_arg.find(e.username) > -1) or (_retrain_arg.find(str(revid)) > -1)))

    if(score != known or (not verified and uncertain) or retrain):
        wikipedia.output("\n\n\n\n\n\n\n >> R%d (%s, %s) by %s(%s): \03{lightblue}%s\03{default}   <<< " %   \
             (e.i, mark(e.reverts_info, lambda x:x!=-2), mark(score_numeric, lambda x:x>-1), e.username, \
                mark(user_reputations[e.username], lambda x:x>-1), e.comment))
        wikipedia.output("Score is %s." % mark(score, lambda x:x=='good'))
        if(known): wikipedia.output("Known as %s." % mark(known, lambda x:x=='good'))
        if(verified): wikipedia.output("Verified as %s." % mark(verified, lambda x:x[:3]!='bad'))
        if(uncertain): wikipedia.output("Uncertain: %s" % uncertain)
        wikipedia.output("Diff: http://en.wikipedia.org/w/index.php?diff=%d" % revid)
        if(k.info(revid)): wikipedia.output("Annotation: %s" % (k.info(revid)))
        if(_verbose_arg): show_diff(e)
        if(extra): extra()

        # uncertain = score_numeric < 1 or reverts_info[i] != -1 or uncertain
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
            _human_responses += 1
        else:
            if(not verified): known = score

    # Collecting stats
    ids[known].append(revid)
    stats['Revision analysis score ' + score + ' on known'][known] += 1
    if(verified):
        ids[verified].append(revid)
        stats['Revision analysis score ' + score + ' on verified'][verified] += 1

    if(_human_responses > 5):
        _human_responses = 0
        dump_cstats(stats, ids)

    return (verified, known, score)



def check_reputations(revisions, user_reputations):

    if(not user_reputations):
        user_reputations = defaultdict(int)
        for e in revisions:
            known = k.is_verified_or_known_as_good_or_bad(e.revid)    # previous score (some human verified)
            if(known == 'good'): user_reputations[e.username] += 1
            if(known == 'bad'): user_reputations[e.username] -= 1
    
    prev = None;
    for e in revisions:
        if prev:
            revid = e.revid
            known = k.is_verified_or_known_as_good_or_bad(revid)    # previous score (some human verified)
            verified = k.is_known_as_verified(revid)                # if not Empty: human verified
            reputation = user_reputations[e.username]
            if not known: continue
            
            if(e.reverts_info == -5):                               # inverse for self-reverts
                score = ('bad', 'good')[reputation < 0]
            else:
                score = ('good', 'bad')[reputation < 0]
        
            # Collecting stats and Human verification
            (verified, known, score) = collect_stats(stats, ids, user_reputations, e, prev, score, False, None)
        prev = e;



def analyse_maxent(revisions, user_reputations):
    # apt-get apt-get install python-numpy python-scipy
    import numpy as np
    from scipy import stats

    # NLTK, the Natural Language Toolkit
    # Note: requires http://code.google.com/p/nltk/issues/detail?id=535 patch
    import nltk, maxent, megam
    # from nltk.classify import maxent, megam


    # download and extract megam_i686.opt from http://www.cs.utah.edu/~hal/megam/
    megam.config_megam('./megam_i686.opt')

    # Tracking blankings and near-blankings
    # Establishing user ratings for the user whitelists
    user_features = defaultdict(lambda: defaultdict(int))           # TODO: optimize!
    edit_features = [None] * len(revisions)                         #

    def add_feature(f):
        edit_features[i][f] = 'present'

    def add_uefeature(f):
        #user_features[e.username]['U' + f] += 1
        edit_features[i][f] = 'present'

    total_time = total_size = 0
    prev = revisions[0]
    for i, e in enumerate(revisions):
        edit_features[i] = {}
        t = """
        if(e.size * i < total_size):                                        # new page is smaller than the average
            add_uefeature('smaller_than_average')
            if(e.reverts_info == -2):                                       # and it was reverted
                add_uefeature('smaller_and_reverted')

        if(e.size < prev.size):   edit_features[i]['smaller %'] = float(prev.size - e.size) * i * 100 / total_size
        elif(e.size > prev.size): edit_features[i]['larger %'] = float(e.size - prev.size) * i * 100 / total_size
 

        if(e.size < prev.size): add_uefeature('smaller')
        elif(e.size > prev.size): add_uefeature('larger')
        else: add_uefeature('same_size')

        if(e.username != prev.username): 
            add_uefeature(urri(e.reverts_info))
        else: 
            add_uefeature('same_user')
            add_uefeature('same_' + urri(e.reverts_info))

        delta_utc = e.utc - prev.utc                                        # prev edition has managed longer than usual
        if(delta_utc * i > total_time): add_uefeature('accepted')
        """
        comment_revert = False
        
        if(e.username.lower().find('bot') > -1):
            add_uefeature('bot')
        elif(e.comment):
            if(e.comment[-2:] == '*/'): add_uefeature('comment_sec_no')
            elif(e.comment[:8] == '[[WP:AES'): add_uefeature('comment_wp_AES')
            elif(e.comment[:9] == '[[WP:UNDO'): add_uefeature('comment_wp_UNDO'); comment_revert = True
            elif(e.comment[:8] == '[[WP:RBK'): add_uefeature('comment_wp_RBK'); comment_revert = True
            elif(e.comment[:7] == '[[Help:'): add_uefeature('comment_wp_Help'); comment_revert = True
            elif(e.comment[:5] == '[[WP:' or e.comment[:7] == '[[Help:'):
                ii = e.comment.find(']]', 5, 32)
                if(ii > 0): add_uefeature('comment_wp_' + e.comment[5:ii])               
            elif e.comment[:6] == 'Revert': add_feature('comment_revert'); comment_revert = True
            elif e.comment[:5] == 'Undid': add_feature('comment_undid'); comment_revert = True
            elif e.comment[:3] == 'rvv': add_feature('comment_rvv'); comment_revert = True
            elif e.comment[:3] == 'rev': add_feature('comment_rev'); comment_revert = True
            elif e.comment[:2] == 'rv': add_feature('comment_rv'); comment_revert = True
            elif e.comment[:4] in ('BOT ', 'bot ', 'robo', 'Robo'): add_feature('comment_bot')
            elif e.comment[:3] == 'cat': add_feature('comment_cat')
            elif e.comment[:1] == '+': add_feature('comment_plus')
            elif e.comment.find('spam') > -1: add_feature('comment_spam'); 
            elif e.comment.find('ref') > -1: add_feature('comment_ref'); # print '%30s\t%s' % (e.username, e.comment)
            else:
                # print '%30s\t%s' % (e.username, e.comment)
                # add_feature('comment')
                if(len(e.comment.split()) > 7): add_uefeature('comment_long')
                #for token in e.comment.split():
                #    edit_features[i][token] = 'comment'
            
        else: add_uefeature('no_comment')
        
        if comment_revert and e.reverts_info == -1:
            print '%30s\t%s' % (e.username, e.comment)
            wikipedia.output("Diff: http://en.wikipedia.org/w/index.php?diff=%d\n\n" % e.revid)
            

        total_size += e.size
        total_time += (e.utc - prev.utc)
        prev = e

    # for v in xrange(1,100): print v, math.trunc(math.log(math.sqrt(i))*2*math.pi)
    # for uf in user_features.values():
    #    for f, v in uf.iteritems():
    #        uf[f] = math.log(v)
            
    
    #pp = pprint.PrettyPrinter(width=140)
    #for u, uf in user_features.iteritems():    
    #    wikipedia.output("user %s(%s) features = \\\n%s" % (u, mark(user_reputations[u], lambda x:x>-1), pp.pformat(uf)))

    train = [None] * len(edit_features)
    for i, features in enumerate(edit_features):
        e = revisions[i]
        known = k.is_verified_or_known_as_good_or_bad(e.revid)              # previous score (some human verified)
        if known == None: wikipedia.output("Unknown revision %d" % e.revid); known = 'good'
        for f, v in user_features[e.username].iteritems():
            features[f] = v        
        train[i] = (features, known)

    #for i in reversed(xrange(1, len(edit_features))):
    #    for f, v in edit_features[i-1].iteritems():
    #        edit_features[i]['PREV' + f] = v

    #for i in xrange(len(edit_features) - 1):
    #    for f, v in edit_features[i+1].iteritems():
    #        edit_features[i]['NEXT' + f] = v

   
    megam.config_megam('./megam_i686.opt')
    enc = maxent.TypedMaxentFeatureEncoding.train(train, alwayson_features=True)
    
    #for fs in train:
    #    s = "";
    #    for f, v in fs[0].iteritems(): s += " : %s = %4s " % (f, v)
    #    print("Featureset", s, " Class: ", fs[1] , "Encoding is: ", enc.encode(fs[0], fs[1]))


    classifier = maxent.MaxentClassifier.train(train, algorithm='megam', encoding=enc, \
                    bernoulli=False, trace=2, tolerance=2e-5, max_iter=1000, min_lldelta=1e-7)
    classifier.show_most_informative_features(n=50)

    ids = defaultdict(list)
    stats = defaultdict(lambda:defaultdict(int))
    for i, e in enumerate(revisions):
        known = k.is_verified_or_known_as_good_or_bad(e.revid)              # previous score (some human verified)
        verified = k.is_known_as_verified(e.revid)                          # if not Empty: human verified        
        features = edit_features[i]
        
        for f, v in user_features[e.username].iteritems():
            features[f] = v
        pdist = classifier.prob_classify(features)
        score = ('bad', 'good')[pdist.prob('good') > pdist.prob('bad')]
        
        
        # Collecting stats and Human verification
        uncertain = known != score
        score_numeric = e.rev_score_info
        extra = lambda: classifier.explain(features);
        #(verified, known, score) = collect_stats(stats, ids, user_reputations, e, prev, score, uncertain, extra)
        stats['Revision analysis score ' + score + ' on known'][known] += 1
    dump_cstats(stats, ids)



def analyse_crm114(revisions, user_reputations):
    # stats
    ids = defaultdict(list)
    stats = defaultdict(lambda:defaultdict(int))
 
    p = re.compile(r'\W+')
    # p = re.compile(r'\s+')

    # CRM114
    c = crm114.Classifier( "data", [ "good", "bad" ] ) 
    i = 0
    prev = None
    for i, e in enumerate(revisions):
        score_numeric = e.rev_score_info                   
        score = ('good', 'bad')[score_numeric < 0]              # current analyse_reverts score
        revid = e.revid
        known = k.is_verified_or_known_as_good_or_bad(revid)    # previous score (some human verified)
        verified = k.is_known_as_verified(revid)                # if not Empty: human verified

        #wikipedia.output("Revision %d (%d): %s by %s Comment: %s" % (i, score, e.timestamp, e.username, e.comment))
        if prev:
            diff_time = e.utc - prev.utc
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
            #if(e.editRestriction): edit.append("ELFeditRest")
            #if(e.moveRestriction): edit.append("ELFmoveRest")
            #edit.append(e.redirect)
            if(e.comment):
                edit.append('ELFcomment')
                edit.append(e.comment)
            else: edit.append('ELFnoComment')

            for (t, v) in e.diff:
                if(v > 0): edit.append('+' + t)
                elif(v < 0): edit.append('-' + t)

            if(e.md5 and prev.md5): edit.append('ELFnotblank')
            elif(e.md5 and not prev.md5): edit.append('ELFrevblank')
            elif(prev.md5 and not e.md5): edit.append('ELFblanking')
            else: edit.append('ELFblank')
            
            edit_text = ' '.join(edit)
            #wikipedia.output(edit_text);
            
            # Run CRM114
            (crm114_answer, probability) = c.classify(edit_text.encode('utf-8'))

            # CRM114 different or uncertain
            if(crm114_answer == 'bad' and score == 'good'): 
                falseString = " >>> \03{lightpurple}FALSE POSITIVE\03{default} <<<"
                uncertain = "CRM114 thinks it is: %s, prob was:%f %s" % (mark(crm114_answer, lambda x:x=='good'), probability, falseString)
            elif(crm114_answer == 'good' and score == 'bad'): 
                falseString = "  >>> \03{lightpurple}False Negative\03{default} <<<"
                uncertain = "CRM114 thinks it is: %s, prob was:%f %s" % (mark(crm114_answer, lambda x:x=='good'), probability, falseString)
            else: uncertain = ""
            
            # Collecting stats and Human verification
            extra = lambda:wikipedia.output(" \03{lightblue}%s\03{default}" % edit_text)
            (verified, known, score) = collect_stats(stats, ids, user_reputations, e, prev, score, uncertain, extra)

            if(i > 500):
                stats['CRM114 answered ' + crm114_answer + ' on known'][known] += 1
                stats['CRM114 answered ' + crm114_answer + ' on score'][score] += 1

            # training CRM114
            if(probability < 0.75 or crm114_answer != known):
                c.learn(known, edit_text.encode('utf-8'))
                stats['CRM114 trained'][known] += 1
                # wikipedia.output("\03{lightpurple}Training %s\03{default}", known)
            if(i % 100 == 0): wikipedia.output("Processed %d revisions" % i)

        prev = e
    dump_cstats(stats, ids)    


# some low hanging text statistics
reU = re.compile("[A-Z]")
reL = re.compile("[a-z]")
reES = re.compile("!")
reHI = re.compile("(hi |penis|fuck)", re.I)
reI = re.compile("i ", re.I)
def comment_score(text):
    uN = len(reU.findall(text))
    lN = len(reL.findall(text))
    esN = len(reES.findall(text))

    if(uN > 5 and lN < uN):                         # uppercase stats is looking bad
        return -1
    if(esN > 2):
        return -1
    if(reHI.search(text) != None):
        return -1
    if(reI.search(text) != None):
        return 0

    return 1





def analyse_decisiontree(revisions, user_reputations):
    total_time = total_size = 0
    prev = None;
    
    for e in revisions:
        known = k.is_verified_or_known_as_good_or_bad(e.revid)  # previous score (some human verified)
        score = 0

        if(e.comment):
            if(e.comment[:5] == '[[WP:'):
                if(e.comment[:17] == u'[[WP:AES|←]]Undid'): score += 100
                elif(e.comment[:19] == u'[[WP:AES|←]]Blanked'): score -= 100
                elif(e.comment[:20] == u'[[WP:AES|←]]Replaced'): score -= 100
                elif(e.comment[:20] == u'[[WP:AES|←]] Blanked'): score -= 100
                elif(e.comment[:21] == u'[[WP:AES|←]] Replaced'): score -= 100
                elif(e.comment[:41] == u'[[WP:Automatic edit summaries|←]]Replaced'): score -= 100 
                else: score += 10
            elif(e.comment[-2:] == '*/'):
                score -= 1
            else:
                score += comment_score(e.comment)
        else:
            score -= 1
                

        if(e.reverts_info == -2):        score -= 1
        elif(e.reverts_info == -1):      score += 2

        if(not e.ipedit): score += 1
        else:         score -= 1

        if(e.ilR > e.ilA and e.iwR > 1):                    # and new page is smaller than the previous
            score -= 1
        if(e.iwR == 50):                                    # large scale removal
            score -= 1            

        if score > 1:       user_reputations[e.username] += 1;  score = 'good'
        elif score < -10:   user_reputations[e.username] -= 1;  score = 'bad'
        elif(e.reverts_info == -2):
            if(score < 0):  user_reputations[e.username] -= 1;  score = 'bad'
            else: continue
        else: continue
        if(not known): continue
        (verified, known, score) = collect_stats(stats, ids, user_reputations, e, prev, score, False, None)

    #for e in revisions:
    #    if(user_reputations[e.username] > 0): score = 'good'
    #    elif(user_reputations[e.username] < 0): score = 'bad'
    #    else: continue
    #    (verified, known, score) = collect_stats(stats, ids, user_reputations, e, prev, score, False, None)
    # dump_cstats(stats, ids)


def compute_reputations_dictionary():
    user_reputations = defaultdict(int)

    if(_output_arg):
        FILE = open(_output_arg, 'wb')

    total_pages = 0; total_revisions = 0; start = time.time();
    for revisions in read_pyc():
        analyse_reverts(revisions)
        analyse_decisiontree(revisions, user_reputations)
        total_pages += 1;
        total_revisions += len(revisions)

        if(total_pages%100 == 0):
            wikipedia.output("Page %d. Revisions %d. Users %s. Analysis time: %f. ETA %f Hours." %
                (total_pages, total_revisions, len(user_reputations), time.time() - start,
                (NNN - total_revisions) / total_revisions * (time.time() - start) / 3600 ))

            for u, r in user_reputations.iteritems():
                marshal.dump((u, r), FILE)
            user_reputations = defaultdict(int)

    if(_output_arg):
        for u, r in user_reputations.iteritems():
            marshal.dump((u, r), FILE)

def compute_reputations_shelve():
    user_reputations = defaultdict(int)

    if(_output_arg):
        rdb = shelve.open(_output_arg)

    total_pages = 0; total_revisions = 0; start = time.time();
    for revisions in read_pyc():
        analyse_reverts(revisions)
        analyse_decisiontree(revisions, user_reputations)
        total_pages += 1;
        total_revisions += len(revisions)

        if(total_pages%100 == 0):
            wikipedia.output("Page %d. Revisions %d. Users %s. Analysis time: %f. ETA %f Hours." %
                (total_pages, total_revisions, len(user_reputations), time.time() - start,
                 (NNN - total_revisions) / total_revisions * (time.time() - start) / 3600 ))

            for u, r in user_reputations.iteritems():
                ue = u.encode('utf-8')
                rdb[ue] = rdb.setdefault(ue, 0) + r

            user_reputations = defaultdict(int)


    if(_output_arg):
        for u, r in user_reputations.iteritems():
            ue = u.encode('utf-8')
            rdb[ue] = rdb.setdefault(ue, 0) + r
        rdb.close()





def main():
    global _retrain_arg, _train_arg, _human_responses, _verbose_arg, _output_arg, _pyc_arg, _reputations_arg
    pattern_arg = None; _pyc_arg = None; _display_last_timestamp_arg = None; _compute_pyc_arg = None;
    _display_pyc_arg = None; _compute_reputations_arg = None;_output_arg = None; _analyze_arg = None
    _reputations_arg = None; _username_arg = None; _filter_pyc_arg = None; _export_arg = None
    for arg in wikipedia.handleArgs():
        if arg.startswith('-xml') and len(arg) > 5: pattern_arg = arg[5:]
        if arg.startswith('-pyc') and len(arg) > 5: _pyc_arg = arg[5:]
        if arg.startswith('-reputations') and len(arg) > 13: _reputations_arg = arg[13:]
        if arg.startswith('-username') and len(arg) > 10: _username_arg = arg[10:]
        if arg.startswith('-retrain'): _retrain_arg = True
        if arg.startswith('-filter-pyc'): _filter_pyc_arg = True
        if arg.startswith('-retrain') and len(arg) > 9: _retrain_arg = arg[9:]
        if arg.startswith('-train'): _train_arg = True
        if arg.startswith('-vvv'): _verbose_arg = True
        if arg.startswith('-output') and len(arg) > 8: _output_arg = arg[8:]
        if arg.startswith('-display-last-timestamp'): _display_last_timestamp_arg = True
        if arg.startswith('-compute-reputations'): _compute_reputations_arg = True
        if arg.startswith('-compute-pyc'): _compute_pyc_arg = True
        if arg.startswith('-display-pyc'): _display_pyc_arg = True
        if arg.startswith('-analyze'): _analyze_arg = True
        if arg.startswith('-export'): _export_arg = True
 
    if(_export_arg):
        special_export()
        return

    if(not pattern_arg and not _pyc_arg):            # work: lightblue lightgreen lightpurple lightred
        wikipedia.output('Usage: ./r.py \03{lightblue}-xml:\03{default}path/Wikipedia-Dump-*.xml.7z -output:Wikipedia-Dump.full -compute-pyc')
        wikipedia.output('     : ./r.py \03{lightblue}-pyc:\03{default}path/Wikipedia-Dump.full -analyze')
        return

    if(pattern_arg):        # XML files input
        xmlFilenames = sorted(locate(pattern_arg))
        wikipedia.output(u"Files: \n%s\n\n" % xmlFilenames)
        mysite = wikipedia.getSite()

    if(_display_last_timestamp_arg): display_last_timestamp(xmlFilenames); return
    if(_compute_pyc_arg): compute_pyc(xmlFilenames); return


    # Precompiled .pyc (.full) files input
    if(_display_pyc_arg): display_pyc(); return
    if(_filter_pyc_arg): filter_pyc(); return
    if(_compute_reputations_arg):
        compute_reputations_dictionary()
        #compute_reputations_shelve()

    if(_reputations_arg):
        user_reputations = read_reputations()
        if(_username_arg): 
            wikipedia.output("User %s, has_key %s, reputation %s" %
                (_username_arg, user_reputations.has_key(_username_arg), user_reputations[_username_arg]))


    #analyse_tokens_lifetime(xmlFilenames)

    global ids, stats
    ids = defaultdict(list)
    stats = defaultdict(lambda:defaultdict(int))

    N = 0; start = time.time();
    if(_analyze_arg):
        for revisions in read_pyc():
            analyse_reverts(revisions)
            #user_reputations = analyse_reputations(revisions)
            if(not N%100): wikipedia.output("Reputation analysis time: %f, N = %d" % (time.time() - start, N))
            N += 1

            analyse_decisiontree(revisions, user_reputations)
            #check_reputations(revisions, user_reputations)
            #analyse_maxent(revisions, user_reputations)
            #analyse_crm114(revisions, user_reputations)
        dump_cstats(stats, ids)


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

