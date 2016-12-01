from trading.stats.before.q_est_better_yahoo import EstBetterYahoo, main
from trading import util

class EstBetterYahooLow(EstBetterYahoo):
    Abbr = "est+yahoo_low"
    Row = 3

if __name__ == '__main__':
    main(EstBetterYahooLow)
