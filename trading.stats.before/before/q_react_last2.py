from trading.stats.before.q_react_8period import Reactions8P, main

class LastReaction2P(Reactions8P):
    Abbr = 'react_last2'
    Significance = dict(gap_down=2)

    def answer(self, data, strategy):
        if len(data) >= 2:
            if strategy == 'gap_down':
                return data[0] < -3 and data[1] < -3

if __name__ == '__main__':
    main(LastReaction2P)
