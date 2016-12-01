from trading import util
import random

class Tester:
    "MM tester"

    def __init__(self, cash = 15000,
                       commissions = 3,
                       win_ratio = .7,
                       max_win_loss = .15
                       ):
            self.cash = cash
            self.init_cash = cash
            self.commissions = commissions
            self.win_ratio = win_ratio
            self.max_win_loss = max_win_loss
            self._runs = []

    def position(self):
        return self.cash / 3

    def run(self, count):
        # print "R", "%2d" % (a + 1), "%.2f" % self.cash, "%5d" % change, "%.2f%%" % (pct * 100)
        self.cash = self.init_cash
        for a in range(100):
            self._run(count)
            self._runs.append(self.cash)

    def _run(self, count):
        for a in range(count):
            change_pct = random.random() * self.max_win_loss
            change = self.position() * change_pct - self.commissions
            sign = self.sign()
            change *=  sign
            self.cash += change
            return change, change_pct

    def sign(self):
        if random.random() >= self.win_ratio:
            return -1
        return 1

    def __str__(self):
        total = 0
        for r in self._runs:
            total += r
        return """init_cash          : %.2f 
win_ratio          : %s%%
max_win or max_loss: %s%%
commissions        : %d
success            : %.2f
min                : %.2f
q25                : %.2f%%
mean               : %.2f
median             : %.2f
q75                : %.2f%%
max                : %.2f""" % (self.init_cash, 
                              self.win_ratio * 100, 
                              self.max_win_loss * 100, 
                              self.commissions,
                              ((total / len(self._runs))/self.init_cash-1)*100,
                              min(self._runs),
                              (util.quantile(self._runs, .25) / self.init_cash - 1) * 100,
                              util.mean(self._runs),
                              util.median(self._runs),
                              (util.quantile(self._runs, .75) / self.init_cash - 1) * 100,
                              max(self._runs)
                              )

if __name__ == "__main__":
    c = 30
    t = Tester()
    print c
    print
    t.run(c)
    print t
