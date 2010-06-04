
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
        print name, "= [\\\n"
        labels = [(k, v) for k, v in d.iteritems()]
        labels.sort(key = itemgetter(0))
        for l in labels:
            print "%s : '%s',\n" % l
        print "]\n"

    def dump(self):
        dump_dict(self.known, "known")
        dump_dict(self.verified, "verified")
        dump_dict(self.gold, "gold")
        dump_dict(self.info, "info")

    def is_verified(self, rid):
        label = self.verified.get(rid)
        if(label == None):           return None
        if(label == "Regular"):      return 'good'
        if(label == "Constructive"): return 'good'
        return 'bad'

    def is_known(self, rid):
        return self.known.get(rid)

    def info(self, id):
        return self.info.get(rid)

    def append_dict(self, dst, src):
        for (k, v) in src.iteritems():
            if k in dst: print "Duplicate:", k
            else: dst[k] = v

    def append(self, gold, info, known, verified):
        append_dict(self.gold, gold)
        append_dict(self.info, info)
        append_dict(self.known, known)
        append_dict(self.verified, verified)


ids = Dataset()     # new
k = Dataset()       # known


labels = {
    "Regular"       : """Regular constructive edit done in a good faith. In other words good edit.""",
    "Vandalism"     : """Generick vandalism. Destructive edit done in a bad faith. In other words unclassified bad edit.""",
    "Constructive"  : """Inaccurate, but constructive edit done in a good faith. Includes partial vandalism clenup, etc. In other words good, but innacurate edit.""",
    "Blanking"      : """Removing all or significant parts of a page's content without any reason, or replacing entire pages with nonsense. """,
    "Link spam"     : """Adding or continuing to add external links to non-notable or irrelevant sites.""",
    "Graffiti"      : """Adding profanity, graffiti, random characters (gibberish) to pages.""",
    "Partial self-revert"   : """Hiding vandalism (by making two bad edits and only reverting one or by reverting edit only partially).""",
    "Formatting"            : """Formatting incorrecty or using incorrect wiki markup and style.""",
    "Misinformation"        : """Adding plausible misinformation to articles, (e.g. minor alteration of facts or additions of plausible-sounding hoaxes).""",
    "Image Attack"          : """Uploading shock images, inappropriately placing explicit images on pages, or simply using any image in a way that is disruptive.""",
    "Tests"                 : """Adding unhelpful content to a page (e.g., a few random characters) as a test. Not done in bad faith.""",
    "Unintentional"         : """Inaccurate and destructive addition or removal of content but in the belief that it is accurate. Done in a good faith.""",
    "Revert Warring"        : """Reverting good faith contributions of other users without any reason. Engaging into a revert war.""",
    "Edit Warring"          : """Engaging into an edit war.""",
    "NONSence"              : """Adding nonsense to pages; creating nonsensical and obviously non-encyclopedic pages.""",
    "Joke"                  : """Adding obviously non-encyclopedic jokes to pages.""",
    "NPOV dispute"          : """Introducing inappropriate material which is not ideal from a NPOV perspective.""",
    "Spam"                  : """Adding text (with or without external links) that promotes one's personal interests.""",
    "Page Lengthening"      : """Adding very large amounts of bad-faith content to a page.""",
    "Personal Attacks"      : """Adding insults, profanity, etc which constitutes a personal attack.""",
    "Abuse of Tags"         : """Bad-faith placing of non-content tags such as {{tl|afd}}, {{tl|delete}}, {{tl|sprotected}}, or other tags on pages that do not meet such criteria. This includes removal of extremely-long-standing {{tl|policy}} and related tags without forming consensus on such a change first.""",
    "Edit Summary Vandalism" : """Making offensive edit summaries in an attempt to leave a mark that cannot be easily expunged from the record.""",
    "Sneaky Vandalism"      : """Vandalism that is harder to spot, or that otherwise circumvents detection. Using two or more different accounts and/or IP addresses at a time to vandalize, abuse of maintenance and deletion templates, or reverting legitimate edits with the intent of hindering the improvement of pages. Some vandals even follow their vandalism with an edit that states "rv vandalism" in the edit summary in order to give the appearance the vandalism was reverted.""",
    "Page Creation"         : """Creating new pages with the sole intent of malicious behavior.""",
    "VandalBot"             : """A script or robot that attempts to vandalize or spam ''massive'' numbers of articles (hundreds or thousands).""",
    "Template Vandalism"    : """Modifying the wiki language or text of a template in a harmful or disruptive manner. This is especially serious, because it will negatively impact the appearance of multiple pages. Some templates appear on hundreds of pages.""",
    "Page-move Vandalism"   : """Changing the names of pages (referred to as "page-moving") to disruptive, irrelevant, or otherwise inappropriate terms.  Wikipedia now only allows registered users active for at least four days and with at least 10 edits (i.e. autoconfirmed users) to move pages.""",
    "Link Vandalism"        : """Modifying internal or external links within a page so that they appear the same but link to a page/site that they are not intended to (e.g. spam, self-promotion, an explicit image, a shock site).""",
    "Avoidant Vandalism"    : """Removing {{tl|afd}}, {{tl|copyvio}} and other related tags in order to conceal deletion candidates or avert deletion of such content. Note that this is often mistakenly done by new users who are unfamiliar with AfD procedures and such users should be given the benefit of the doubt and pointed to the proper page to discuss the issue.""",
    "Modifying Users Comments"  : """Editing other users comments to substantially change their meaning (e.g. turning someone's vote around), except when removing a personal attack.""",
    "Discussion Page vandalism" : """Blanking the posts of other users from talk pages other than your own, Wikipedia space, and other discussions, aside from removing spam, vandalism, etc., is generally considered vandalism.""",
    "Repeated Uploading of Copyrighted Material" : """Uploading or using material on Wikipedia in ways which violate Wikipedia's copyright policies after having been warned is vandalism. Because users may be unaware that the information is copyrighted, or of Wikipedia policies on how such material may and may not be used, such action ''only'' becomes vandalism if it continues after the copyrighted nature of the material and relevant policy restricting its use have been communicated to the user.""",
    "Malicious Account Creation" : """Creating accounts with usernames that contain deliberately offensive or disruptive terms.""",
    "Hidden Vandalism" : """Any form of vandalism that makes use of embedded text, which is not visible to the final rendering of the article but visible during editing. This includes link vandalism (described above), or placing malicious, offensive, or otherwise disruptive or irrelevant messages or spam in hidden comments for editors to see.""",
    "Gaming The System" : """Deliberate attempts to circumvent enforcement of Wikipedia policies, guidelines, and procedures by making bad faith edits go unnoticed. Includes marking bad faith edits as minor to get less scrutiny, making a minor edit following a bad faith edit so it won't appear on all watchlists, recreating previously deleted bad faith creations under a new title, use of the {{tl|construction}} tag to prevent deletion of a page that would otherwise be a clear candidate for deletion, or use of sock puppets.""",
}



