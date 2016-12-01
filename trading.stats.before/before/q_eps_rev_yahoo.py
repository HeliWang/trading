from trading.data.yahoo import AnalystEstimates
from trading.stats.before.question import Question, main
from trading import util

import os

class EPSRevisionsYahoo(Question):
    Abbr = "eps_rev_yahoo"
    CacheFN = '%s.cache' % os.path.splitext(__file__)[0]
    Significance = dict(gap_up=1, gap_down=1)
    Link = "ae"

    def answer(self, data, strategy):
        u, d = 0, 0
        if strategy == 'gap_up':
            # move map(int, ...) to data/yahoo
            u += (sum(map(int, data[1][1:]))*2)
            u += (sum(map(int, data[2][1:]))*1)
            d += (sum(map(int, data[3][1:]))*2)
            d += (sum(map(int, data[4][1:]))*1)
            if u > 3 and d < 2:
                return True
            else:
                return False
        elif strategy == 'gap_down':
            u += (sum(map(int, data[1][1:]))*1)
            u += (sum(map(int, data[2][1:]))*1)
            d += (sum(map(int, data[3][1:]))*1)
            d += (sum(map(int, data[4][1:]))*1)
            return d > 4 and u < 1
            #return d > 6 and u < 1

    def _data_from_db(self):
        ae = self.cache_page('yahoo.AnalystEstimates', AnalystEstimates)
        if not ae.valid:
            return
        for line in ae.eps_rev: #XXX do this in data.yahoo.?
            for i in line[1:]:
                if not i:
                    return
        return ae.eps_rev

if __name__ == '__main__':
    main(EPSRevisionsYahoo)
