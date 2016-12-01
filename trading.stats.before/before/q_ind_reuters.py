from trading.tools.cache import Cache
from trading.data.reuters import Estimates
from trading.stats.before.question import Question, main
from trading import util

import os

cache = Cache()
cache.load_all()

class IndustryReuters(Question):
    Abbr = "ind_reuters"
    Category = 'reuters_industry'
    DaysBack = 30
    Significance = dict(gap_up=1)
    Link = "industry"

    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]

    def answer(self, data, strategy):
        industry, sector = data
        if industry:
            c = cache.get_category(self.Category, 
                                   industry, 
                                   start_date=(self.date - self.DaysBack),
                                   end_date=(self.date - 1))
            all = util.flatten(*c.values())
            #good = filter(lambda x: x.r_eps_surprise(), all)
            good = filter(lambda x: x.e_eps_surprise(), all)
            if strategy == 'gap_up':
                return len(good) > len(all)*.75 and len(good) < len(all)*.90

    def _data_from_db(self):
        e = self.cache_page('reuters.Estimates', Estimates)
        if not e.valid:
            return
        i = e.industry
        s = e.sector
        #XXX unless str() is used shelve will break because of UTF being used...
        if i:
            i = str(i)
        if s:
            s = str(s)
        return i, s 

    def _optimalize(self, data):
        return 

if __name__ == '__main__':
    main(IndustryReuters)
