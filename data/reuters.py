from trading.page import SymbolPage, MultiPage
from trading.data import _Insiders_Entry
from trading.data import Estimates_Period as _Estimates_Period
from trading import parser
from trading import util
from trading import browser
from mechanize import LinkNotFoundError

class Estimates_Period(_Estimates_Period):
    def _parse_rev(self, rev):
        result = util.atof(rev)
        if result:
            return result * 1000000

import re

def _validate(data, title):
    if data.find('We are experiencing technical difficulties at this time.') != -1:
        raise browser.FetchLater()
    if data.find('TD width="100%" class="notFound"><SPAN><B>Company Search</B><BR>') != -1:
        return False
    if data.find('<title>Lipper - - Leading Fund Intelligence</title>') != -1:
        return False
    if data.find('<strong>Company or Symbol not found</strong><br/>') != -1:
        return False
    if data.find('<h1>Company Name Look-up</h1>') != -1:
        return False
    if data.find('<h1>Company Name or Symbol Look-up</h1>') != -1:
        return False
    return True

class ReutersPage(SymbolPage):

    ### 13.11.06 boli niektore symboli v uppercase -> not found (EBAY, A)
    #def url(self):
    #    return self._URL % self.name.lower()

    def _validate(self, data, title):
        super(ReutersPage, self)._validate(data, title)
        if not _validate(data, title):
            self.valid = False

# #ifndef VERSION_SPIDER
    def convert(self, what, idx=2, factory=None):
        """
        convert a reuters table to something more usefull -> table of tables
        `what` is a parser.Parser object
        """
        if what is None:
            return [], None
        result = []
        table = parser.tablify(what)
        for i, line in enumerate(table[idx:]):
            if len(line) == 1 and not line[0]:
                continue
            r = []
            for j, e in enumerate(line):
                if not e:
                    r.append(None)
                elif j > 0 and e == '--':
                    r.append(None)
                else:
                    # remove funny stuff like this: Estimate vs. Actual\r\n                \r\n                In U.S. Dollars
                    val = " ".join(str(e).split())
                    if factory is None or j == 0 or i < 2:
                        r.append(val)
                    else:
                        r.append(factory(val))
            result.append(r)
        raw = str(what)
        raw = raw.replace('<table', '<table cellspacing="1" cellpadding="0"')
        raw.replace(' colspan="7"', '')
        result = table[:idx] + result
        for line in result:
            while len(line) < 4:
                line.append(None)
        return result, raw

# #endif

class Estimates(ReutersPage):
    CachePrefix = "reuters_estimates"
    _URL = "http://www.reuters.com/finance/stocks/estimates?symbol=%s"

