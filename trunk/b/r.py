#!/usr/bin/python
# -*- coding: utf-8  -*-

# How comes rep["217.42.224.103"] = -1???


# Use article total revisions number as a feature (popular/unpopular)
# Use article protected status



#retrain BAD: 167750423, 285306288

# 167750423

# TODO:
# consecutive edits as one edit
# self-reverts: reverted edit is bad. no karma change.
# tokens lifetime - use relative lifetime
# switch to F1-score

# User karma - tuples (+, -) - how often '+' do '-'
# Try to produce 'string' karma "er eeer es es", "eee ceeee e e e e "


# Users with bad karma can do good edits:
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

# Edit by:  vandal, regular
# Whose edit was it:  self, other user

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

# for v in xrange(1,100): print v, math.trunc(math.log(math.sqrt(i))*2*math.pi)


# ==================================================================================
# belief propagation
#
# (user karma) -> {edit, edit, edit}
#        negative for self-reverts
#
# (user karma) -> {previous edit, previous edit}
#           negative for reverts
#
# edit -> user karma
#

# 1) Mark edits based on heuristics
# 2) Calculate karma based on heuristics
# 3) Mark edits based on karma
# 4) Adjust karma
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

import re, sys, time, calendar, difflib, string, math, hashlib, os, fnmatch, marshal, cPickle
import pprint, ddiff
from collections import defaultdict, namedtuple
from ordereddict import OrderedDict

# pywikipedia (trunk 2010/03/15) in your PYTHONPATH, configured and running
import wikipedia, pagegenerators, xmlreader, editarticle


# CRM114, crm.py module by Sam Deane
import crm114   

#import wicow08r_chin_microsoft_annotation as k
#import wicow08r_chin_lincoln_annotation as k
#import pan10_vandalism_test_collection as k

from labels import k, ids, labels, labels_shortcuts, labeler, good_labels, bad_labels
import pan_wvc_10_gold; k.append(known = pan_wvc_10_gold.g, info = pan_wvc_10_gold.i);
#import pan_wvc_10_labels; k.append(verified = pan_wvc_10_labels.verified)#, known = pan_wvc_10_labels.known)
import pan_wvc_10_labels_15k as pan_wvc_10_labels; k.append(verified = pan_wvc_10_labels.verified)#, known = pan_wvc_10_labels.known)
import wrdse10_dchichkov_rocket_annotations as wrdse; k.append(known = wrdse.known, verified = wrdse.verified);

NNN = 313797035 # total revisions in the latest wiki dump
counters_dict = lambda:defaultdict(lambda:(0, 0, 0, 0, 0, 0, 0, 0))
good_counter = lambda x:x[-2]*5<x[0]

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


def dump_cstats(stats):
    if(_verbose_arg): ids.dump() 
    wikipedia.output("===================================================================================")
    wikipedia.output("stats = \\\n%s" % pprint.PrettyPrinter(width=140).pformat(stats))
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
    __slots__ = ('i', 'reverts_info', 'rev_score_info', 'duplicates_info', 'reverted', 'edit_group', 'oldid',
                 
                 'id', 'revid', 'username', 'comment', 'title', 'size', 'utc', 'md5', 'ipedit',
                 'editRestriction', 'moveRestriction', 'isredirect',
                 'al', 'bl', 'lo', 'ahi', 'bhi', 'ilA', 'ilR', 'iwA', 'iwR', 'ilM', 'iwM', 'diff'
                  )

    def __init__(self, args):
        (self.id, self.revid, self.username, self.comment, self.title,
        self.size, self.utc, self.md5, self.ipedit,
        self.editRestriction, self.moveRestriction, self.isredirect,
        self.al, self.bl, self.lo, self.ahi, self.bhi,
        self.ilA, self.ilR, self.iwA, self.iwR, self.ilM, self.iwM, self.diff) = args

        self.reverts_info = -1
        self.rev_score_info = 0
        self.duplicates_info = None
        self.reverted = None
        self.edit_group = []
        self.oldid = None


class EmptyFullInfoPlaceholder(object):
    def __init__(self):
        self.username = None
        self.edit_group = None
        self.revid = None
        




def read_pyc_count_empty():
    wikipedia.output("Reading %s..." % _pyc_arg)
    FILE = open(_pyc_arg, 'rb')
    start = time.time()
    total_revisions = 0; empty_revisions = 0;
    try:
        while True:
            e = FullInfo(marshal.load(FILE))     # load first in order to
            if(e.size == 0 and e.comment and e.comment[:2] == '/*' and not e.ipedit): 
                title = None; 
                if e.title: title =  e.title.encode('utf-8');
                empty_revisions += 1; print("%d,%d,%s,%s" % (e.id, e.revid, e.utc, title))
            total_revisions += 1

            if(total_revisions%100000 == 0):
                RPS = total_revisions / (time.time() - start);
                wikipedia.output("Revisions %d. Empty Revisions %d. Analysis time: %f. ETA %f Hours." %
                    (total_revisions, empty_revisions, time.time() - start,
                    (NNN - total_revisions) / RPS / 3600 ))

    except IOError, e:
        raise
    except EOFError, e:
        wikipedia.output("Done reading %s. Read time: %f." % (_pyc_arg, time.time() - start))

    wikipedia.output("Revisions %d. Empty Revisions %d. Analysis time: %f. ETA %f Hours." %
         (total_revisions, empty_revisions, time.time() - start,
         (NNN - total_revisions) / total_revisions * (time.time() - start) / 3600 ))



