from trading.data.earnings import History
from trading.data.yahoo import Quotes
from trading.stats.before.question import Question, main
from trading import indicator

import os

def ema(data):
    #raise NotImplementedError # this is buggy and unused XXX
    """
    >>> ema([1,0,1,1])
    1.75
    >>> ema([1,1,1,1])
    2.5
    >>> ema([1,1])
    1.5
    """
    if not data:
        return 0
    total = 1
    step = 1./len(data)
    result = 0
    for i, d in enumerate(data):
         result += total*d
         total -= step
    return result/len(data)



class Reactions8P(Question):
    Periods = 8
    DaysBack = 2.5*360
    Abbr = "react_8p"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    MinGain = .5
    Significance = dict(gap_up=1, gap_down=1) 
    Link = "history"

    def answer(self, data, strategy):
        if not data:
            return
        e = ema(data)
        if strategy == 'gap_up':
            # ziadne velke diskrepancie
            if e/1.5 > sum(data) or e*2.5 < sum(data): #XXX magic constant
                return False
            # ziadnych loserov
            if len(data) >= 2 and (data[0] < self.MinGain or data[1] < self.MinGain):
                return False
            # neprehriate akcie
            return e < 14 #XXX magic constant
        elif strategy == 'gap_down':
            return len(filter(lambda x: x <= -.5, data)) > 6 #XXX magic

    def _data_from_db(self):
        h = self.cache_page('earnings.History', History)
        q = self.cache_page('yahoo.Quotes', Quotes)
        if not h.valid or not q.valid:
            return
        data = filter(lambda x: x.date is not None and x.date < self.date, h.data)
        data = filter(lambda x: x.date > (self.date - self.DaysBack), data)
        data = [float(e.reaction(q)) for e in data[:self.Periods] \
                if e.reaction(q) is not None]
        return data

    def _optimalize(self, data):
        if data:
            data = data[:4]
            e = ema(data)
            s = sum(data)
            r = 0
            if e:
                r = s/e
            fmt = "%.2f"
            return [fmt % e, fmt % s, fmt % r] + map(lambda x : fmt % x, data)

if __name__ == '__main__':
    main(Reactions8P)
