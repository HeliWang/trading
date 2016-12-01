from trading.tools.cache import Cache
from trading.data.yahoo import Profile
from trading.stats.before.question import Question, main
from trading import util

import os

cache = Cache()
cache.load_all()

class IndustryYahooContra(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Category = 'yahoo_industry'
    DaysBack = 30
    SurpriseFactor = .15
    Abbr = "ind_yahoo_contra"
    Significance = dict(gap_up=2)
    Link = "industry"

    def answer(self, data, strategy):
        industry, sector = data
        if industry:
            c = cache.get_category(self.Category, industry, 
                                   start_date=(self.date - self.DaysBack), 
                                   end_date=(self.date - 1))
            all = util.flatten(*c.values())
            good = filter(lambda x: x.r_eps_surprise(), all) 
            if strategy == 'gap_up':
                return len(good) < len(all)*self.SurpriseFactor

    def _data_from_db(self):
        p = self.cache_page('yahoo.Profile', Profile)
        if not p.valid:
            return
        return p.industry, p.sector

    def _optimalize(self, data):
        return #list(data)

if __name__ == '__main__':
    main(IndustryYahooContra)