# #ifndef VERSION_SPIDER
    RevPat = re.compile('^<td class="(?P<cls>\S+)">(?P<num>[-0-9,.]+)</td>')
    RevPat2 = re.compile('^<td>(?P<num>[-0-9,.]+)</td>')

    def __init__(self, *args, **kw):
        super(Estimates, self).__init__(*args, **kw)
        self.est = []
        self.hist = []
        # without next lines `..._raw` = None wu:23.10.6 won't generate
        self.hist_raw = None
        self.trend_raw = None
        self.rev_raw = None
        self.est_raw = None

    def _init(self, data):
        p = parser.parse(data)
        if data.find("We're sorry, Consensus Estimates Analysis is not available for") == -1:
            est = p.find('a', attrs=dict(name='consensus')).findNext('table')
            self.est, self.est_raw = self.convert(est)
            self.q0, self.q1, self.y0, self.y1 = None, None, None, None
            if len(self.est) > 1:
                r_est = map(lambda x: x[2], self.est)
                r_est = r_est[2:6] + r_est[7:11]
                if len(r_est) >= 8:
                    self.q0 = Estimates_Period(r_est[4], r_est[0])
                    self.q1 = Estimates_Period(r_est[5], r_est[1])
                    self.y0 = Estimates_Period(r_est[6], r_est[2])
                    self.y1 = Estimates_Period(r_est[7], r_est[3])
        hist = p.find('a', attrs=dict(name='surprise')).findNext('table')
        self.hist, self.hist_raw = self.convert(hist)
        trend = p.find('a', attrs=dict(name='trends')).findNext('table')
        self.trend, self.trend_raw = self.convert(trend)
        rev = p.find('a', attrs=dict(name='revisions')).findNext('table')
        self.rev, self.rev_raw = self.convert(rev, idx=1, factory=int)

        self.sector = p.find('b',text='sector:').findNext('a').string
        self.industry = p.find('b',text='industry:').findNext('a').string

        #XXX cleanup stuff below
        # colorify reuters EPS/REV revisions
        if self.rev_raw:
            tmp = []
            i = 0
            for line in self.rev_raw.splitlines():
                match = self.RevPat.match(line)
                if match:
                    i += 1
                    cls, val = match.groups()
                    if val == '--':
                        val = 0
                    else:
                        val = int(val)
                    line = '<td class="%s"%%s>%d</td>' % (cls, val)
                    if val > 0:
                        if cls == 'lightShadeCenter':
                            tmp.append(line % ' bgcolor="yellow"')
                        elif cls == 'noShadeCenter':
                            tmp.append(line % ' bgcolor="red"')
                        elif cls == 'center':
                            if not i % 2:
                                tmp.append(line % ' bgcolor="red"')
                            else:
                                tmp.append(line % ' bgcolor="yellow"')
                        else:
                            assert 0, line
                    else:
                        tmp.append(line % "")
                else:
                    tmp.append(line)
            self.rev_raw = "\n".join(tmp)

        if self.trend_raw:
            tmp = []
            prev = None
            count = 0
            lines = []
            for line in self.trend_raw.splitlines():
                line = line.replace('<td>&nbsp;</td>', '<td>-</td>\n').splitlines()
                lines.extend(line)
            for line in reversed(lines):
                line = line.replace('<td>&nbsp;</td>', '<td>-</td>\n')
                match = self.RevPat2.match(line)
                if match:
                    color = None
                    val = match.group('num')
                    cls = None
                    if val == '-':
                        val = None
                    if count == 5:
                        prev = None
                        count = 0
                    if None not in (prev, val):
                        v = util.atof(val)
                        if v > prev:
                            color = "yellow" 
                            if count == 1: # year ago
                                color = "khaki" #XXX standartize colors/magic
                        elif v < prev:
                            color = "red" 
                            if count == 1: # year ago
                                color = "orange" #XXX standartize colors/magic
                        if color:
                            line = '<td bgcolor="%s">%s</td>' % (color, val)
                    prev = util.atof(val)
                    count += 1
                tmp.append(line)
            self.trend_raw = "\n".join(reversed(tmp))

        # additional validation
        if len(self.hist) in (1, 3): # 3 is because of 2006-07-21/MTL/-1
            self.hist = None

        if not self.hist or not self.est:
            self.valid = False
        if data.find("We're sorry, Historical Surprises are not available") != -1:
            self.hist = []
            self.valid = False
        if data.find("We're sorry, Consensus Estimates Analysis is not available") != -1:
            self.est = []
            self.valid = False
        #XXX what about checks for other sections?

        if self.hist:
            while len(self.hist) < 13:
                self.hist.insert(len(self.hist)/2+1, [None] * 4)
                self.hist.append([None] * 4)
            assert len(self.hist) == 13, self.name

    def check_years(self, date): #XXX move to a better place? remove?
        if self.hist:
            data = map(lambda x: x[0], self.hist[2:7] + self.hist[8:13])
            data = filter(None, data)
            years = map(lambda x: int(x.split('/')[1]), data)
            if filter(lambda x: x < date.year-2, years):
                print "XXX: invalid years"
                print "XXX: date=%s" % date.date_str()
                for line in data:
                    print "XXX: %s" % line
                print
                self.hist = []

    def _hist_line(self, idx, period, offset):
        result = [None]*4
        if not period or not self.hist:
            return result
        result = [None]*4
        quarter, year = period.split()
        line = self.hist[offset+idx]
        if line[0] and line[0].startswith(quarter):
            result = line
        if result == [None]*4:
            for line in self.hist[offset:offset+5]:
                cell = line[0]
                if not cell:
                    continue
                if cell.startswith(quarter) and cell.endswith(year):
                    result = line
                    break
        if result == [None]*4:
            line = self.hist[offset:offset+5][idx]
            if line[0] and not None in line:
                result = map(lambda x: x.replace("Quarter Ending", "QE"), line)
        return result

    def hist_eps(self, i, period):
        return self._hist_line(i, period, 8)

    def hist_rev(self, i, period):
        return self._hist_line(i, period, 2)
# #endif

class AnalystOpinion(ReutersPage):
    CachePrefix = "reuters_analyst_opinion"
    _URL = "http://www.reuters.com/finance/stocks/recommendations?symbol=%s"

# #ifndef VERSION_SPIDER
    def __init__(self, *args, **kw):
        super(AnalystOpinion, self).__init__(*args, **kw)
        self.opinion_raw = None

    def _init(self, data):
        p = parser.parse(data)
        opinion = p.find('div', attrs={'class':'moduleHeader'}).findNext('div', attrs={'class':'moduleHeader'})
        opinion = opinion.findNext('table')
        self.opinion_raw = str(opinion)
# #endif

class FinancialHighlights(ReutersPage):
    CachePrefix = "reuters_financial_highlights"
    _URL = "http://www.reuters.com/finance/stocks/financialHighlights?symbol=%s"

class Overview(SymbolPage):
    _URL = "http://www.reuters.com/finance/stocks/overview?symbol=%s"

class Options(SymbolPage):
    _URL = "http://www.reuters.com/finance/stocks/option?symbol=%s"

class AnalystResearch(SymbolPage):
    _URL = "http://www.reuters.com/finance/stocks/analystResearch?symbol=%s"
