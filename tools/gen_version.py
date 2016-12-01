from trading import util

import os
import shutil
import tempfile

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "%prog [options] <output_dir> <TAG> file1 ... fileN"
    parser = OptionParser(usage=usage)
    opts, args = parser.parse_args()

    if len(args) < 2:
        parser.error("please set correct arguments")
    output_dir = args[0]
    version = args[1]
    files = args[2:]
    if os.path.exists(output_dir):
        parser.error('output_dir (%s) must not exist' % output_dir)
    util.mkdir(output_dir)

    tmp_fn = tempfile.mktemp()
    for fn in files:
        cmd = 'preprocess -D %s -o %s %s' % (version, tmp_fn, fn)
        print cmd
        os.system(cmd)
        if os.path.exists(tmp_fn):
            dir, rest = os.path.split(fn)
            new_dir = os.path.join(output_dir, dir)
            new_fn = os.path.join(new_dir, rest)
            os.system('mkdir -p %s' % new_dir) #XXX not portable (so WTF)
            util.debug('move: %s -> %s' % (tmp_fn, new_fn))
            shutil.move(tmp_fn, new_fn)
