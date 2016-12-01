from trading.stats.before.question import Strategy, main
from trading.stats.before.q_est_eps_rev_reuters import EPSRevisionsReuters
from trading.stats.before.q_eps_rev_yahoo import EPSRevisionsYahoo

class Analysts(Strategy):
    Abbr = 'anal_rev'
    Questions = [EPSRevisionsReuters,
                 EPSRevisionsYahoo,
                ]

if __name__ == '__main__':
    main(Analysts)
