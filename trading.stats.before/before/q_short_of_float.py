from trading.data.yahoo import Keystats
from trading.stats.before.question import Question, main

import os

class ShortOfFloat(Question):
    Abbr = "short_of_float"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        short_of_float, short_ratio = data
        if strategy == 'gap_up':
            return short_of_float >= 10 and short_ratio >= 10

    def _data_from_db(self):
        ks = self.cache_page('yahoo.Keystats', Keystats)
        if not ks.valid:
            return
        return ks.short_of_float, ks.short_ratio

if __name__ == '__main__':
    main(ShortOfFloat)
