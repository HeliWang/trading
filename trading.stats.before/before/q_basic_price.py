from trading.data.yahoo import Summary
from trading.stats.before.question import Question, main

import os

class Basic(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    SummaryKey = None

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            val = data.summary.get(self.SummaryKey)
            if val is not None:
                result = True
                if self.Min is not None and val < self.Min:
                    result = False
                if self.Max is not None and val > self.Max:
                    result = False
                return result

    def _data_from_db(self):
        s = self.cache_page('yahoo.Summary', Summary)
        if not s.valid:
            return
        return s

    def _optimalize(self, data):
        return data.summary.get(self.SummaryKey)


class Price(Basic):
    Abbr = "price"
    Min = 5
    Max = None
    SummaryKey = 'Last Trade'

if __name__ == '__main__':
    main(Price)
