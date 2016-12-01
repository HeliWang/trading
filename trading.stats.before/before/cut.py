if __name__ == '__main__':
    from optparse import OptionParser

    usage = "%prog [options]"
    parser = OptionParser(usage=usage)
    opts, args = parser.parse_args()

    # check options
    for arg in args:
        for line in file(arg).xreadlines():
            if line.startswith('V '):
                tokens = line.split()
                if int(tokens[2]):
                    print tokens[3]
