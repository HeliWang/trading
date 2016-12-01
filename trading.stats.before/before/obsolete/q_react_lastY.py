from trading.stats.before.q_react_8period import Reactions8P, main

class LastYearReaction(Reactions8P):
    Abbr = 'react_lastY'
    Periods = 1
    MinGain = 0

    def answer(self, data, strategy):
        if strategy == 'gap_up':
            if len(data) >= 4*self.Periods:
                result = True
                for reaction in data[3:self.Periods*4:4]:
                    if reaction is None or float(reaction) < self.MinGain:
                        result = False
                return result

if __name__ == '__main__':
    main(LastYearReaction)
