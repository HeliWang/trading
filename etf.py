from trading.data.yahoo import Quotes
from trading.util import Date

#XXX add dynamic data downloading

class Simulator:
    def __init__ (self, data, amount = 1000, start = None, end = None):
        self.data = data
        self.amount = 1000
        self.start = Date(start) or data.first().date
        self.end = end
        self.shares = 0
        self.worth = 0
        self.spent = 0

    def __call__ (self):
        s0 = self.data.prev_close(self.start)
        last_month = self.start.month
        self.shares = self.amount / s0.close
        while 1:
            s1 = s0.next
            if not s1:
                break
            if last_month != s1.date.month:
                c = self.amount / s1.close
                print "Buying %.2f of shares on %s" % (c, s1.date)
                self.shares += c
                self.spent += self.amount
                last_month = s1.date.month
            s0 = s1
        self.worth = self.data.last().close * self.shares

    def __str__ (self):
        return str(self.__dict__)

if __name__ == '__main__':
    import sys

    raw = open(sys.argv[1]).read()
    data = Quotes(None, None)
    data._init(data = raw)

    s = Simulator(data, start = sys.argv[2])
    s()

    print s
