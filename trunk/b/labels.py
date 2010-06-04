from operator import itemgetter
import re

# k, known - latest best evaluation, if verified as X should be known as X
# g, gold - imported dataset
# v, verified - human labels, superiour to gold and known
# i, info - dict with extra labels

# for r in ids['bad']:
#    print '<a href="http://en.wikipedia.org/w/index.php?diff==%d">%d</a>' % (r, r)


class Dataset(object):
    "Labeled lists of revisions. Two lists: known and verified."
    def __init__(self):
        self.known = dict()
        self.verified = dict()
        self.gold = dict()
        self.info = dict()

    def dump_dict(self, d, name):
        print
        print name, "= {"
        labels = [(rid, v) for rid, v in d.iteritems()]
        labels.sort(key = itemgetter(0))
        for l in labels:
            print "%s : '%s',    " % l
        print "}"

    def dump(self):
        self.dump_dict(self.known, "known")
        self.dump_dict(self.verified, "verified")
        self.dump_dict(self.gold, "gold")
        self.dump_dict(self.info, "info")

    def is_verified(self, rid):
        label = self.verified.get(rid)
        if(label == None):           return None
        if(label == "Regular"):      return 'good'
        if(label == "Constructive"): return 'good'
        return 'bad'

    def is_known(self, rid):
        return self.known.get(rid)

    def info_string(self, rid):
        if not self.info.get(rid): return ""
        return str(self.info[rid])

    def append_dict(self, dst, src):
        for (rid, v) in src.iteritems():
            if rid in dst: print "Duplicate:", rid
            else: dst[rid] = v

    def append(self, gold = {}, info = {}, known = {}, verified = {}):
        self.append_dict(self.gold, gold)
        self.append_dict(self.info, info)
        self.append_dict(self.known, known)
        self.append_dict(self.verified, verified)

    def check(self):
        for rid in self.verified.keys():
            if not rid in self.known: print "Verified:", rid, "is unknown."
            if self.is_known(rid) != self.is_verified(rid): 
                print "Verified:", rid, "is known as:", self.is_known(rid), " But it is verified as:", self.is_verified(rid), "."                 
        for rid in self.gold.keys():
            if not rid in self.known: print "Gold:", rid, "is unknown."
        

ids = Dataset()     # new
k = Dataset()       # known


