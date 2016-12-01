from trading.data.reuters import Estimates
from trading.stats.before.question import Question, main
from trading import util

import os

class EstBetterReuters(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    MinRevAnalysts = 2
    MinEpsAnalysts = 3
    Significance = dict(gap_down=2, gap_up=3)
    Abbr = "est+reuters"

    def answer(self, data, strategy):
        if data:
            est, hist = data
            rev_no, rev = est[2][1:3]
            eps_no, eps = est[7][1:3]
            rev_old = hist[5][2]
            eps_old = hist[11][2]
            if None in (rev_no, rev, eps_no, eps, rev_old, eps_old):
                return
            rev_old = util.atof(rev_old)
            eps_old = util.atof(eps_old)
            rev_no = int(rev_no)
            eps_no = int(eps_no)
            rev = util.atof(rev)
            eps = util.atof(eps)
            test = (rev_no >= self.MinRevAnalysts and \
                    eps_no >= self.MinEpsAnalysts and \
                    rev > rev_old and eps > eps_old)
            if strategy == 'gap_up': #XXX delete because of poor performance?
                return test
            elif strategy == 'gap_down':
                return not test

    def _data_from_db(self):
        e = self.cache_page('reuters.Estimates', Estimates)
        if not e.valid:
            return
        if not e.est or not e.hist:
            return
        return e.est, e.hist

if __name__ == '__main__':
    main(EstBetterReuters)
