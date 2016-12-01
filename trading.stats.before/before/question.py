from trading.tools.cache import Cache
from trading.stats.before.summary import Summary
from trading import util
from trading import config
from trading.htmlgen import font, T

from mx.DateTime import TimeDelta #XXX factorize is_amc ...

from termcolor import term

import os
import sys
import shelve
import inspect
import traceback

class Question(object):
    Abbr = None
    CacheFN = None
    ValidStrategies = ('gap_down', 'gap_up')
    Significance = dict(gap_down=3, gap_up=3) # 1 - 3; 1 is best.
    When = 'bia' #= BMO, INTRADAY, AMC
    Link = None

    def answer(self, data, strategy):
        raise NotImplementedError

    def _data_from_db(self):
        raise NotImplementedError

    def __init__(self, directory, date, symbol, pages):
        self.root_dir = directory
        self.date = date
        self.symbol = symbol
        self.pages = pages
        self.dir = os.path.join(directory, date.date_str(), symbol, '-1')
        self._cache = None # cache with results data
        if self.CacheFN is not None:
            self._cache = shelve.open(self.CacheFN)

    def _precondition(self):
        result = os.path.exists(self.dir)
        if not result:
            print "%s: %s does not exist" % (self.symbol, self.dir)
        return result

    def _postcondition(self, answer):
        assert answer in (True, False, None), answer

    def ask_html(self, strategy):
        _, answer, _ = self.ask(strategy)
        bold = False
        color = None
        if answer is True:
            i = self.Significance[strategy]
            color = None
            if strategy == 'gap_down':
                color = 'red'
            elif strategy == 'gap_up':
                color = 'blue'
            text = font(self.Abbr, color=color, size=11)
            if i == 1:
                text = font(self.Abbr, color=color, size=14, bold=True)
        html = font(text, color=color, bold=bold)
        if self.Link:
            html = T.a(html, href="%s/index.html#%s" % (self.symbol, self.Link))
        return html
       
    def ask(self, strategy):
        assert strategy in self.ValidStrategies
        answer = None
        data = None
        if self._precondition():
            data = self._data()
            if data is not None:
                answer = self.answer(data, strategy)
            self._postcondition(answer)
        optimalized = None
        if data:
            optimalized = self._optimalize(data)
        return [], answer, optimalized

    def cache_page(self, key, cls):
        page = util.cache_page(self.pages, key, cls, self.dir, self.symbol)
        if not page.valid:
            print "%s: invalid %s (Question: %s)" % \
                (self.symbol, key, self.Abbr)
        return page

    def _optimalize(self, data):
        return data

    def _data(self):
        result = None
        key = "%s;%s" % (self.date.date_str(), self.symbol)
        if self._cache is not None:
            #print key, self.Abbr #XXX
            result = self._cache.get(key)
        if result is None:
            result = self._data_from_db() #XXX comment out to use cache only
            if self._cache is not None:
                self._cache[key] = result
        return result


class MultiQuestion(Question):
    Questions = []

    def ask(self, strategy):
        answers = []
        pages = {}
        if self._precondition():
            for Q in self.Questions:
                _, answer, _ = Q(self.root_dir, 
                                 self.date, 
                                 self.symbol, 
                                 self.pages).ask(strategy)
                self._postcondition(answer)
                answers.append(answer)
        else:
            print "Precondition not met: %s" % self
            answers = [None] * len(self.Questions)
        return answers, None, None

class Strategy(MultiQuestion):

    def signal(self, answers):
        return filter(None, answers) == answers

    def ask(self, *args, **kw):
        answers, _, _ = super(Strategy, self).ask(*args, **kw)
        signal = self.signal(answers)
        self._postcondition(signal)
        return answers, signal, None

def print_answer(symbol, answers, signal, result, sep):
    color = ""
    if signal:
        color = term.RED
        if result.gain > 0:
            color = term.GREEN
    answers = map(lambda x: x and 1 or 0, answers)
    print sep.join(map(str, ['V' + color, 
                              "%06s" % symbol, 
                              ";".join(map(str, answers)),
                              signal and 1 or 0,
                              "%05s" % result.gain, 
                              result.rel_date.datetime_str(), 
                              #result.headline, #XXX
                              term.NORMAL]))

    sys.stdout.flush()


def main(Question):
    from optparse import OptionParser

    usage = "%prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--begin_date') 
    parser.add_option('-e', '--end_date')
    parser.add_option('-o', '--optimalize', action="store_true", default=False)
    parser.add_option('-s', '--sep', default=' ') 
    opts, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide a strategy: %s' % str(Question.ValidStrategies))
    else:
        strategy = args[0]

    cache = Cache()
    cache.load_all()
    summary = Summary(verbosity='mwd')
    print "Date: %s" % util.now().datetime_str()
    print 'CacheFN: %s' % Question.CacheFN
    print "Strategy: %s" % strategy
    print "Source:"
    for line in inspect.getsource(Question).splitlines():
        print '# %s' % line
    if issubclass(Question, MultiQuestion):
        print "Questions: " + ";".join(map(lambda x: x.Abbr, Question.Questions))

    db_dir = config.DB_DIR
    for d in util.db_entries(root_dir=db_dir):
        date = util.Date(d)
        if opts.begin_date and util.Date(opts.begin_date) > date:
            continue
        if opts.end_date and util.Date(opts.end_date) <= date:
            continue
        for symbol in util.db_entry_symbols(db_dir, d):
            result = cache.get(date, symbol)
            if result is None:
                print "%s: no result" % symbol
                continue
            if result.gain is None or result.gain2 is None:
                print "%s: no gain(s)" % symbol
                continue
            d = result.rel_date.timedelta()
            if d < TimeDelta(hours=9, minutes=30):
                if 'b' not in Question.When:
                    continue
            elif d >= TimeDelta(hours=16):
                if 'a' not in Question.When:
                    continue
            else:
                if 'i' not in Question.When:
                    continue
            answers, signal, data = Question(db_dir, date, symbol, {}).ask(strategy)
            summary.add(signal, result, data, date)
            print_answer(symbol, answers, signal, result, opts.sep)
    summary.finish()
    if opts.optimalize:
        summary.optimalize()