if __name__ == "__main__":
    import unittest, re, pprint

    class DefaultTests(unittest.TestCase):
        def test_labels(self):
            keyed_labels = {}
            for l in labels.keys():
                key = ''.join(re.findall("[A-Z]", l))
                if(key in keyed_labels):
                    print "Duplicate: ", keyed_labels[key], l
                else:
                    keyed_labels[key] = l

        def test_pprint(self):

            int_ids = defaultdict(list)
            for k, l in ids.items():
                for id in l:
                    int_ids[k].append(int(id))
            for v in int_ids.values():
                v.sort()
            print("\nids = \n")
            pprint(int_ids, width=140)

        def test_known_as(self):
            """verify that is_known_as works"""
            test_cases = 0
            for k, l in ids.items():
                for id in l:
                    if not is_known_as(id, k):
                        print "FAILED(a) at k = %s id = %s" % (k, id)
                        self.fail()
                    if is_known_as(id, 'good') and is_known_as(id, 'bad'):
                        print "FAILED(b) at id = %s" % (k, id)
                        self.fail()
                    test_cases += 1
            print "(%d)" % test_cases



import re
keyed_labels = {}
for l in labels.keys():
    key = ''.join(re.findall("[A-Z]", l))
    if(key in keyed_labels):
        print "Duplicate: ", keyed_labels[key], l
    else:
        keyed_labels[key] = l
