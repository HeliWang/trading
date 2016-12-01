from trading import util
from termcolor import term

class _Interval:

    def __init__(self, start_date):
        start_date = start_date.date_obj()
        self.start_date = start_date
        self.end_date = None
        self.data = [] #= list of tuples: (signal, %gain)
        self.Table[self.start_date] = self

    def add(self, signal, result, data, date):
        self.data.append((signal, result, data, date))
        self.end_date = date

    def is_new(self, other_date):
        "do we need to create a new interval because other doesn't belong here?"
        raise NotImplementedError

    def _tag(self):
        raise NotImplementedError

    def print_(self, verbosity):
        class_name = self.__class__.__name__
        if (class_name == 'Week' and 'w' in verbosity) or \
           (class_name == 'Day' and 'd' in verbosity) or \
           (class_name == 'Month' and 'm' in verbosity):
            def _print(tag, data):
                def pct(seq, winners):
                    result = 0
                    if seq:
                        result = (100./len(seq))*winners
                    return result

                eps_winners = len(filter(lambda x: x[1].r_eps_surprise(), data))
                eps_pct = pct(filter(lambda x: x[1].r_eps_surprise() is not None, data), eps_winners)
                rev_winners = len(filter(lambda x: x[1].r_rev_surprise(), data))
                rev_pct = pct(filter(lambda x: x[1].r_rev_surprise() is not None, data), rev_winners)
                gain_winners = len(filter(lambda x: x[1].gain > 0, data))
                gain_pct = pct(filter(lambda x: x[1].gain is not None, data), gain_winners)
                gain2_winners = len(filter(lambda x: x[1].gain2 > 0, data))
                gain2_pct = pct(filter(lambda x: x[1].gain2 is not None, data), gain2_winners)

                total = len(data)
                losers = len(filter(lambda x: x[1].gain < 0, data))
                winners = total - losers
                data = map(lambda x: x[1].gain, data)
                mean = util.mean(data, geometric=True)
                
                if not data or mean is None:
                    print "%s: N/A" % tag
                else:
                    if mean > 0:
                        color = term.GREEN
                    else:
                        color = term.RED

                    print "%s:"% (tag + color),
                    print total, winners, losers, \
                          term.BOLD + ("(%.2f%%)" % gain_pct), \
                          term.NORMAL + color + "%.2f" % min(data), \
                          "%.2f" % util.quantile(data, f=.25), \
                          term.BOLD + "%.2f" % util.median(data), \
                          "%.2fg {%.2f}" % (mean, util.mean(data)), \
                          term.NORMAL + color + "%.2f" % util.quantile(data, f=.75), \
                          ("%.2f" % max(data)), \
                          "[%.2f%% %.2f%% %.2f%%]" % (eps_pct, rev_pct, gain2_pct), \
                          "" + term.NORMAL

            data = filter(lambda x: x[1].gain is not None, self.data)
            print self._tag(),
            _print("strategy", filter(lambda x: x[0] is True, data)) 
            print self._tag(),
            _print("  market", data)


class Day(_Interval):
    Table = {}

    def _tag(self):
        return "D %s" % self.start_date.date_str()

    def is_new(self, other):
        s = self.start_date.date_str() 
        o = other.date_str()
        if s == o:
            return False
        return True

class Week(_Interval):
    Table = {}

    def _tag(self):
        d = self.start_date
        return "W (%s-%s) %s/%s" % ((d.next_week()-7).strftime('%d'), 
                                    (d.next_week()-1).strftime('%d.%b'),
                                    d.strftime("%W"), 
                                    d.year)

    def is_new(self, o):
        return self.start_date.next_week() != o.next_week() or \
               self.start_date.year != o.year


class Month(_Interval):
    Table = {}

    def _tag(self):
        return "M %s/%s" % (self.start_date.month, self.start_date.year)

    def is_new(self, other):
        if self.start_date.month != other.month and self.start_date.date_str() != other.date_str():
            return True
        return False

class Summary:

    def __init__(self, verbosity="dwm"):
        self.day = None
        self.week = None
        self.month = None
        self.verbosity = verbosity

    def add(self, signal, result, data, date):
        if self.day is None:
            self.day = Day(date)
        if self.week is None:
            self.week = Week(date)
        if self.month is None:
            self.month = Month(date)
        # day
        if self.day.is_new(date):
            self.day.print_(self.verbosity)
            self.day = Day(date)
        self.day.add(signal, result, data, date)
        # week
        if self.week.is_new(date):
            self.week.print_(self.verbosity)
            self.week = Week(date)
        self.week.add(signal, result, data, date)
        # month
        if self.month.is_new(date):
            self.month.print_(self.verbosity)
            self.month = Month(date)
        self.month.add(signal, result, data, date)

    def finish(self):
        self.week.print_(self.verbosity)
        self.month.print_(self.verbosity)

    def optimalize(self):
        all = []
        for day in Day.Table.values():
            all.extend(day.data)
        all.sort(lambda x, y: cmp(x[1].gain, y[1].gain))
        all.reverse()
        for i in all:
            signal, result, data, date = i
            #if not data: #XXX
            #    continue
            if not signal:
                continue
            if type(data) is tuple:
                print 'O %s' % str(data)
            else:
                print 'O %s' % data
            print 'O %d %6s %.2f %.2f %s' % \
                (signal and 1 or 0,
                 result.name, 
                 result.gain, 
                 result.gain2, 
                 result.rel_date.datetime_str(), 
                )
        all_signals = filter(lambda x: x[0], all)
        print " ".join(map(lambda x: "%s:%s" % (x[1].name.upper(), x[3].date_str()), all_signals))
