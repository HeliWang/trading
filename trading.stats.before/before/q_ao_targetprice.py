from trading.data.yahoo import AnalystOpinion, Summary
from trading.stats.before.question import Question, main

import os

class TargetPrice(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Significance = dict(gap_down=3)
    Abbr = "ao_target_price"

    def answer(self, data, strategy):
        price, targets = data
        if strategy == 'gap_down':
            if targets['Mean Target'] is not None:
                return price *.6 > targets['Mean Target'] 
        #XXX gap_up?

    def _data_from_db(self):
        ao = self.cache_page('yahoo.AnalystOpinion', AnalystOpinion)
        s = self.cache_page('yahoo.Summary', Summary)
        if not ao.valid or not s.valid:
            return
        if ao.target_sum is None:
            return
        price = s.summary['Last Trade']
        return price, ao.target_sum

if __name__ == '__main__':
    main(TargetPrice)
