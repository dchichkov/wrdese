## Labels ##
  * 'bad' - automatically identified edits that generally require a revert (some human verified)
  * 'good' - automatically identified good faith edits (some human verified)

Additional extra information (revisions in these lists are already in the 'good' or 'bad'):
  * 'good (corrected by user)' - good edits (automatically identified, corrected by a human)
  * 'constructive (corrected by user)' - good edits, questionably good edits, partial vandalism reverts, etc. (human corrections)
  * 'bad (corrected by user)' - bad edits (automatically identified, corrected by a human)
  * 'bad (verified by user)' - bad edits (automatically identified, verified by a human)
  * 'good (verified by user)' - good edits (automatically identified, verified by a human)

## Usage ##
Add following URL before the revision ID to see the diff:
```
http://en.wikipedia.org/w/index.php?diff=
```

Example:
[http://en.wikipedia.org/w/index.php?diff=7267547](http://en.wikipedia.org/w/index.php?diff=7267547)

In python you can execute this data set as a code and get a dictionary of sorted revisions lists. Here is an example that prints html refs to the Wikipedia diffs for the 'bad' revisions:
```
for r in ids['bad']:
    print '<a href="http://en.wikipedia.org/w/index.php?diff=%d">%d</a>' % (r, r)
```


There is also a helper python module available: http://wrdese.googlecode.com/svn/trunk/b/k.py that provides is\_good\_or\_bad helper routines.