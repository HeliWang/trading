from trading.stats.before.q_basic_price import Basic, main

class Market(Basic):
    Abbr = "market"
    MarketName = 'NYSE'

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            return data.market.lower().startswith(self.MarketName.lower())

    def optimalize(self, data):
        return data.market

if __name__ == '__main__':
    main(Market)
