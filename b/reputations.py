import marshal
from time import time
from collections import defaultdict

def read_reputations(_reputations_arg):
    print("Reading %s..." % _reputations_arg)
    FILE = open(_reputations_arg, 'rb')
    user_reputations = defaultdict(int)
    start = time()
    try:
        while True:
            (u,r) = marshal.load(FILE)
            user_reputations[u] += r
    except IOError, e:
        raise
    except EOFError, e:
        print("Done reading %s. Read time: %f. Total users: %d" % (_reputations_arg, time() - start, len(user_reputations)))
    return user_reputations

