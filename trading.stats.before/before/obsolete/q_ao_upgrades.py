from trading.data.marketwatch import AnalystUpgrades
from trading.stats.before.question import Question, main

import os

class Upgrades(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Abbr = "ao_upgrades"
    DaysBack = 20

    def answer(self, ao, strategy):
        if strategy == 'gap_up':
            up = filter(lambda x: x.date > self.date - self.DaysBack, ao.up)
            down = filter(lambda x: x.date > self.date - self.DaysBack, ao.down)
            return len(up) > 0

    def _data_from_db(self):
        ao = self.cache_page('marketwatch.AnalystUpgrades', AnalystUpgrades)
        if not ao.valid:
            return
        return ao

if __name__ == '__main__':
    main(Upgrades)