def read_pyc():
    pycFilenames = sorted(locate(_pyc_arg))
    wikipedia.output(u"Files: \n%s\n\n" % pycFilenames)

    for pycFilename in pycFilenames:
        wikipedia.output("Reading %s..." % pycFilename)
        FILE = open(pycFilename, 'rb')
        start = time.time(); size = os.path.getsize(pycFilename); show_progress = time.time() + 15
        revisions = [];
        try:
            info = FullInfo(marshal.load(FILE))     # load first in order to  
            if(info.utc > 1258329600): continue     # filter date < Mon, 16 Nov 2009 00:00:00 GMT
            id = info.id;                           # initialize id from info.id
            revisions.append(info)
            while True:
                info = FullInfo(marshal.load(FILE))
                if(info.utc > 1258329600): continue     # filter date < Mon, 16 Nov 2009 00:00:00 GMT
                if(id != info.id):
                    yield revisions
                    revisions = []
                    id = info.id

                    if(time.time() > show_progress):
                        DT = (time.time() - start) / 3600; BPH = FILE.tell() / DT; show_progress = time.time() + 15
                        wikipedia.output("DT %f Hours, ETA %f Hours." % (DT, (size/BPH - DT)) )

                revisions.append(info)
        except IOError, e:
            raise
        except EOFError, e:
            wikipedia.output("Done reading %s. Read time: %f." % (pycFilename, time.time() - start))

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
            known = k.is_known(e.revid)
            if known: break
        if not known: continue

        # mark 'known'
        for e in revisions:
            known = k.is_known(e.revid)
            if known: k.g[e.revid] = 'known'

        for e in revisions:
            full_info = (e.id, e.revid, e.username, e.comment, e.title,
                e.size, e.utc, e.md5, e.ipedit,
                e.editRestriction, e.moveRestriction, e.isredirect,
                e.al, e.bl, e.lo, e.ahi, e.bhi,
                e.ilA, e.ilR, e.iwA, e.iwR, e.ilM, e.iwM, e.diff)
            marshal.dump(full_info, FILE)
            filtered_revisions += 1
        filtered_pages += 1

    l = []
    for e, v in k.g.iteritems():
        if v != 'known': l.append(e)
    
    # print "Known list:", k.g
    print "Missing list", sorted(l)
    print "Known revisions: ", len(k.g)
    print "Missing revisions total: ", len(l)
    print "Filtered pages: ", filtered_pages, "Filtered revisions", filtered_revisions


def referenced_users(revisions):
    """Returns the list of referenced in the revisions users"""
    users = {}
    for e in revisions:
        users[e.username] = True
        if e.reverted: users[e.reverted.username] = True
        for g in e.edit_group:
            users[g.username] = True
            if g.reverted: users[e.reverted.username] = True    
    


def read_counters(revisions):
    """Read/Merge/Filter user counters. 
    If _output_arg global is provided, counters will be merged and saved;
    If revisions argument is provided only referenced users revisions will be saved;"""
    
    wikipedia.output("Reading %s..." % _counters_arg)
    FILE = open(_counters_arg, 'rb')
    user_counters = counters_dict()
    start = time.time()
    try:
        if _output_arg:                                 # read and merge
            if revisions:                               
                users = referenced_users(revisions)          # filter / known users
                            
            while True:
                (u,r) = marshal.load(FILE)
                if not revisions or u in referenced_users:
                    user_counters[u] = tuple([a+b for (a,b) in zip(user_counters[u] , r)])
        else:                                           
           while True:                                  # just read
               (u,r) = marshal.load(FILE)
               user_counters[u] = r

    except IOError, e:
        raise
    except EOFError, e:
        wikipedia.output("Done reading %s. Read time: %f. Total users: %d" % (_counters_arg, time.time() - start, len(user_counters)))
    if(_output_arg):
        #wikipedia.output("Filtering counters <0 or >10")
        FILE = open(_output_arg, 'wb')
        for u, r in user_counters.iteritems():
            # if(r < 0 or r > 10):
            marshal.dump((u, r), FILE)
    return user_counters