labels_list = [(l, ''.join(re.findall("[A-Z]", l)), d) for (l, d) in [
    ("Yes"           , """Internal Use. Not a label. Agree with the proposed label."""),
    ("No"            , """Internal Use. Not a label. Select the opposite of the proposed label."""),
    ("Skip"          , """Internal Use. Not a label. Skip it."""),
    ("Regular"       , """Regular constructive edit done in a good faith. In other words good edit."""),
    ("Vandalism"     , """Generick vandalism. Destructive edit done in a bad faith. In other words unclassified bad edit."""),
    ("Constructive"  , """Inaccurate, but constructive edit done in a good faith. Includes partial vandalism clenup, etc. In other words good, but innacurate edit."""),
    ("Blanking"      , """Removing all or significant parts of a page's content without any reason, or replacing entire pages with nonsense. """),
    ("Link spam"     , """Adding or continuing to add external links to non-notable or irrelevant sites."""),
    ("Graffiti"      , """Adding profanity, graffiti, random characters (gibberish) to pages."""),
    ("Partial self-revert"   , """Hiding vandalism (by making two bad edits and only reverting one or by reverting edit only partially)."""),
    ("Formatting"            , """Formatting incorrecty or using incorrect wiki markup and style."""),
    ("Misinformation"        , """Adding plausible misinformation to articles, (e.g. minor alteration of facts or additions of plausible-sounding hoaxes)."""),
    ("Image Attack"          , """Uploading shock images, inappropriately placing explicit images on pages, or simply using any image in a way that is disruptive."""),
    ("Tests"                 , """Adding unhelpful content to a page (e.g., a few random characters) as a test. Not done in bad faith."""),
    ("Unintentional"         , """Inaccurate and destructive addition or removal of content but in the belief that it is accurate. Done in a good faith."""),
    ("Revert Warring"        , """Reverting good faith contributions of other users without any reason. Engaging into a revert war."""),
    ("Edit Warring"          , """Engaging into an edit war."""),
    ("NONSence"              , """Adding nonsense to pages; creating nonsensical and obviously non-encyclopedic pages."""),
    ("Joke"                  , """Adding obviously non-encyclopedic jokes to pages."""),
    ("NPOV dispute"          , """Introducing inappropriate material which is not ideal from a NPOV perspective."""),
    ("SPAM"                  , """Adding text (with or without external links) that promotes one's personal interests."""),
    ("Page Lengthening"      , """Adding very large amounts of bad-faith content to a page."""),
    ("Personal Attacks"      , """Adding insults, profanity, etc which constitutes a personal attack."""),
    ("Abuse of Tags"         , """Bad-faith placing of non-content tags such as {{tl|afd}}, {{tl|delete}}, {{tl|sprotected}}, or other tags on pages that do not meet such criteria. This includes removal of extremely-long-standing {{tl|policy}} and related tags without forming consensus on such a change first."""),
    ("Edit Summary Vandalism" , """Making offensive edit summaries in an attempt to leave a mark that cannot be easily expunged from the record."""),
    ("Sneaky Vandalism"      , """Vandalism that is harder to spot, or that otherwise circumvents detection. Using two or more different accounts and/or IP addresses at a time to vandalize, abuse of maintenance and deletion templates, or reverting legitimate edits with the intent of hindering the improvement of pages. Some vandals even follow their vandalism with an edit that states "rv vandalism" in the edit summary in order to give the appearance the vandalism was reverted."""),
    ("Page Creation"         , """Creating new pages with the sole intent of malicious behavior."""),
    ("VandalBot"             , """A script or robot that attempts to vandalize or spam ''massive'' numbers of articles (hundreds or thousands)."""),
    ("Template Vandalism"    , """Modifying the wiki language or text of a template in a harmful or disruptive manner. This is especially serious, because it will negatively impact the appearance of multiple pages. Some templates appear on hundreds of pages."""),
    ("Page-move Vandalism"   , """Changing the names of pages (referred to as "page-moving") to disruptive, irrelevant, or otherwise inappropriate terms.  Wikipedia now only allows registered users active for at least four days and with at least 10 edits (i.e. autoconfirmed users) to move pages."""),
    ("Link Vandalism"        , """Modifying internal or external links within a page so that they appear the same but link to a page/site that they are not intended to (e.g. spam, self-promotion, an explicit image, a shock site)."""),
    ("Avoidant Vandalism"    , """Removing {{tl|afd}}, {{tl|copyvio}} and other related tags in order to conceal deletion candidates or avert deletion of such content. Note that this is often mistakenly done by new users who are unfamiliar with AfD procedures and such users should be given the benefit of the doubt and pointed to the proper page to discuss the issue."""),
    ("Modifying Users Comments"  , """Editing other users comments to substantially change their meaning (e.g. turning someone's vote around), except when removing a personal attack."""),
    ("Discussion Page vandalism" , """Blanking the posts of other users from talk pages other than your own, Wikipedia space, and other discussions, aside from removing spam, vandalism, etc., is generally considered vandalism."""),
    ("Repeated Uploading of Copyrighted Material" , """Uploading or using material on Wikipedia in ways which violate Wikipedia's copyright policies after having been warned is vandalism. Because users may be unaware that the information is copyrighted, or of Wikipedia policies on how such material may and may not be used, such action ''only'' becomes vandalism if it continues after the copyrighted nature of the material and relevant policy restricting its use have been communicated to the user."""),
    ("Malicious Account Creation" , """Creating accounts with usernames that contain deliberately offensive or disruptive terms."""),
    ("Hidden Vandalism" , """Any form of vandalism that makes use of embedded text, which is not visible to the final rendering of the article but visible during editing. This includes link vandalism (described above), or placing malicious, offensive, or otherwise disruptive or irrelevant messages or spam in hidden comments for editors to see."""),
    ("Gaming The System" , """Deliberate attempts to circumvent enforcement of Wikipedia policies, guidelines, and procedures by making bad faith edits go unnoticed. Includes marking bad faith edits as minor to get less scrutiny, making a minor edit following a bad faith edit so it won't appear on all watchlists, recreating previously deleted bad faith creations under a new title, use of the {{tl|construction}} tag to prevent deletion of a page that would otherwise be a clear candidate for deletion, or use of sock puppets."""),
]]

