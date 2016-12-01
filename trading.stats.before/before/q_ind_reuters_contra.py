from trading.tools.cache import Cache
from trading.stats.before.q_ind_reuters import IndustryReuters, main
from trading import util

cache = Cache()
cache.load_all()

class IndustryReutersContra(IndustryReuters):
    Abbr = 'ind_reuters_contra'
    Significance = dict(gap_up=1)

    def answer(self, data, strategy):
        industry, sector = data
        if industry:
            c = cache.get_category(self.Category, 
                                   industry, 
                                   start_date=(self.date - self.DaysBack),
                                   end_date=(self.date - 1))
            all = util.flatten(*c.values())
            good = filter(lambda x: x.r_eps_surprise(), all)
            if strategy == 'gap_up':
                return len(good) < len(all)*.2 

if __name__ == '__main__':
    main(IndustryReutersContra)
