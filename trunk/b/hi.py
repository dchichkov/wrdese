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
       (re.compile('^suck', re.I)               , -5),          # Usually bad words
       (re.compile('honeysuckle', re.I)        , +5),
       (re.compile('stupid', re.I)             , -3),
       (re.compile('^haha', re.I)               , -5),
       (re.compile('hahaha', re.I)               , -5),
       (re.compile('^hehe', re.I)               , -5),
       (re.compile('hehehe', re.I)               , -5),
       (re.compile('^omg', re.I)              , -3),
       (re.compile('^pimp$', re.I)           , -7),
       (re.compile('^1337$', re.I)               , -5),
       (re.compile('^leet$', re.I)               , -5),
       (re.compile('^dumb$', re.I)               , -5),
       (re.compile('^puta$', re.I)           , -7),
       (re.compile('^homo$', re.I)           , -7),
       (re.compile('^GAY$')                 , -10),
       (re.compile('^slut', re.I)             , -5),
       (re.compile('^damn', re.I)               , -5),
       (re.compile('^ass$', re.I)                , -10),
       (re.compile('^RAPE$')               , -7),
       (re.compile('^poop$', re.I)               , -10),
       (re.compile('^cock$', re.I)               , -10),
       (re.compile('^lol$', re.I)                , -7),
       (re.compile('^crap$', re.I)               , -5),
       (re.compile('^SEX$')                , -5),
       (re.compile('^noob', re.I)               , -5),
       (re.compile('^nazi$', re.I)               , -3),
       (re.compile('^neo-nazi$', re.I)           , +3),          # False-positive
       (re.compile('^fuck', re.I)               , -20),             # Stronger bad words
       (re.compile('\[\[Fucked\ Up\]\]', re.I)          , +20),     # This one is a false positive
       (re.compile('^bitch', re.I)              , -20),
       (re.compile('^pussy$', re.I)              , -20),
       (re.compile('penis', re.I)              , -20),
       (re.compile('Penisula', re.I)                , +20),         # False Positive
       (re.compile('vagina', re.I)             , -20),
       (re.compile('whore', re.I)              , -15),
       (re.compile('^shit$', re.I)               , -20),
       (re.compile('nigger', re.I)             , -20),
       (re.compile('^nigga$', re.I)              , -20),
       (re.compile('cocksucker', re.I)             , -20),
       (re.compile('assrape', re.I)                , -15),
       (re.compile('motherfucker', re.I)           , -20),
       (re.compile('wanker', re.I)             , -20),
       (re.compile('^cunt$', re.I)               , -20),
       (re.compile('faggot', re.I)             , -20),
       (re.compile('^fags', re.I)               , -20),
       (re.compile('asshole', re.I)                , -15),
       (re.compile('fuck ((yo)?u|h(er|im)|them|it)', re.I) , -100),        # This looks like a personal attack
       (re.compile('((yo)?u|s?he|we|they|it) sucks?', re.I)    , -100),    # This looks like a personal attack
       (re.compile('666+$', re.I)             , -50),                      # Though this has uses, it is commonly used by vandals
       
       #(re.compile('(.{1,4})\1{20}')          , -10),        # Ugg .. the same letter(s) several times in a row. */
       #(re.compile('[A-Z][^a-z]{20,}')        , -10),        # All capitals? Looks like vandal activity */

    ]
    
    
