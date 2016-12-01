from trading.stats.before.question import MultiQuestion, main

from trading.stats.before.q_ao_targetprice import TargetPrice
from trading.stats.before.q_eps_rev_yahoo import EPSRevisionsYahoo
from trading.stats.before.q_ao_thisweek import BetterWeeklyAO
from trading.stats.before.q_insiders_purchases import InsidersPurchases
from trading.stats.before.q_insiders_accum import InsidersAccumulation
from trading.stats.before.q_inst_shares import InstitutionsShares
from trading.stats.before.q_inst_shares2 import InstitutionsShares2
from trading.stats.before.q_inst_shares3 import InstitutionsShares3
from trading.stats.before.q_est_eps_rev_reuters import EPSRevisionsReuters
from trading.stats.before.q_est_rev_rev_reuters import RevRevisionsReuters
from trading.stats.before.q_react_8period import Reactions8P
from trading.stats.before.q_ind_reuters_contra import IndustryReutersContra
from trading.stats.before.q_ind_yahoo_contra import IndustryYahooContra
from trading.stats.before.q_stockta_long import StocktaLong
from trading.stats.before.q_ind_reuters import IndustryReuters
from trading.stats.before.q_hist_yy import YYSurprise
from trading.stats.before.q_hist_analyst import AnalystSurprise
from trading.stats.before.q_options import Options
from trading.stats.before.q_options2 import Options2
from trading.stats.before.q_est_better_reuters import EstBetterReuters
from trading.stats.before.q_inst_holders import InstitutionsHolders
from trading.stats.before.q_inst_holders_contra import InstitutionsHoldersContra

from trading.stats.before.q_basic_price import Price
from trading.stats.before.q_basic_volume import Volume
from trading.stats.before.q_basic_cap import Cap
from trading.stats.before.q_basic_market import Market

class All(MultiQuestion):
    Questions = [EPSRevisionsYahoo, 
                 InsidersAccumulation, 
                 TargetPrice,
                 InstitutionsShares, 
                 InstitutionsShares2, 
                 InstitutionsShares3, 
                 Reactions8P,
                 EPSRevisionsReuters, 
                 InsidersPurchases,
                 StocktaLong, 
                 IndustryReutersContra, 
                 IndustryYahooContra,
                 Options,
                 InstitutionsHolders,
                 IndustryReuters,
                 YYSurprise, 
                 InstitutionsHoldersContra,
                 RevRevisionsReuters,
                 AnalystSurprise, 
                 #EstBetterReuters, #XXX because of BOT:17.10.6
                 BetterWeeklyAO, 
                 Options2,
          ]

if __name__ == '__main__':
    main(All)
