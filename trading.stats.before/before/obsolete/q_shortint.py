from trading.data.nasdaq import ShortInterest
from trading.stats.before.question import Question, main
from trading import indicator

import os

class ShortInt(Question):
    Abbr = "short_int"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            if len(data) > 1:
                ema = indicator.ema(map(lambda x: x.shares, data))
                return data[0].shares < data[1].shares

    def _data_from_db(self):
        s = self.cache_page('nasdaq.ShortInterest', ShortInterest)
        if not s.valid:
            return
        return s.data

    def _optimalize(self, data):
        if data:
            shares = map(lambda x: x.shares, data)
            ratio = map(lambda x: x.ratio, data)
            if None not in ratio and None not in shares:
                return [indicator.ma(shares)] + [indicator.ma(ratio)] + data

if __name__ == '__main__':
    main(ShortInt)
