from trading.stats.before.question import Strategy, main
from trading.stats.before.q_hist_yy import YYSurprise
from trading.stats.before.q_hist_analyst import AnalystSurprise
from trading.stats.before.q_basic_price import Price
from trading.stats.before.q_basic_volume import Volume
from trading.stats.before.q_basic_cap import Cap
from trading.stats.before.q_est_better_reuters import EstBetterReuters

class Juggler(Strategy):
    Abbr = 'juggler'
    Questions = [YYSurprise, AnalystSurprise, 
                 Volume, Cap,
                 EstBetterReuters,
                ]

    #def signal(self, answers):
    #    return answers == [0, 1, 1, 1, 1] or answers == [1, 0, 1, 1, 1] or \
    #           answers == [1, 1, 1, 1, 1]

if __name__ == '__main__':
    main(Juggler)
