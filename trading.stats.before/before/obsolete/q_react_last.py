from trading.stats.before.q_react_8period import Reactions8P, main

class LastReaction(Reactions8P):
    Abbr = 'react_last'

    def answer(self, data, strategy):
        if data:
            if strategy == 'gap_up':
                return data[0] > -1

if __name__ == '__main__':
    main(LastReaction)
