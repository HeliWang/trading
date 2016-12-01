from trading.data.yahoo import AnalystOpinion
from trading.stats.before.question import Question, main

import os

class BetterWeeklyAO(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Significance = dict(gap_up=2, gap_down=3) #XXX gap_up 1?
    Abbr = "ao_thisweek"

    def answer(self, data, strategy):
        this, last = data
        d = this - last 
        if strategy == 'gap_up':
            return d < -.3
        elif strategy == 'gap_down':
            return d <= .1 and d >= -.1

    def _data_from_db(self):
        ao = self.cache_page('yahoo.AnalystOpinion', AnalystOpinion)
        if not ao.valid:
            return
        if ao.recom_sum is None:
            return
        this = ao.recom_sum[0][1]
        last = ao.recom_sum[1][1]
        if this is not None and last is not None:
            this = float(this)
            last = float(last)
            return this, last

if __name__ == '__main__':
    main(BetterWeeklyAO)