def display_last_timestamp(xmlFilenames):
    total_revisions = 0
    for xmlFilename in xmlFilenames:
        revisions = xmlreader.XmlDump(xmlFilename, allrevisions=True).parse()
        for e in revisions:
            total_revisions += 1
    
    wikipedia.output("Total revision analyzed: %d" % total_revisions)
    if(total_revisions): wikipedia.output("Timestamp of the last revision: %s" % e.timestamp)
    


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

    # Marking duplicates_info:
    #   None: regular revision
    #   [revid, revid, ]: this revision is a duplicate of
    for m, indexes in rev_hashes.iteritems():
        if len(indexes) > 1:
            for i in indexes:
                revisions[i].duplicates_info = indexes

    # Marking (-2, -4, >=0)
    # -2 : between duplicates, by single user (reverted, most likely bad)
    # -4 : between duplicates, (revert that was reverted. revert war.)
    # ------------------------------------------------------------------
    # Revision 54 (-1)      User0    Regular edit
    # Revision 55 (55)      User1    Regular edit
    # Revision 56 (-2)      User2    Vandalism
    # Revision 57 (-2)      User2    Vandalism
    # Revision 58 (-2)      User3    Correcting vandalism, but not quite
    # Revision 59 (55)      User4    Revert to Revision 55

    revert = None
    for e in reversed(revisions):
        if revert != None:
            if not e.duplicates_info:                           # regular reverted revision
                e.reverts_info = -2      
                e.reverted = revert
            elif e.i == revert.duplicates_info[0]:              # reached reverted_to[0]
                e.reverts_info = e.i                            # LEGACY 
                revert = None
            elif e.duplicates_info != revert.duplicates_info:   # revert war, revision has duplicates and was reverted 
                e.reverts_info = -4 
                e.reverted = revert
            else:
                revert = e
                e.reverts_info = revert.duplicates_info[0]      # LEGACY 
        elif e.duplicates_info:
            if e.i == e.duplicates_info[0]:
                e.reverts_info = e.i                            # LEGACY 
                revert = None
            else:                 
                revert = e
                e.reverts_info = revert.duplicates_info[0]      # LEGACY
                    

    # Marking (-3) : between duplicates, by other users (reverted, questionable)
    # Revision 54 (-1)  ->   (-1)                User0    Regular edit
    # Revision 55 (55)  ->   (55)                User1    Regular edit
    # Revision 56 (-2)  ->   (-2)                User2    Vandalism
    # Revision 57 (-2)  ->   (-2)                User2    Vandalism
    # Revision 58 (-2)  ->   (-3)                User3    Correcting vandalism, but not quite
    # Revision 59 (55)  ->   (55)                User4    Revert to Revision 55

    # Marking (-5) : self-reverts
    # Revision 54 (-1)  ->   (-1)                User0    Regular edit
    # Revision 55 (55)  ->   (55)                User1    Regular edit
    # Revision 56 (-2)  ->   (-2)                User1    Self-reverted edit
    # Revision 59 (55)  ->   (55)                User4    Revert to Revision 55
         
    username = None; prev = EmptyFullInfoPlaceholder();
    for e in revisions:
        if(e.reverts_info == -2):
            if(e.username == e.reverted.username): e.reverts_info = -5
            if(username == None): username = e.username
            elif (username != e.username): e.reverts_info = -3
        else: username = None

        # Filling oldid
        e.oldid = prev.revid

        # Marking edit groups: consequent edits by a single user
        if prev.username == e.username:
            prev.edit_group.append(prev)  
            e.edit_group = prev.edit_group
        elif prev.edit_group:
            prev.edit_group.append(prev)
        prev = e        





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
            user_reputations[prev.username] += 1

        if(e.comment and len(e.comment) > 80):        # we like long comments. TODO
            user_reputations[e.username] += 1
            
        total_size += e.size
        total_time += (e.utc - prev.utc)
        prev = e

    # marking initial revision scores
    # adjusting revision scores with user karma scores
    for e in revisions:
        e.rev_score_info = user_reputations[e.username];
        if(e.reverts_info == -2):      e.rev_score_info -= 2     # reverted
        elif(e.reverts_info == -5):    e.rev_score_info = -5      # self-reverted
        elif(e.reverts_info < -2):     e.rev_score_info -= 1     
        elif(e.reverts_info > -1):     e.rev_score_info += 1

    return user_reputations



def mark(value, function = None):
    if(not function):
        if value == 'good' or value in good_labels:  return "\03{lightgreen}%s\03{default}" % unicode(value)
        if value == 'bad' or value in bad_labels: return "\03{lightred}%s\03{default}" % unicode(value)
        return "\03{lightpurple}%s\03{default}" % unicode(value)

    if(function(value) == True): return "\03{lightgreen}%s\03{default}" % unicode(value)
    if(function(value) == False): return "\03{lightred}%s\03{default}" % unicode(value)
    return "\03{lightpurple}%s\03{default}" % unicode(value)


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

def show_edit(e, prefix):
    wikipedia.output("%s %d (%s) by %s: \03{lightblue}%s\03{default}  Diff: http://en.wikipedia.org/w/index.php?diff=%d <<< " %   \
     (prefix, e.i, mark(e.reverts_info, lambda x:x!=-2), e.username, e.comment, e.revid))

def collect_stats(stats, user_counters, e, score, uncertain, extra):
    global _retrain_arg, _train_arg, _human_responses
    score_numeric = e.rev_score_info                   
    revid = e.revid
    known = k.is_known(revid)                       # previous score (some human verified)
    verified = k.is_verified(revid)                 # if not Empty: human verified
    # if the retrain arg is set to true, username or the revision id
    retrain = (_retrain_arg == True) or (_retrain_arg and ((_retrain_arg.find(e.username) > -1) or (_retrain_arg.find(str(revid)) > -1)))

    if((_verbose_arg and (score != known or (not verified and uncertain))) or retrain):
        wikipedia.output("\n\n\n\n\n\n\n >> R%d (%s, %s) by %s(%s): \03{lightblue}%s\03{default}  Diff: http://en.wikipedia.org/w/index.php?diff=%d <<< " %   \
             (e.i, mark(e.reverts_info, lambda x:x!=-2), mark(score_numeric, lambda x:x>-1), e.username, \
                mark(user_counters[e.username], good_counter), e.comment, revid))
        if(e.reverted): show_edit(e.reverted, "Reverted:")
        if(e.edit_group):
            for edit in e.edit_group: show_edit(edit, "Edit Group:")
            wikipedia.output("Edit Group Diff: http://en.wikipedia.org/w/index.php?diff=%d&oldid=%d" % (e.edit_group[-1].revid, e.edit_group[0].oldid))    
        wikipedia.output("Score is %s." % mark(score))
        if(known): wikipedia.output("Known as %s." % mark(known))
        if(verified): wikipedia.output("Verified as %s." % mark(verified))
        if(uncertain): wikipedia.output("Uncertain: %s" % uncertain)
        if(k.info_string(revid)): wikipedia.output("Annotation: %s" % k.info_string(revid))
        show_diff(e)
        if(extra): extra()
                                 
        if((uncertain and not verified) or retrain):
            if not verified: known = score              # keep verified answer by default, use score overwise
            answer = wikipedia.inputChoice(u'Do you want to mark this revision as %s (Yes)?' % \
                        mark(known), labels(), labels_shortcuts(), 'Y')
            if answer == 'n':
                wikipedia.output(" \03{lightpurple}***** Wow! *****\03{default} \03{lightgreen}Thank you for correcting me.\03{default}") 
            (known, verified) = labeler(answer, known, verified)
            wikipedia.output("Marked as %s, %s" % (mark(known), mark(verified)) )
            _human_responses += 1
        #else:
        #    if(not verified): known = score

    # Collecting stats
    ids.known[revid] = known
    stats['Revision analysis score ' + score + ' on known'][known] += 1
    if(verified and _verbose_arg):
        ids.verified[revid] = verified
        stats['Revision analysis score ' + score + ' on verified'][verified] += 1

    if(_human_responses > 5):
        _human_responses = 0
        dump_cstats(stats)

    return (verified, known, score)



