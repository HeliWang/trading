from trading.stats.before.q_basic_price import Basic, main

class Volume(Basic):
    Abbr = "volume"
    Min = 30000
    Max = None
    SummaryKey = 'Avg Vol (3m)'

if __name__ == '__main__':
    main(Volume)