good_labels = ['Regular', 'Constructive']
bad_labels = [label for (label, shortcut, description) in labels_list if label not in good_labels]

def labels_shortcuts():
    return [shortcut for (label, shortcut, description) in labels_list]

def labels():
    return [label for (label, shortcut, description) in labels_list]

def labels_legend():
    legend = [re.sub(r"([A-Z]+)", r"[\1]", label) for (label, shortcut, description) in labels_list]
    return ",   ".join(sorted(legend))

def labeler(answer, known, verified):
    if answer == 'n':
        if known == 'good':  known = 'bad'
        elif known == 'bad': known = 'good'
        else: print "Warning. Answer is (N) and known =", known
    elif answer == 'y':
        if known not in ['good', 'bad']: print "Warning. Answer is (Y) and known =", known
    elif answer == 's':
        return (known, verified)
    else:
        try:
            verified = labels()[labels_shortcuts().index(answer.upper())]
            known = ('bad', 'good')[verified in good_labels]
            return (known, verified)
        except:
            print "Warning. Answer was:", answer
            return (known, verified)

    if(known == 'good' and verified not in good_labels): verified = 'Regular'
    elif(known == 'bad' and verified not in bad_labels): verified = 'Vandalism'
    else: "Warning. known =", known
    return (known, verified)