def check_karma(revisions, user_karma):
    if(not user_karma):
        user_karma = defaultdict(int); user_features = defaultdict(str);
        for e in revisions:
            known = k.is_known(e.revid)    # previous score (some human verified)
            if(known == 'good'): user_karma[e.username] += 1; user_features[e.username] += 'g';
            if(known == 'bad'): user_karma[e.username] -= 1; user_features[e.username] += 'b';
    
    for e in revisions:
        revid = e.revid
        known = k.is_known(revid)                      # previous score (some human verified)
        verified = k.is_verified(revid)                # if not Empty: human verified
        karma = user_karma[e.username]
        if not known: continue
        
        # if(e.reverts_info == -5):                               # inverse for self-reverts
        #    score = ('bad', 'good')[karma < 0]
        #else:
        score = ('bad', 'good')[karma > 0]
        stats['Reputation score ' + score + ' on known'][known] += 1
    
        # Collecting stats and Human verification
        extra = lambda:wikipedia.output(" User Features: \03{lightblue}%s\03{default}" % user_features[e.username])
        (verified, known, score) = collect_stats(stats, user_karma, e, score, False, extra)

    return user_karma



def compute_revisions_trainset(revisions, user_counters):
    train = []

    for e in revisions:
        #if not analyse_revision_decisiontree(e, user_reputations) != 'unknown': 
        #   train.append(None); 
        #else:
        
        # for v in xrange(1,100): print v, math.trunc(math.log(math.sqrt(v))*2*math.pi)
        features = {'comment' : analyse_comment(e.comment),
                    # 'reverts info' : urri(e.reverts_info),
                    'ipedit' : e.ipedit,
                    'edit_group' : bool(e.edit_group), 
                    'smaller' : (e.ilR > e.ilA and e.iwR > 1),
                    'large_scale_removal' : (e.iwR == 50),  
                    #'size' : ('larger', 'same', 'smaller')[max(1, min(-1, e.size < prev.size))]
                    #'smaller_than_average' : e.size * i < total_size,
                    #'same_user' : e.username != prev.username, 
                    #'accepted' : e.utc - prev.utc * i > total_time      # prev edition has managed longer than usual        
                    }

        #total_size += e.size; total_time += (e.utc - prev.utc); prev = e;
        train.append( (features, k.is_known(e.revid)) )
    return train


