from trading.stats.before.q_basic_price import Basic, main

class Cap(Basic):
    Abbr = "cap"
    Min = 50000000
    Max = None
    SummaryKey = 'Market Cap'

if __name__ == '__main__':
    main(Cap)
