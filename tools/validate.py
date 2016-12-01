from trading import util
from trading.tools import fetch

import os

if __name__ == "__main__" :
    from optparse import OptionParser

    usage = "%prog [options] dir1 ... dirN"
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--day',  type="int", default=-1)
    parser.add_option('-l', '--logfile',  default="../validate.log")
    parser.add_option('-o', '--ignoreoptions',  default=False,
        action="store_true")
    opts, args = parser.parse_args()

    dirs_done = []
    if os.path.exists(opts.logfile):
        dirs_done = [l.strip() for l in open(opts.logfile).readlines() if l]

    log = file(opts.logfile, 'a')

    for dir in args:
        if dir.endswith('/'):
            dir = dir[:-1]
        if dir in dirs_done:
            continue
        print "checking: %s" % dir
        symbol = os.path.split(os.path.split(dir)[0])[-1]
        pages = fetch.page_list(opts.day, dir, symbol, util.now() - 1)
        is_ok = True
        for p in pages:
            if not p.is_cached():
                print "missing: ", dir, symbol, "%s.%s" % (p.__class__.__module__, p.__class__.__name__)
                if opts.ignoreoptions and (p.__class__.__name__ == 'Options'):
                    continue
                is_ok = False
            try:
                p.init()
            except NotImplementedError:
                pass
            except Exception:
                print "*** Exception while processing: %s ***" % p.cache_fn(abs=True)
                raise
        if is_ok:
            print >> log, dir
            log.flush()

    log.close()