buckets_table = [0, 1, 2, 2, 3, 3, 3, 3, 3, 3,
                 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 
                 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 
                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
                 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
def buckets(i):
    return math.trunc(math.log1p(i * 2 * math.pi))
    

def compute_karma_trainset(revisions, user_counters):
    train = []

    for e in revisions:
        known = k.is_known(e.revid)  # previous score (some human verified)
        
        if e.username in user_counters:
            counter = user_counters[e.username]
            features = {'edits' : buckets(counter[0]),
                        'comments' : buckets(counter[1]),
                        'reverts'  : buckets(counter[2]),
                        'regular' : buckets(counter[-1]),
                        'reverted' : buckets(counter[-2]),
                        'questionable' : buckets(counter[-3]),
                        'revert war' : buckets(counter[-4]),
                        'self revert' : buckets(counter[-5]),
                        #'known user' : 'True',
                        }
            train.append( (features, known) )
        else: 
            train.append(None)
            #features = {
            #        'known user' : False
            #       }
        

    return train



def analyse_maxent(revisions, user_counters):
    # apt-get apt-get install python-numpy python-scipy
    # import numpy as np

    # NLTK, the Natural Language Toolkit
    # Note: requires http://code.google.com/p/nltk/issues/detail?id=535 patch
    # download and extract megam_i686.opt from http://www.cs.utah.edu/~hal/megam/
    import nltk, maxent, megam, platform
    megam.config_megam( ('./megam_i686.opt', './megam_x64')[platform.architecture() == ('64bit', 'ELF')] )
    # from nltk.classify import maxent, megam

    train = compute_karma_trainset(revisions, user_counters)
    
    if(not _classifier_arg):        
        # Typed:
        #enc = maxent.TypedMaxentFeatureEncoding.train([t for t in train if t], alwayson_features=True)
        #for fs in train:
        #    s = "";
        #    for f, v in fs[0].iteritems(): s += " : %s = %4s " % (f, v)
        #    print("Featureset", s, " Class: ", fs[1] , "Encoding is: ", enc.encode(fs[0], fs[1]))
        #classifier = maxent.MaxentClassifier.train([t for t in train if t], algorithm='megam', encoding=enc, \
        #                bernoulli=False, trace=2, tolerance=2e-5, max_iter=1000, min_lldelta=1e-7)
        
        # Bool:
        classifier = maxent.MaxentClassifier.train([t for t in train if t], algorithm='megam', trace=2, tolerance=2e-6, max_iter=2000, min_lldelta=1e-8)
    else:
        wikipedia.output("Reading %s..." % _classifier_arg)
        classifier = cPickle.load(open(_classifier_arg, 'rb'))


    classifier.show_most_informative_features(n=100, show='all')

    if(_output_arg): cPickle.dump(classifier, open(_output_arg, 'wb'), 1)


    for i, e in enumerate(revisions):
        known = k.is_known(e.revid)                                 # previous score (some human verified)
        verified = k.is_verified(e.revid)                           # if not Empty: human verified        
        if not train[i]: continue                                   # skip this revision
        pdist = classifier.prob_classify(train[i][0])
        score = ('bad', 'good')[pdist.prob('good') > pdist.prob('bad')]
        #if pdist.prob('good') > 0.65: score = 'good'
        #elif pdist.prob('bad') > 0.65: score = 'bad'
        #else: continue

        stats['Maxent score ' + score + ' on known'][known] += 1
                
        # Collecting stats and Human verification
        #if(verified): score = k.is_verified_as_good_or_bad(e.revid)
        #if(not score): print e.revid
        #k.known[e.revid] = known = score
        uncertain = known != score
        extra = lambda: classifier.explain(train[i][0]);
        (verified, known, score) = collect_stats(stats, user_counters, e, score, uncertain, extra)



def analyse_plot_reverts(revisions, user_counters):
    import matplotlib.pyplot as plt
    if True:
        y = defaultdict(lambda:[[] for i in xrange(len(counters_dict()[0]))] )
        l = defaultdict(int)     
        for e in revisions:
            known = k.is_known(e.revid)  # previous score (some human verified)
            counter = user_counters[e.username]
            for i, c in enumerate(counter): y[known][i].append(c)
            l[known] += 1
    
        #plt.plot(y['good'][0], [1] * l['good'], 'g|')
        #plt.plot(y['bad'][0], [2] * l['bad'], 'r|')
        plt.plot(y['good'][0], y['good'][1], 'g.')
        plt.plot(y['bad'][0], y['bad'][1], 'r.')
        #plt.axis([0, 200, 0, 200])
        plt.show()


    s = defaultdict(lambda:defaultdict(lambda:[0] * 500))     
    for x in xrange(500):
        for e in revisions:
            known = k.is_known(e.revid)  # previous score (some human verified)
            counter = user_counters[e.username]
            if(counter[0] < 25): continue            
            score = ('bad', 'good')[counter[-2]/ 100.0 * x < counter[0]]
            s[known][score][x] += 1

    #plt.plot(xrange(1000), s['good']['good'], 'g')
    plt.plot([x/100.0 for x in xrange(500)], s['bad']['bad'], 'g')
    plt.plot([x/100.0 for x in xrange(500)], s['good']['bad'], 'r')
    plt.plot([x/100.0 for x in xrange(500)], s['bad']['good'], 'm')
    plt.axis([0, 5, 0, 1000])
    plt.show()



def analyse_plot(revisions, user_counters):
    import matplotlib.pyplot as plt
    if False:
        y = defaultdict(lambda:[[] for i in xrange(len(counters_dict()[0]))] )
        l = defaultdict(int)     
        for e in revisions:
            known = k.is_known(e.revid)  # previous score (some human verified)
            counter = user_counters[e.username]
            for i, c in enumerate(counter): y[known][i].append(c)
            l[known] += 1
    
        #plt.plot(y['good'][0], [1] * l['good'], 'g|')
        #plt.plot(y['bad'][0], [2] * l['bad'], 'r|')
        plt.plot(y['good'][0], y['good'][1], 'g.')
        plt.plot(y['bad'][0], y['bad'][1], 'r.')
        #plt.axis([0, 200, 0, 200])
        plt.show()


    N = 20
    s = defaultdict(lambda:defaultdict(lambda:[0] * N))     
    for x in xrange(N):
        for e in revisions:
            known = k.is_known(e.revid)  # previous score (some human verified)
            counter = user_counters[e.username]
            score = ('bad', 'good')[counter[1] > x]
            s[known][score][x] += 1

    #plt.plot(xrange(1000), s['good']['good'], 'g')
    plt.plot([x for x in xrange(N)], s['bad']['bad'], 'g')
    plt.plot([x for x in xrange(N)], s['good']['bad'], 'r')
    plt.plot([x for x in xrange(N)], s['bad']['good'], 'm')
    plt.axis([0, N, 0, 15000])
    plt.show()






def evaluate_gold(revisions, user_counters):
    print "editid,newrevisionid,class,annotators,totalannotators,known,verified,diffurl,editgroupdiffurl,revertdiffurl,revertcomment"
    for i, e in enumerate(revisions):
        score = k.is_gold(e.revid)
        known = k.is_known(e.revid)                                 # previous score (some human verified)
        info = k.info[e.revid]
        verified = k.is_verified(e.revid)                           # if not Empty: human verified
        if not known: continue
        if score == known: continue        

        edit_group_diff = ""; revert_diff = "";  revert_comment = ""
        if(e.edit_group and e.edit_group[0].oldid): edit_group_diff = "http://en.wikipedia.org/w/index.php?diff=%d&oldid=%d" % (e.edit_group[-1].revid, e.edit_group[0].oldid) 
        if(e.reverted): revert_diff = "http://en.wikipedia.org/w/index.php?diff=%d" % e.reverted.revid; 
        if(e.reverted and e.reverted.comment): revert_comment = e.reverted.comment


        print('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s"' %
                         (info[0]['editid'], e.revid, info[1]['class'], info[1]['annotators'], info[1]['totalannotators'],                        
                          known, verified,   
                          info[0]['diffurl'],
                          edit_group_diff, revert_diff, revert_comment.encode("utf-8")   
                          ))


        uncertain = known != score
        (verified, known, score) = collect_stats(stats, user_counters, e, score, uncertain, None)



def analyse_crm114(revisions, user_counters):
    # stats
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
        known = k.is_known(revid)                               # previous score (some human verified)
        verified = k.is_verified(revid)                         # if not Empty: human verified

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
                uncertain = "CRM114 thinks it is: %s, prob was:%f %s" % (mark(crm114_answer), probability, falseString)
            elif(crm114_answer == 'good' and score == 'bad'): 
                falseString = "  >>> \03{lightpurple}False Negative\03{default} <<<"
                uncertain = "CRM114 thinks it is: %s, prob was:%f %s" % (mark(crm114_answer), probability, falseString)
            else: uncertain = ""
            
            # Collecting stats and Human verification
            extra = lambda:wikipedia.output(" \03{lightblue}%s\03{default}" % edit_text)
            (verified, known, score) = collect_stats(stats, user_counters, e, score, uncertain, extra)

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


# some low hanging text statistics
reU = re.compile("[A-Z]")
reL = re.compile("[a-z]")
reES = re.compile("!")
reHI = re.compile("(hi |penis|fuck)", re.I)
reI = re.compile("i ", re.I)

def analyse_comment(comment):
    #if(e.username.lower().find('bot') > -1):
    #    add_uefeature('bot')
    if(comment):
        if comment.startswith('[[WP:'):
            if comment.startswith(u'[[WP:UNDO|Undid'): return 'undo'
            elif comment.startswith(u'[[WP:A'):
                if comment.startswith(u'[[WP:AES|\u2190]]Replaced'): return 'replaced'
                elif comment.startswith(u'[[WP:AES|\u2190]]Redirected'): return 'redirected'
                elif comment.startswith(u'[[WP:AES|\u2190]]Blanked'): return 'blanked'
                elif comment.startswith(u'[[WP:AES|\u2190]]Undid'):  return 'undid'
                elif comment.startswith(u'[[WP:AES|\u2190]]Reverted'): return 'reverted'
                elif comment.startswith(u'[[WP:AES|\u2190]] Replaced'): return 'replaced'
                elif comment.startswith(u'[[WP:AES|\u2190]] Redirected'): return 'redirected'
                elif comment.startswith(u'[[WP:AES|\u2190]] Blanked'): return 'blanked'
                elif comment.startswith(u'[[WP:AES|\u2190]] Undid'): return 'undid'
                elif comment.startswith(u'[[WP:AES|\u2190]] Reverted'): return 'reverted'
                elif comment.startswith(u'[[WP:AES|\u2190]]\u200bReplaced'): return 'replaced'
                elif comment.startswith(u'[[WP:AES|\u2190]]\u200bRedirected'): return 'redirected'
                elif comment.startswith(u'[[WP:AES|\u2190]]\u200bBlanked'): return 'blanked'
                elif comment.startswith(u'[[WP:AES|\u2190]]\u200bUndid'): return 'undid'
                elif comment.startswith(u'[[WP:AES|\u2190]]\u200bReverted'): return 'reverted'
                elif comment.startswith(u'[[WP:AES|\u2190Replaced'): return 'replaced'
                elif comment.startswith(u'[[WP:AES|\u2190Redirected'): return 'redirected'
                elif comment.startswith(u'[[WP:AES|\u2190Blanked'): return 'blanked'
                elif comment.startswith(u'[[WP:AES|\u2190Undid'): return 'undid'
                elif comment.startswith(u'[[WP:AES|\u2190Reverted'): return 'reverted'
                elif comment.startswith(u'[[WP:Automatic edit summaries|\u2190]]Replaced'): return 'replaced'
                elif comment.startswith(u'[[WP:Automatic edit summaries|\u2190]]Redirected'): return 'redirected'
                elif comment.startswith(u'[[WP:Automatic edit summaries|\u2190]]Blanked'): return 'blanked'
                elif comment.startswith(u'[[WP:Automatic edit summaries|\u2190]]Undid'): return 'undid'
                elif comment.startswith(u'[[WP:Automatic edit summaries|\u2190]]Reverted'): return 'reverted'
                elif comment.startswith(u'[[WP:AWB'): return 'awb'
                elif comment.startswith(u'[[WP:AES'): return 'aes'
                else: return 'wp'
            elif comment.startswith(u'[[WP:UNDO|Revert'): return 'revert'
            elif comment.startswith(u'[[WP:RBK|Reverted'): return 'reverted'
            #elif comment.startswith(u'[[Help:': return 'help'    
            else: return 'wp'   #print e.comment.encode('unicode-escape');
        elif(comment[-2:] == '*/'): return 'section'
        else:
            if e.comment.startswith('Revert'): return 'revert'
            #elif e.comment.startswith('Undid'): return 'undid'
            #elif e.comment.startswith('rvv'): return 'rvv'
            #elif e.comment.startswith('rev'): return 'rev'
            #elif e.comment.startswith('rv'): return 'rv' 
            #elif e.comment[:4] in ('BOT ', 'bot ', 'robo', 'Robo'): return 'bot'
            #elif e.comment.startswith('cat'): return 'cat'
            #elif e.comment.startswith('+'): return 'plus'
            #elif e.comment.find('spam') > -1: return 'spam'; 
            #elif e.comment.find('ref') > -1: return 'ref'            
            
            uN = len(reU.findall(comment))
            lN = len(reL.findall(comment))
            esN = len(reES.findall(comment))
            if(uN > 5 and lN < uN): return 'stats'       # uppercase stats is looking bad
            elif(esN > 2): return 'stats'
            elif(reHI.search(comment) != None): return 'hi'
            elif(reI.search(comment) != None): return 'i'
            return 'good'
            # if len(comment) > 80:        # we like long comments
            # if(len(e.comment.split()) > 7): add_uefeature('comment_long')
    return 'no'  


def analyse_decisiontree(revisions, user_counters):
    total_time = total_size = 0
    for e in revisions:

        score = analyse_revision_decisiontree(e, user_counters)
        if(score == 'unknown'): continue
        #uncertain = (user_counters[e.username] > 0 and score == 'bad') or (user_counters[e.username] < 0 and score == 'good')
        (verified, known, score) = collect_stats(stats, user_counters, e, score, False, None)

def analyse_revision_decisiontree(e, user_counters):
    known = k.is_known(e.revid)                 # previous score (some human verified)
    comment = analyse_comment(e.comment)
    
    score = 0
    
    #if comment in ['no', 'section']: pass
    #elif comment == 'good': pass
    #elif comment in ['replaced', 'blanked']: score -= 100
    #elif comment in ['undid', 'redirected', 'reverted', 'awb', 'aes', 'wp', 'revert']: score += 100
    #elif comment in ['hi', 'i', 'stats']: pass

    #removal = e.ilR > e.ilA and e.iwR > 1                # and new page is smaller than the previous
    #blanking = e.iwR == 50 and e.iwA < 2                 # large scale removal

    # if not e.ipedit and comment: score += 10
    # if(e.ipedit and no_comment): score -= 1
    # if(e.ipedit and no_comment_section): score -= 1
    # if(e.utc - prev.utc * i > total_time):              # prev edition has managed longer than usual
    
    if score > 0: score = 'good'
    elif score < 0: score = 'bad'
    else: score = 'unknown'
    return score




def compute_counters(revisions, user_counters):
    total_time = total_size = 0
    for e in revisions:
        score = 0

        regular_comment = 0
        if(e.comment):
            comment = e.comment
            if comment.startswith(u'[[WP:AES'): pass
            elif comment.startswith(u'[[WP:Automatic edit summaries'): pass
            elif comment.startswith(u'[[WP:UNDO'): pass
            elif comment[-2:] == '*/': pass
            else:
                uN = len(reU.findall(comment))
                lN = len(reL.findall(comment))
                esN = len(reES.findall(comment))
                if(uN > 5 and lN < uN): pass                        # uppercase stats is looking bad
                elif(esN > 2): pass
                elif(reHI.search(comment) != None): pass
                elif(reI.search(comment) != None): pass
                else: regular_comment = 1

        if e.reverts_info > -1: b =    (1, regular_comment, 1, 0, 0, 0, 0, 0)
        elif e.reverts_info == -1: b = (1, regular_comment, 0, 0, 0, 0, 0, 1)
        elif e.reverts_info == -2: b = (1, regular_comment, 0, 0, 0, 0, 1, 0)
        elif e.reverts_info == -3: b = (1, regular_comment, 0, 0, 0, 1, 0, 0)
        elif e.reverts_info == -4: b = (1, regular_comment, 0, 0, 1, 0, 0, 0)
        elif e.reverts_info == -5: b = (1, regular_comment, 0, 1, 0, 0, 0, 0)
        else: b = (1, regular_comment, 0, 0, 0, 0, 0, 0)

        user_counters[e.username] = tuple([a+b for (a,b) in zip(user_counters[e.username] , b)])
        # Collecting stats and Human verification
        #known = k.is_known(e.revid)
        #if(not regular_comment and known == 'good'):
        #    (verified, known, score) = collect_stats(stats, user_counters, e, 'unknown', False, None)




def compute_counters_dictionary():
    user_counters = counters_dict()

    if(_output_arg):
        FILE = open(_output_arg, 'wb')

    total_pages = 0; total_revisions = 0; start = time.time();
    for revisions in read_pyc():
        analyse_reverts(revisions)
        compute_counters(revisions, user_counters)
        total_pages += 1;
        total_revisions += len(revisions)

        if(total_pages%1000 == 0):
            wikipedia.output("Page %d. Revisions %d. Users %s. Analysis time: %f. " %
                (total_pages, total_revisions, len(user_counters), time.time() - start))

            for u, r in user_counters.iteritems():
                marshal.dump((u, r), FILE)
            user_counters = counters_dict()

    if(_output_arg):
        for u, r in user_counters.iteritems():
            marshal.dump((u, r), FILE)



def main():
    global _retrain_arg, _train_arg, _human_responses, _verbose_arg, _output_arg, _pyc_arg, _counters_arg, _classifier_arg, stats; 
    _xml_arg = None; _pyc_arg = None; _display_last_timestamp_arg = None; _compute_pyc_arg = None; 
    _display_pyc_arg = None; _compute_counters_arg = None;_output_arg = None; _analyze_arg = None
    _counters_arg = None; _username_arg = None; _filter_pyc_arg = None; _count_empty_arg = None
    _revisions_arg = None; _filter_known_revisions_arg = None; _classifier_arg = None; _evaluate_arg = None
    stats = defaultdict(lambda:defaultdict(int)); revisions = [];

    for arg in wikipedia.handleArgs():
        if arg.startswith('-xml') and len(arg) > 5: _xml_arg = arg[5:]
        if arg.startswith('-pyc') and len(arg) > 5: _pyc_arg = arg[5:]
        if arg.startswith('-revisions') and len(arg) > 11: _revisions_arg = arg[11:]
        if arg.startswith('-counters') and len(arg) > 10: _counters_arg = arg[10:]
        if arg.startswith('-classifier') and len(arg) > 12: _classifier_arg = arg[12:]
        if arg.startswith('-username') and len(arg) > 10: _username_arg = arg[10:]
        if arg.startswith('-retrain'): _retrain_arg = True
        if arg.startswith('-filter-pyc'): _filter_pyc_arg = True
        if arg.startswith('-retrain') and len(arg) > 9: _retrain_arg = arg[9:]
        if arg.startswith('-train'): _train_arg = True
        if arg.startswith('-vvv'): _verbose_arg = True
        if arg.startswith('-output') and len(arg) > 8: _output_arg = arg[8:]
        if arg.startswith('-display-last-timestamp'): _display_last_timestamp_arg = True
        if arg.startswith('-compute-counters'): _compute_counters_arg = True
        if arg.startswith('-filter-known-revisions'): _filter_known_revisions_arg = True
        if arg.startswith('-compute-pyc'): _compute_pyc_arg = True
        if arg.startswith('-display-pyc'): _display_pyc_arg = True
        if arg.startswith('-count-empty'): _count_empty_arg = True
        if arg.startswith('-analyze'): _analyze_arg = True
        if arg.startswith('-analyze') and len(arg) > 9: _analyze_arg = arg[9:] 
        if arg.startswith('-evaluate'): _evaluate_arg = True
 

    if(not _xml_arg and not _pyc_arg and not _counters_arg and not _revisions_arg):
        wikipedia.output('Usage: ./r.py \03{lightblue}-xml:\03{default}path/Wikipedia-Dump-*.xml.7z -output:Wikipedia-Dump.full -compute-pyc')
        wikipedia.output('     : ./r.py \03{lightblue}-pyc:\03{default}path/Wikipedia-Dump.full -analyze')
        return

    if(_xml_arg):        # XML files input
        xmlFilenames = sorted(locate(_xml_arg))
        wikipedia.output(u"Files: \n%s\n\n" % xmlFilenames)
        mysite = wikipedia.getSite()

    if(_display_last_timestamp_arg): display_last_timestamp(xmlFilenames); return
    if(_compute_pyc_arg): compute_pyc(xmlFilenames); return


    # Precompiled .pyc (.full) files input
    if(_display_pyc_arg): display_pyc(); return
    if(_count_empty_arg): read_pyc_count_empty(); return
    if(_filter_pyc_arg): filter_pyc(); return
    if(_compute_counters_arg):
        compute_counters_dictionary()

    # filter and save known revisions
    if(_filter_known_revisions_arg):
        known_revisions = []
        for revisions in read_pyc():
            analyse_reverts(revisions)
            for e in revisions:
                if k.is_known(e.revid): known_revisions.append(e)
        if(_output_arg): cPickle.dump(known_revisions, open(_output_arg, 'wb'), -1)

    # load known revisions
    if(_revisions_arg):
        wikipedia.output("Reading %s..." % _revisions_arg)
        revisions = cPickle.load(open(_revisions_arg, 'rb'))


    if(_counters_arg):
        user_counters = read_counters(revisions)
        if(_username_arg): 
            wikipedia.output("User %s, has_key %s, counter %s" %
                (_username_arg, user_counters.has_key(_username_arg), user_counters[_username_arg]))



    #analyse_tokens_lifetime(xmlFilenames)
    start = time.time();

    if(_evaluate_arg):
        evaluate_gold(revisions, defaultdict(int))        

    if(_analyze_arg):        
        if(_analyze_arg == 'counters'): user_counters = check_counters(revisions, user_counters)        
        if not user_counters: user_counters = counters_dict()
        if(_analyze_arg == 'maxent'): analyse_maxent(revisions, user_counters)
        if(_analyze_arg == 'plot'): analyse_plot(revisions, user_counters)
        if(_analyze_arg == 'decisiontree'): analyse_decisiontree(revisions, user_counters)
        # user_reputations = analyse_reputations(revisions)
        # analyse_crm114(revisions, user_counters)
        wikipedia.output("Revisions %d. Analysis time: %f" % (len(revisions), time.time() - start))
        dump_cstats(stats)


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

