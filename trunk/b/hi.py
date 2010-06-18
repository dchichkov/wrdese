# This python module is a list of obsceneties from the User:ClueBot/Source 
# converted to a python dictionary. It can be shared under Creative Commons
# Attribution-ShareAlike Licence. See also the corpus README file below.
# See: http://en.wikipedia.org/wiki/User:ClueBot/Source
#

import re


# This page contains bad words out of necessity.
# Here is 50 lines of whitespace before the actual list:
# (scroll down to see the list)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# Here is the list:
#

obscenelist =  [
        #('preg'               : points
       (re.compile(r'^suck', re.I)               , -5),          # Usually bad words
       (re.compile(r'honeysuckle', re.I)        , +5),
       (re.compile(r'stupid', re.I)             , -3),
       (re.compile(r'^haha', re.I)               , -5),
       (re.compile(r'hahaha', re.I)               , -5),
       (re.compile(r'^hehe', re.I)               , -5),
       (re.compile(r'hehehe', re.I)               , -5),
       (re.compile(r'^omg', re.I)              , -3),
       (re.compile(r'^pimp$', re.I)           , -7),
       (re.compile(r'^1337$', re.I)               , -5),
       (re.compile(r'^leet$', re.I)               , -5),
       (re.compile(r'^dumb$', re.I)               , -5),
       (re.compile(r'^puta$', re.I)           , -7),
       (re.compile(r'^homo$', re.I)           , -7),
       (re.compile(r'^homos$', re.I)           , -7),
       (re.compile(r'^GAY$')                 , -10),
       (re.compile(r'^slut', re.I)             , -5),
       (re.compile(r'^damn', re.I)               , -5),
       (re.compile(r'^ass$', re.I)                , -10),
       (re.compile(r'^RAPE$')               , -7),
       (re.compile(r'^poop$', re.I)               , -10),
       (re.compile(r'^cock$', re.I)               , -10),
       (re.compile(r'^lol$', re.I)                , -7),
       (re.compile(r'^crap$', re.I)               , -5),
       (re.compile(r'^SEX$')                , -5),
       (re.compile(r'^noob', re.I)               , -5),
       (re.compile(r'^nazi$', re.I)               , -3),
       (re.compile(r'^neo-nazi$', re.I)           , +3),          # False-positive
       (re.compile(r'^fuck', re.I)               , -20),             # Stronger bad words
       (re.compile(r'\[\[Fucked\ Up\]\]', re.I)          , +20),     # This one is a false positive
       (re.compile(r'^bitch', re.I)              , -20),
       (re.compile(r'^pussy$', re.I)              , -20),
       (re.compile(r'penis', re.I)              , -20),
       (re.compile(r'Penisula', re.I)                , +20),         # False Positive
       (re.compile(r'vagina', re.I)             , -20),
       (re.compile(r'whore', re.I)              , -15),
       (re.compile(r'^shit$', re.I)               , -20),
       (re.compile(r'nigger', re.I)             , -20),
       (re.compile(r'^nigga$', re.I)              , -20),
       (re.compile(r'cocksucker', re.I)             , -20),
       (re.compile(r'assrape', re.I)                , -15),
       (re.compile(r'motherfucker', re.I)           , -20),
       (re.compile(r'wanker', re.I)             , -20),
       (re.compile(r'^cunt$', re.I)               , -20),
       (re.compile(r'faggot', re.I)             , -20),
       (re.compile(r'^fags', re.I)               , -20),
       (re.compile(r'asshole', re.I)                , -15),
       (re.compile(r'fuck ((yo)?u|h(er|im)|them|it)', re.I) , -100),        # This looks like a personal attack
       (re.compile(r'((yo)?u|s?he|we|they|it) sucks?', re.I)    , -100),    # This looks like a personal attack
       (re.compile(r'666+$', re.I)             , -50),                      # Though this has uses, it is commonly used by vandals
 
       (re.compile(r'^hi$', re.I)              , -3),
       (re.compile(r'^i$')              , -3),
       (re.compile(r'^yo$', re.I)              , -3),
       (re.compile(r'^my$')              , -1),
       (re.compile(r'^you$')              , -1),
       (re.compile(r'^I$')              , -1),
       (re.compile(r'!!!+')              , -3),

       (re.compile(r'([h-zH-Z]{1,4})\1{3}')    , -3),        # Ugg .. the same letter(s) several times in a row. */       
       (re.compile(r'(.{1,4})\1{10}')    , -6),        # Ugg .. the same letter(s) several times in a row. */
       (re.compile(r'^[A-Z]{5,}$')       , -1),        # All capitals? Looks like vandal activity */
    ]



