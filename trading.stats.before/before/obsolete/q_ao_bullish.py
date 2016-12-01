from trading.data.yahoo import AnalystOpinion
from trading.stats.before.question import Question, main

import os

class AnalystsBullish(Question):
    Abbr = "ao_bullish"
    Min = 2.2
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, ao, strategy):
        if strategy == 'gap_up':
            return ao < self.Min

    def _data_from_db(self):
        ao = self.cache_page('yahoo.AnalystOpinion', AnalystOpinion)
        if not ao.valid:
            return
        if ao.recom_sum is not None:
            this = ao.recom_sum[0][1]
            if this is not None:
                this = float(this)
                return this


if __name__ == '__main__':
    main(AnalystsBullish)
