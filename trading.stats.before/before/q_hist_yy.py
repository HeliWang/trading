from trading.data.earnings import History
from trading.stats.before.question import Question, main
from trading import util

import os

class YYSurprise(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Abbr = "YY_surp"
    Periods = 10
    Significance = dict(gap_up=2, gap_down=3)
    Link = "history"

    def answer(self, data, strategy):
        result = self._compute(data)
        if not len(result) >= 4:
            return
        if strategy == 'gap_up':
            if not sum(result[:4]) == len(result[:4]):
                return False
            if len(filter(lambda x: x == -1, result)) > 1:
                return False
            return True
        elif strategy == 'gap_down':
            #XXX najlepsie vysledky niesu extremy ale pri strede ...
            if sum(result[:4]) > 1:
                return False
            return len(filter(lambda x: x < 1, result)) > 7

    def _data_from_db(self):
        h = self.cache_page('earnings.History', History)
        if not h.valid:
            return
        return h.data

    def _compute(self, data):
        earnings = filter(lambda x: x.date is not None, data)
        earnings = filter(lambda x: x.date < self.date, earnings)
        result = []
        for e in earnings[:self.Periods]:
            if e.act is not None and e.est is not None:
                result.append(cmp(e.act, e.est))
            else:
                result.append(0)
        return result

    def _optimalize(self, data):
        return self._compute(data)

if __name__ == '__main__':
    main(YYSurprise)
