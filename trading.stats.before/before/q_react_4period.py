from q_react_8period import Reactions8P, main
from trading import util

class Reactions4P(Reactions8P):
    Abbr = "react_4p"
    Significance = dict(gap_down=2)

    def answer(self, data, strategy):
        if not data:
            return
        data = data[:4]
        if strategy == 'gap_up':
            return
        elif strategy == 'gap_down':
            return sum(data) > 20  and data[0] > 8 #XXX magic

if __name__ == '__main__':
    main(Reactions4P)
