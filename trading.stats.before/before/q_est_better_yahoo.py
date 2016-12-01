from trading.data.yahoo import AnalystEstimates
from trading.stats.before.question import Question, main
from trading import util

import os

class EstBetterYahoo(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Abbr = "est+yahoo"
    Significance = dict(gap_up=3, gap_down=2)
    Row = 1

    def answer(self, ae, strategy):
        rev = ae.rev_est[self.Row][1]
        rev_old = ae.rev_est[5][1]
        eps = ae.eps_est[self.Row][1]
        eps_old = ae.eps_est[5][1]
        if eps is not None and eps_old is not None and rev is not None and rev_old is not None:
            eps = float(eps)
            eps_old = float(eps_old)
            rev = util.atof(rev)
            rev_old = util.atof(rev_old)
            if strategy == 'gap_up': #XXX poor performance. delete?
                return eps > eps_old and rev > rev_old
            elif strategy == 'gap_down':
                return eps <= eps_old and rev <= rev_old

    def _data_from_db(self):
        ae = self.cache_page('yahoo.AnalystEstimates', AnalystEstimates)
        if not ae.valid:
            return
        return ae

if __name__ == '__main__':
    main(EstBetterYahoo)
