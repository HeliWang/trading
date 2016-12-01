from trading.stats.before.obsolete.q_stockta_short import StocktaShort, main

class StocktaLong(StocktaShort):
    Abbr = "ta_long"
    Key = 'Long'
    Significance = dict(gap_up=2, gap_down=2)
    Link = "TA"

if __name__ == '__main__':
    main(StocktaLong)
