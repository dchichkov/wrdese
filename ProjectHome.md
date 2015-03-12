## wpcvn ##
[WPCVN](http://wpcvn.com/) - yet another collaborative (it shows other users actions - patrols and reverts) Web 2.0 RC patrol tool that runs in a browser. It has been tested with Firefox, IE and Google Chrome. Currently operates for en-wiki only in the alpha testing|alpha mode. WPCVN aggregates recent changes IRC feed, IRC feed from the MiszaBot and WPCVN user actions. It also uses pre-calculated Wikipedia users "karma" (based on the recent en-wiki dump analysis) to separate edits made by users with clearly good or bad reputation. The tool is open source (LGPL) and uses JQuery/JQueryUI + Django backend.

## pymwdat ##
If you are looking for some MediaWiki Dump Analysis python code go to:
http://code.google.com/p/pymwdat/

## wrdese ##
This code. Internal/current sandbox/experiments code. I must warn you, that I haven't really tried to clean up that code and when I was writing it, I was concentrating on a get-results-quick-and-dirty approach, rather than on designing beautiful and reusable code.


In the single page history or full wikipedia history dump (.xml/.7z):
  * Detects reverts, reverted edits, revert wars.
  * Calculates users/page counters, revert rates, page diffs, ets (~1 week/C2Duo/Full Wikipedia dump).
  * Filtering, labeled revisions data sets management, etc;
  * Uses CRM114/MaxEnt/decissiontree (text categorization engine to detect bad/good edits;
  * Assists in the verification by a human;
  * Calculates statistics;
  * Calculates tokens 'lifetime' statistics. Can be used to differentiate between ham/spam tokens/edits.

  * Language/libraries: python, pywikipedia, pysci, nltk, megam, crm114, etc
  * Installation: see http://code.google.com/p/wrdese/wiki/Installation
  * Common commands: http://code.google.com/p/wrdese/source/browse/trunk/b/README