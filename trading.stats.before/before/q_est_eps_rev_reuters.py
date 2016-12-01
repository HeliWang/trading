from trading.data.reuters import Estimates
from trading.stats.before.question import Question, main

import os

class EPSRevisionsReuters(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Abbr = "eps_rev_reuters"
    Row = 8
    Significance = dict(gap_up=1, gap_down=1)
    Link = "ae"

    def answer(self, rev, strategy):
        up = 0
        down = 0
        for line in rev[self.Row:]:
            line = [e is not None and e or 0 for e in line]
            #XXX before 14.10.6 we had four zeros, not only three
            if line == [u'Revenue (in Millions)', 0, 0, 0]: #XXX
                continue
            if line == [u'Revenue', 0, 0, 0]: #XXX
                continue
            if line == ['Earnings', 0, 0, 0]: #XXX
                continue
            if strategy == 'gap_up':
                up += (line[1]*1)
                up += (line[3]*1)
                down += (line[2]*1)
                down += (line[4]*1)
            elif strategy == 'gap_down':
                up += (line[1]*1)
                up += (line[3]*1)
                down += (line[2]*1)
                down += (line[4]*1)
        if strategy == 'gap_up':
            return up > 3 and down < 2
        elif strategy == 'gap_down':
            return up < 1 and down > 3

    def _data_from_db(self):
        e = self.cache_page('reuters.Estimates', Estimates)
        if not e.valid:
            return
        if not len(e.rev) == 12: #XXX move to data.reuters?
            return
        return e.rev

if __name__ == '__main__':
    main(EPSRevisionsReuters)