obscenelist_comment =  [
        #('preg'               : points
       (re.compile(r'\bsuck', re.I)               , -5),          # Usually bad words
       (re.compile(r'honeysuckle', re.I)        , +5),
       (re.compile(r'stupid', re.I)             , -1),
       (re.compile(r'\bhaha', re.I)               , -1),
       (re.compile(r'hahaha', re.I)               , -1),
       (re.compile(r'\bhehe', re.I)               , -1),
       (re.compile(r'hehehe', re.I)               , -1),
       (re.compile(r'\bomg', re.I)              , -3),
       (re.compile(r'\bpimp\b', re.I)           , -7),
       (re.compile(r'\b1337\b', re.I)               , -1),
       (re.compile(r'\bleet\b', re.I)               , -1),
       (re.compile(r'\bdumb\b', re.I)               , -1),
       (re.compile(r'\bputa\b', re.I)           , -7),
       (re.compile(r'\bhomo\b', re.I)           , -7),
       (re.compile(r'\bhomos\b', re.I)           , -7),
       (re.compile(r'\bGAY\b')                 , -10),
       (re.compile(r'\bslut', re.I)             , -5),
       (re.compile(r'\bdamn', re.I)               , -1),
       (re.compile(r'\bass\b', re.I)                , -10),
       (re.compile(r'\bRAPE\b')               , -7),
       (re.compile(r'\bpoop\b', re.I)               , -10),
       (re.compile(r'\bcock\b', re.I)               , -10),
       (re.compile(r'\blol\b', re.I)                , -1),
       (re.compile(r'\bcrap\b', re.I)               , -1),
       (re.compile(r'\bSEX\b')                , -3),
       (re.compile(r'\bnoob', re.I)               , -1),
       (re.compile(r'\bnazi\b', re.I)               , -1),
       (re.compile(r'\bneo-nazi\b', re.I)           , +3),          # False-positive
       (re.compile(r'\bfuck', re.I)               , -3),             # Stronger bad words
       (re.compile(r'\[\[Fucked\ Up\]\]', re.I)          , +20),     # This one is a false positive
       (re.compile(r'\bbitch', re.I)              , -20),
       (re.compile(r'\bpussy\b', re.I)              , -20),
       (re.compile(r'penis', re.I)              , -20),
       (re.compile(r'Penisula', re.I)                , +20),         # False Positive
       (re.compile(r'vagina', re.I)             , -20),
       (re.compile(r'whore', re.I)              , -15),
       (re.compile(r'\bshit\b', re.I)               , -1),
       (re.compile(r'nigger', re.I)             , -20),
       (re.compile(r'\bnigga\b', re.I)              , -20),
       (re.compile(r'cocksucker', re.I)             , -20),
       (re.compile(r'assrape', re.I)                , -15),
       (re.compile(r'motherfucker', re.I)           , -20),
       (re.compile(r'wanker', re.I)             , -20),
       (re.compile(r'\bcunt\b', re.I)               , -20),
       (re.compile(r'faggot', re.I)             , -20),
       (re.compile(r'\bfags', re.I)               , -20),
       (re.compile(r'asshole', re.I)                , -15),
       (re.compile(r'fuck ((yo)?u|h(er|im)|them|it)', re.I) , -100),        # This looks like a personal attack
       (re.compile(r'((yo)?u|s?he|we|they|it) sucks?', re.I)    , -100),    # This looks like a personal attack
       (re.compile(r'666+\b', re.I)             , -50),                      # Though this has uses, it is commonly used by vandals

       (re.compile(r'^hi\b', re.I)              , -3),
       (re.compile(r'^I\b', re.I)              , -1),
       (re.compile(r'\byo\b', re.I)              , -3),
       (re.compile(r'\bmy\b')              , -1),
       (re.compile(r'\byou\b')              , -1),
       (re.compile(r'!!!!!!!!!+')              , -3),

       (re.compile(r'([a-zA-Z]{1,4})\1{5}')    , -1),        # Ugg .. the same letter(s) several times in a row. */
       (re.compile(r'[A-Z ]{5,}$')       , -1),        # All capitals? Looks like vandal activity */


       (re.compile(r'removed', re.I)       , +3),
    ]



