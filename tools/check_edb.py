from trading import util
from trading import config

import os

min_compression = 8

if __name__ == "__main__":
    parser = util.from_to_parser()
    parser.add_option('-c', '--check_compression', 
                      action='store_true', default=False)
    parser.add_option('-i', '--check_integrity', 
                      action='store_true', default=False)
    parser.add_option('-v', '--verbose',
                      action='store_true', default=False)
    opts, args = parser.parse_args()

    if not opts.check_integrity and not opts.check_compression:
        parser.error("nothing to do")

    dates = util.db_dates(begin=opts.begin_date, end=opts.end_date)
    for d in dates:
        for fn in os.listdir(os.path.join(config.DB_DIR, d)):
            absfn = os.path.join(config.DB_DIR, d, fn)
            if opts.verbose:
                print "checking: %s" % absfn
            if opts.check_integrity:
                z = util.ZipFile(absfn, mode='r')
                bad = z.testzip()
                if bad:
                    print "invalid archive: %s" % absfn
                    print "invalid file: %s" % bad
                    raise SystemExit
                z.close()
            if opts.check_compression:
                tofix = {}
                z = util.ZipFile(absfn, mode='r')
                for e in z.infolist():
                    if e.compress_type < min_compression:
                        print "insufficient compression: %s" % absfn
                        print "fix: %s (%d)" % (e.filename, e.compress_type)
                        data = z.read(e.filename)
                        tofix[e.filename] = data
                z.close()
                for _fn, data in tofix.items():
                    util.ZipFile.Replace(absfn, _fn, data)