if __name__ == "__main__":
    import unittest, pprint
    
    g = {3552757 : 'good', 4519859 : 'bad', 4758519 : 'good', 4805423 : 'good',}
    i = {
        3552757 : {'vandal_type': '', 'revert': '0', 'rev_id': '3552757'},
        4519859 : {'vandal_type': 'Blanking', 'revert': '0', 'rev_id': '4519859'},
        4758519 : {'vandal_type': '', 'revert': '0', 'rev_id': '4758519'},
        4805423 : {'vandal_type': '', 'revert': '0', 'rev_id': '4805423'},
        }
    v = {3552757 : 'Regular', 4519859 : 'Blanking', 4758519 : 'Regular', 4805423 : 'Regular',}
    k = {3552757 : 'good', 4519859 : 'bad', 4758519 : 'good', 4805423 : 'good',}
    k_ = {3552757 : 'bad', 4519859 : 'bad', 4758519 : 'bad', 4805423 : 'bad',}
    
  

    class DefaultTests(unittest.TestCase):
        def test_labels(self):
            """Verify labels"""
            shortcuts = {}
            for (l, s, d) in labels_list:
                if(s in shortcuts):
                    print "Duplicate Shortcut: ", shortcuts[s], l
                else:
                    shortcuts[s] = l
                    
            print labels_legend()

        def test_dataset(self):
            """Verify Dataset() class methods"""
            t = Dataset()
            t.append(gold = g, info = i, verified = v, known = k)
            print
            t.dump()
            print
            t.check()
            print
            
        def test_negative(self):
            """Verify Dataset() error reporting"""
            t = Dataset()
            t.append(gold = g, info = i, verified = v, known = k_)
            print
            t.dump()
            print
            t.check()
            print
            t.append(known = k)

        def test_labeler(self):
            self.assertTrue( labeler('y', 'good', 'Regular') == ('good', 'Regular') )
            self.assertTrue( labeler('n', 'good', 'Regular') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('s', 'good', 'Regular') == ('good', 'Regular') )
            self.assertTrue( labeler('b', 'good', 'Regular') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'good', 'Regular') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'good', 'Constructive') == ('good', 'Constructive') )
            self.assertTrue( labeler('n', 'good', 'Constructive') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('s', 'good', 'Constructive') == ('good', 'Constructive') )
            self.assertTrue( labeler('b', 'good', 'Constructive') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'good', 'Constructive') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'good', 'Vandalism') == ('good', 'Regular') )
            self.assertTrue( labeler('n', 'good', 'Vandalism') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('s', 'good', 'Vandalism') == ('good', 'Vandalism') )   # Drat
            self.assertTrue( labeler('b', 'good', 'Vandalism') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'good', 'Vandalism') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'good', 'Blanking') == ('good', 'Regular') )
            self.assertTrue( labeler('n', 'good', 'Blanking') == ('bad', 'Blanking') )
            self.assertTrue( labeler('s', 'good', 'Blanking') == ('good', 'Blanking') )   # Drat
            self.assertTrue( labeler('b', 'good', 'Blanking') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'good', 'Blanking') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'good', 'Graffiti') == ('good', 'Regular') )
            self.assertTrue( labeler('n', 'good', 'Graffiti') == ('bad', 'Graffiti') )
            self.assertTrue( labeler('s', 'good', 'Graffiti') == ('good', 'Graffiti') )   # Drat
            self.assertTrue( labeler('b', 'good', 'Graffiti') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'good', 'Graffiti') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'good', '') == ('good', 'Regular') )
            self.assertTrue( labeler('n', 'good', '') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('s', 'good', '') == ('good', '') )
            self.assertTrue( labeler('b', 'good', '') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'good', '') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'bad', 'Regular') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('n', 'bad', 'Regular') == ('good', 'Regular') )
            self.assertTrue( labeler('s', 'bad', 'Regular') == ('bad', 'Regular') )     # Drat
            self.assertTrue( labeler('b', 'bad', 'Regular') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'bad', 'Regular') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'bad', 'Constructive') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('n', 'bad', 'Constructive') == ('good', 'Constructive') )
            self.assertTrue( labeler('s', 'bad', 'Constructive') == ('bad', 'Constructive') )       # Drat
            self.assertTrue( labeler('b', 'bad', 'Constructive') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'bad', 'Constructive') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'bad', 'Vandalism') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('n', 'bad', 'Vandalism') == ('good', 'Regular') )
            self.assertTrue( labeler('s', 'bad', 'Vandalism') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('b', 'bad', 'Vandalism') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'bad', 'Vandalism') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'bad', 'Blanking') == ('bad', 'Blanking') )
            self.assertTrue( labeler('n', 'bad', 'Blanking') == ('good', 'Regular') )
            self.assertTrue( labeler('s', 'bad', 'Blanking') == ('bad', 'Blanking') )
            self.assertTrue( labeler('b', 'bad', 'Blanking') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'bad', 'Blanking') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'bad', 'Graffiti') == ('bad', 'Graffiti') )
            self.assertTrue( labeler('n', 'bad', 'Graffiti') == ('good', 'Regular') )
            self.assertTrue( labeler('s', 'bad', 'Graffiti') == ('bad', 'Graffiti') )
            self.assertTrue( labeler('b', 'bad', 'Graffiti') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'bad', 'Graffiti') == ('bad', 'Graffiti') )

            self.assertTrue( labeler('y', 'bad', '') == ('bad', 'Vandalism') )
            self.assertTrue( labeler('n', 'bad', '') == ('good', 'Regular') )
            self.assertTrue( labeler('s', 'bad', '') == ('bad', '') )
            self.assertTrue( labeler('b', 'bad', '') == ('bad', 'Blanking') )
            self.assertTrue( labeler('g', 'bad', '') == ('bad', 'Graffiti') )


    suite = unittest.TestLoader().loadTestsFromTestCase(DefaultTests)
    unittest.TextTestRunner(verbosity=2).run(suite)


