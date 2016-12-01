from trading.stats.before.obsolete.q_stockta_short import StocktaShort, main

class StocktaInter(StocktaShort):
    Abbr = "ta_inter"
    Key = 'Intermediate'

if __name__ == '__main__':
    main(StocktaInter)
