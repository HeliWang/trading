from trading.page import SymbolPage, BinaryPage, MultiPage
from trading.data import _Quotes, _Insiders_Entry, Estimates_Period
from trading import parser
from trading import util
from trading import browser

# #ifndef VERSION_SPIDER
from mx.DateTime import TimeDelta
from trading.htmlgen import T
# #endif

import decimal
import os
import re
import mx

class News_Entry(object):
    Highlight_Words = ( ('stock', 'repurchase')
                      , ('merge', )
                      , ('buyback', )
                      )
    def __init__(self, date, headline, source, link=None, paid=False):
        self.date = util.Date(date)
        self.headline = headline
        self.source = source
        self.link = link
        self.paid = paid

    def __cmp__(self, other): 
        return cmp(repr(self), repr(other))

    def highlight(self):
        headline = self.headline.lower()
        complete_matches = 0
        for words in self.Highlight_Words:
            word_matches = 0
            for word in words:
                if headline.find(word.lower()) != -1:
                    word_matches += 1
            complete_matches += len(words) == word_matches
        return complete_matches > 0

    def fetch(self, output_dir, browser, obfuscate=0, fn='marketwatch_pr_%s.html'):
        fn = news_fn(self.date, self.headline, fn=fn)
        if self.link:
            msg = NewsPage(output_dir, self.link, fn)
            data = msg.fetch(browser, obfuscate=obfuscate)
        else:
            print "XXX: marketwatch.News_Entry without a link"
    
    def __str__(self):
        paid = "  "
        if self.paid:
            paid = "$ "
        return "%s %s%s (%s)" % (self.date.datetime_str(), 
                                 paid,
                                 self.headline, 
                                 self.source)
    __repr__ = __str__



# #ifndef VERSION_SPIDER
def highlight(text, pattern, color='yellow'):
    i = text.find(pattern)
    assert i != -1
    i = text.find('class="yfnc_tabledata1"', i)
    text = text[:i] + (' bgcolor="%s" ' % color) + text[i+23:]
    return text

def sanitize(text):
    text = str(text)
    text = text.replace('cellpadding="2" cellspacing="1"', 'cellpadding="0" cellspacing="1"')
    return text
# #endif

def _validate(data, title):
    if title == 'Yahoo! - 500 Internal Server Error':
        raise browser.FetchLater()
    if data.find(' is not a valid ticker symbol.') != -1:
        return False
    if data.find('<small>Interested in ETFs? Check out the') != -1:
        return False
    if data.find('<h1>Get Quotes Results for ') != -1:
        return False
    i = data.find('is no longer valid')
    if i != -1:
        #new = data[data.find('<b>', i)+3:data.find('</b>', i)]
        #XXX do something? change .name and throw FetchLater() ???
        return False
    return True

    
class YahooPage(SymbolPage):

    def _market_time(self, data):
        p = parser.parse(data)
        t = p.find('span', attrs=dict(id='yfs_market_time')).string
        return util.Date(t[:t.find('ET')])

    def _validate(self, data, title):
        super(YahooPage, self)._validate(data, title)
        if not _validate(data, title):
            self.valid = False

# #ifndef VERSION_SPIDER
    def mapping(self, p, headline):
        result = p.find('b', text=headline).findNext('table').findNext('table')
        result = parser.tablify(result)
        result = [(str(k).rstrip(":"), str(v)) for (k, v) in result]
        return result
# #endif

class Summary(YahooPage):
    CachePrefix = "yahoo_summary"
    _URL = "http://finance.yahoo.com/q?s=%s"

# #ifndef VERSION_SPIDER
    def __init__(self, *args, **kw):
        super(Summary, self).__init__(*args, **kw)
        self.delinquent = False

    def _init(self, data):
        p = parser.parse(data)

        name = p.find(name='div', attrs={'id':'yfi_investing_head'}).findNext('h1')
        self.fullname = name.contents[0]

        market = p.find(name='div', attrs={'class':'yfi_quote_summary'})
        self.market = None
        if market:
            self.market = market.span.string.split('(')[1].split(':')[0]

        self.delinquent = data.find('is delinquent in its regulatory filings') != -1

        # summary
        s = p.find(name='div', attrs={'id':'yfi_quote_summary_data'})
        summary = parser.tablify(s.table)
        summary.extend(parser.tablify(s.table.findNext('table')))
        self.summary = dict([(str(k.rstrip(":")), v) for (k, v) in summary])
        self.summary_raw = self._summary_raw()
        self.cap_raw = self.summary['Market Cap']
        self.summary['Last Trade'] = util.atof(self.summary['Last Trade'])
        self.summary['Volume'] = util.atoi(self.summary['Volume'])
        self.summary['Market Cap'] = util.atof(self.cap_raw) 
        v = self.summary['Avg Vol (3m)']
        if v == 'N/A':
            v = None
        else:
            v = util.atof(v) 
        self.summary['Avg Vol (3m)'] = v 
        t1 = s.find('table', attrs={'id': 'table1'})
        t2 = s.find('table', attrs={'id': 'table2'})
# #endif

    def _summary_raw(self):
        table = T.table
        for k in ('Last Trade', 'Trade Time', '1y Target Est', '52wk Range', 'Volume', 'Avg Vol (3m)', 'Market Cap'):
            if k in self.summary:
                table += T.tr[T.td(**{'class': 'yfnc_tablehead1'})[k], T.td(**{'class':'yfnc_tabledata1'})[self.summary[k]]]
        return table

class AnalystEstimates(YahooPage):
    CachePrefix = "yahoo_analyst_estimates"
    _URL = "http://finance.yahoo.com/q/ae?s=%s"

    def _validate(self, data, title):
        super(AnalystEstimates, self)._validate(data, title)
        if data.find('No analyst estimates data available for ') != -1:
            self.valid = False
            raise browser.FetchLater()

# #ifndef VERSION_SPIDER
    def __init__(self, *args, **kw):
        super(AnalystEstimates, self).__init__(*args, **kw)
        self.eps_est = None
        self.eps_hist = None #XXX add asserts (self._check)
        self.rev_est = None
        self.eps_trends = None
        self.eps_rev = None
        self.growth_est = None

        self.eps_est_raw = None
        self.rev_est_raw = None
        self.eps_hist_raw = None
        self.eps_trends_raw = None
        self.eps_rev_raw = None
        self.growth_est_raw = None

    def _init(self, data):
        if data.find("No analyst estimates data available for ") != -1 or \
           data.find('There is no  data available for') != -1:
            self.valid = False
            return

        p = parser.parse(data)
        def table(headline):
            raw = p.find(name='b', text=headline).findPrevious('table')
            table = parser.tablify(raw)
            result = [[str(h).strip().replace('\n         ', '') for h in
                        table[0]]]
            for line in table[1:]:
                row = [str(line[0])]
                for e in line[1:]:
                    if e.lower() == 'n/a':
                        row.append(None)
                    row.append(str(e))
                result.append(row)
            return result, self._sanitize2(str(raw))

        self.eps_est, self.eps_est_raw = table('Earnings Est')
        self.rev_est, self.rev_est_raw = table('Revenue Est')
        self.eps_hist, self.eps_hist_raw = table('Earnings History')
        self.eps_trends, self.eps_trends_raw = table('EPS Trends')
        self.eps_rev, self.eps_rev_raw = table('EPS Revisions')
        self.growth_est, self.growth_est_raw = table('Growth Est')
        self._check()

        #self.eps_est_raw = highlight(self.eps_est_raw, 'Avg. Estimate </td>')
        #self.eps_est_raw = highlight(self.eps_est_raw, 'Year Ago EPS </td>')
        #self.rev_est_raw = highlight(self.rev_est_raw, 'Avg. Estimate </td>', 'orange')
        #self.rev_est_raw = highlight(self.rev_est_raw, 'Year Ago Sales </td>', 'orange')

        # colorify trends
        if len(self.eps_trends) == 6:
            table = T.table(**{'class':'yfnc_tableout1', 'cellpadding':0, 'cellspacing':1, 'width':'100%'})
            tr = T.tr
            tr += T.td[T.b[self.eps_trends[0][0]]]
            for header in self.eps_trends[0][1:]:
                tr += T.td(**dict(align='center', width='18%'))[T.font(**dict(face='arial', size='-2'))[header]]
            table += tr
            data = []
            for line in reversed(self.eps_trends[1:]):
                tr = T.tr
                for i, cell in enumerate(line):
                    if i == 0:
                        tr += T.td(**{'class':'yfnc_tablehead1'})[cell]
                    else:
                        d = {}
                        if data:
                            now = util.atof(cell)
                            prev = data[len(data)-1][i-1]
                            if None not in (prev, now):
                                if now > prev:
                                    d['bgcolor'] = 'yellow'
                                elif prev > now:
                                    d['bgcolor'] = 'red'
                        if not d:
                            d['class'] = 'yfnc_tabledata1'
                        tr += T.td(**d)[cell]
                table.insert(1, tr)
                data.append(map(util.atof, line[1:]))
            self.eps_trends_raw = str(table)

        # colorify eps revisions
        if len(self.eps_rev) == 5:
            table = T.table(**{'class':'yfnc_tableout1', 'cellpadding':0, 'cellspacing':1, 'width':'100%'})
            tr = T.tr
            tr += T.td[T.b[self.eps_rev[0][0]]]
            for header in self.eps_rev[0][1:]:
                tr += T.td(**dict(align='center', width='18%'))[T.font(**dict(face='arial', size='-2'))[header]]
            table += tr
            for i, line in enumerate(self.eps_rev[1:]):
                tr = T.tr
                for j, cell in enumerate(line):
                    if j == 0:
                        tr += T.td(**{'class':'yfnc_tablehead1'})[cell]
                    else:
                        val = util.atoi(cell)
                        d = {'class':'yfnc_tabledata1'}
                        if val > 0 and i < 2:
                            d = {'bgcolor':'yellow'}
                        elif val > 0 and i > 1:
                            d = {'bgcolor':'red'}
                        tr += T.td(**d)[cell]
                table += tr
            self.eps_rev_raw = str(table)

        # unified Estimates (_Period) interface
        self.q0, self.q0, self.y0, self.y1 = None, None, None, None
        if self.rev_est and self.eps_est:
            self.q0 = Estimates_Period(self.eps_est[1][1], self.rev_est[1][1])
            self.q1 = Estimates_Period(self.eps_est[1][2], self.rev_est[1][2])
            self.y0 = Estimates_Period(self.eps_est[1][3], self.rev_est[1][3])
            self.y1 = Estimates_Period(self.eps_est[1][4], self.rev_est[1][4])

    def _sanitize2(self, table):
        if table.find('yfnc_tableout1') == -1:
            table = table.replace('<table', '<table class="yfnc_tableout1"', 1)
        return sanitize(table)

    def _check(self):
        def f(left, right): 
            assert left == right, '%s != %s' % (left, right)
        s = self
        # earning est
        f(s.eps_est[0][0], 'Earnings Est')
        f(s.eps_est[0][1].startswith('Current Qtr'), True)
        f(s.eps_est[0][2].startswith('Next Qtr'), True)
        f(s.eps_est[0][3].startswith('Current Year'), True)
        f(s.eps_est[0][4].startswith('Next Year'), True)
        f(s.eps_est[1][0], 'Avg. Estimate')
        f(s.eps_est[2][0], 'No. of Analysts')
        f(s.eps_est[3][0], 'Low Estimate')
        f(s.eps_est[4][0], 'High Estimate')
        f(s.eps_est[5][0], 'Year Ago EPS')
        # revenue est
        f(s.rev_est[0][0], 'Revenue Est')
        f(s.rev_est[0][1].startswith('Current Qtr'), True)
        f(s.rev_est[0][2].startswith('Next Qtr'), True)
        f(s.rev_est[0][3].startswith('Current Year'), True)
        f(s.rev_est[0][4].startswith('Next Year'), True)
        f(s.rev_est[1][0], 'Avg. Estimate')
        f(s.rev_est[2][0], 'No. of Analysts')
        f(s.rev_est[3][0], 'Low Estimate')
        f(s.rev_est[4][0], 'High Estimate')
        f(s.rev_est[5][0], 'Year Ago Sales')
        f(s.rev_est[6][0], 'Sales Growth (year/est)')
        # eps trends
        f(s.eps_trends[0][0], 'EPS Trends')
        f(s.eps_trends[0][1].startswith('Current Qtr'), True)
        f(s.eps_trends[0][2].startswith('Next Qtr'), True)
        f(s.eps_trends[0][3].startswith('Current Year'), True)
        f(s.eps_trends[0][4].startswith('Next Year'), True)
        f(s.eps_trends[1][0], 'Current Estimate')
        f(s.eps_trends[2][0], '7 Days Ago')
        f(s.eps_trends[3][0], '30 Days Ago')
        f(s.eps_trends[4][0], '60 Days Ago')
        f(s.eps_trends[5][0], '90 Days Ago')
        # eps revisions
        f(s.eps_rev[0][0], 'EPS Revisions')
        f(s.eps_rev[0][1].startswith('Current Qtr'), True)
        f(s.eps_rev[0][2].startswith('Next Qtr'), True)
        f(s.eps_rev[0][3].startswith('Current Year'), True)
        f(s.eps_rev[0][4].startswith('Next Year'), True)
        f(s.eps_rev[1][0], 'Up Last 7 Days')
        f(s.eps_rev[2][0], 'Up Last 30 Days')
        f(s.eps_rev[3][0], 'Down Last 30 Days')
        f(s.eps_rev[4][0], 'Down Last 90 Days')
        # growth est
        f(s.growth_est[0][0], 'Growth Est')
        # replace('-', '') some tickers have a minus in the name in yahoo (CRDB
        # vs. CRD-B)
        f(s.growth_est[0][1].replace('-', '').startswith(self.name.upper()), True)
        f(s.growth_est[0][2].startswith('Industry'), True)
        f(s.growth_est[0][3].startswith('Sector'), True)
        f(s.growth_est[0][4].startswith('S&P 500'), True)
        f(s.growth_est[1][0], 'Current Qtr.')
        f(s.growth_est[2][0], 'Next Qtr.')
        f(s.growth_est[3][0], 'This Year')
        f(s.growth_est[4][0], 'Next Year')
        f(s.growth_est[5][0], 'Past 5 Years (per annum)')
        f(s.growth_est[6][0], 'Next 5 Years (per annum)')
        f(s.growth_est[7][0], 'Price/Earnings (avg. for comparison categories)')
        f(s.growth_est[8][0], 'PEG Ratio (avg. for comparison categories)')
# #endif

class Profile(YahooPage):
    CachePrefix = "yahoo_profile"
    _URL = "http://finance.yahoo.com/q/pr?s=%s"

# #ifndef VERSION_SPIDER
    def _init(self, data):
        data = unicode(data, 'latin1')
        p = parser.parse(data)
        self.summary = p.find(name='b', text='BUSINESS SUMMARY')
        if self.summary is not None:
            self.summary = self.summary.findNext('table').findNext('td').string
        try:
            profile = dict(self.mapping(p, 'DETAILS'))
        except AttributeError:
            profile = dict(Industry="", Sector="")
        self.industry = str(profile['Industry'])
        self.sector = str(profile['Sector'])
        if self.industry in ('', 'N/A'):
            self.industry = None
        if self.sector in ('', 'N/A'):
            self.sector = None
        self.homepage = p.find('a', text='Home Page')
        if self.homepage is not None:
            self.homepage = str(self.homepage.parent['href'])
# #endif

class AnalystOpinion(YahooPage):
    CachePrefix = "yahoo_analyst_opinion"
    _URL = "http://finance.yahoo.com/q/ao?s=%s"

    _UpgradeLineStart = '<td class="yfnc_tabledata1" nowrap="nowrap" align="right">'
    _UpgradeLineEnd = '</td>'
    _FloatPat = re.compile('^\d+(\.\d+)?$')

    def _validate(self, data, title):
        super(AnalystOpinion, self)._validate(data, title)
        if data.find('No recommendation summary data available for ') != -1 and \
           data.find('No recommendation trend available for ') != -1 and \
           data.find('No Upgrades &amp; Downgrades available for ') != -1 and \
           data.find('No price target summary data available for ') != -1:
            self.valid = False
            raise browser.FetchLater()
        # sometimes date may be sth like this: -19909312.747 (PWEI:1.11.6)
        headline = 'UPGRADES &amp; DOWNGRADES HISTORY'
        p = parser.parse(data)
        if p.find('b', text=headline) is not None:
            upgrades, upgrades_raw = self._table(p, headline)
            start = self._UpgradeLineStart
            end = self._UpgradeLineEnd
            for line in upgrades_raw.split('</tr><tr>'):
                if line.startswith(start):
                    try:
                        util.Date(line[len(start):line.find(end)])
                    except mx.DateTime.RangeError:
                        self.valid = False
                        raise browser.FetchLater()
            # sometimes firm may be sth like this: 675612782.135 (MOV:7.12.6)
            if upgrades:
                for row in upgrades[1:]:
                    firm = row[1]
                    if firm and self._FloatPat.match(firm):
                        raise browser.FetchLater()

# #ifndef VERSION_SPIDER
    def __init__(self, *args, **kw):
        super(AnalystOpinion, self).__init__(*args, **kw)
        self.recom_sum = []
        self.recom_sum_raw = None
        self.target_sum = {}
        self.target_sum_raw = None
        self.recom_trends = []
        self.recom_trends_raw = None
        #XXX add to self._check()
        self.upgrades = None
        self.upgrades_raw = None

    def _init(self, data):
        if data.find('There is no  data available for') != -1:
            self.valid = False
            return 
        p = parser.parse(data)

        if data.find('No recommendation summary data available for') == -1:
            self.recom_sum, self.recom_sum_raw = \
                self._table(p, 'RECOMMENDATION SUMMARY')

        if data.find('No price target summary data available for') == -1:
            self.target_sum, self.target_sum_raw = \
                self._table(p, 'PRICE TARGET SUMMARY')
            self.target_sum = dict(map(lambda (k,v): (k, util.atof(v)), self.target_sum))

        if data.find('No recommendation trend available for') == -1:
            self.recom_trends, self.recom_trends_raw = \
                self._table(p, 'RECOMMENDATION TRENDS')

        if data.find('No Upgrades &amp; Downgrades available for ') == -1:
            self.upgrades, self.upgrades_raw = \
                self._table(p, 'UPGRADES &amp; DOWNGRADES HISTORY')

        self._check()

    def upgrades_hl(self, start_date):
        if not self.upgrades_raw:
            return
        result = []
        start = self._UpgradeLineStart
        end = self._UpgradeLineEnd
        for i, line in enumerate(self.upgrades_raw.split('</tr><tr>')):
            hl = False
            if line.startswith(start) and start_date is not None:
                hl = util.Date(line[len(start):line.find(end)]) >= start_date
            if i != 0:
                if hl:
                    line = 'bgcolor="lavender">' + line
                    line = line.replace(' class="yfnc_tabledata1"', '')
                else:
                    line = '>' + line
            result.append(line)
        return "</tr>\n<tr ".join(result)

    def targets_hl(self, price):
        if not self.target_sum:
            return
        result = self.target_sum_raw
        for key in ('Mean Target', 'Median Target', 'High Target', 'Low Target'):
            if self.target_sum[key] > price:
                color = 'yellow'
            else:
                color = 'red'
            result = highlight(result, '%s:' % key, color=color)
        return result

    def _table(self, p, headline):
        #XXX self.mapping copy&paste
        special = ('RECOMMENDATION TRENDS', 'UPGRADES &amp; DOWNGRADES HISTORY')
        if headline == special[0]:
            p = p.find('b', text=headline).findAllNext('table')[2]
        else:
            p = p.find('b', text=headline).findNext('table').findNext('table')
        table = parser.tablify(p) 
        if headline not in special:
            table = [(str(k).rstrip(":"), str(v)) for (k, v) in table]
        result = []
        for line in table:
            row = []
            for e in line:
                e = str(e).strip()
                if e.lower() in ('', 'n/a'):
                    row.append(None)
                else:
                    row.append(e)
            result.append(row)
        return result, sanitize(p.findPrevious('table'))

    def _check(self):
        def f(left, right): 
            assert left == right, '%r != %r' % (left, right)
        s = self
        if self.recom_sum:
            f(self.recom_sum[0][0], 'Mean Recommendation (this week)')
            f(self.recom_sum[1][0], 'Mean Recommendation (last week)')
            f(self.recom_sum[2][0], 'Change')
            #XXX od urciteho casu sa prestavaju uvadzat industry, sector, sp500 
            #means
            #if self.name == 'CBS':
            #    f(self.recom_sum[3][0], 'Media Industry Mean')
            #elif self.name == "BYI": # 2007-07-12
            #    f(self.recom_sum[3][0], 'Travel & Leisure Industry Mean')
            #elif self.name == 'FNM':
            #    f(self.recom_sum[3][0], 'General Finance Industry Mean')
            #elif self.name == 'VMED':
                #f(self.recom_sum[3][0], 'Fixed Line Telecommunications Industry Mean')
                #XXX 2007-05-09 mal uz len "Industry Mean"
            #    pass
            #else:
            #    f(self.recom_sum[3][0], 'Industry Mean')
            #f(self.recom_sum[4][0], 'Sector Mean')
            #f(self.recom_sum[5][0], 'S&P 500 Mean')
        if self.target_sum:
            assert self.target_sum.keys() == ['High Target', 'Mean Target', 'Median Target', 'No. of Brokers', 'Low Target']
        if self.recom_trends:
            f(self.recom_trends[0][1], 'Current Month')
            f(self.recom_trends[0][2], 'Last Month')
            f(self.recom_trends[0][3], 'Two Months Ago')
            f(self.recom_trends[0][4], 'Three Months Ago')
            f(self.recom_trends[1][0], 'Strong Buy')
            f(self.recom_trends[2][0], 'Buy')
            f(self.recom_trends[3][0], 'Hold')
            #f(self.recom_trends[4][0], 'Sell')
            assert self.recom_trends[4][0] in ('Sell', 'Underperform')
            #f(self.recom_trends[5][0], 'Strong Sell')
            assert self.recom_trends[5][0] in ('Strong Sell', 'Sell')
# #endif

# #ifndef VERSION_SPIDER
class Insiders_Entry(_Insiders_Entry):
    Actions = ( ("Purchase", "Purchase", 3, 'p')
              , ("Private Purchase", "Private Purchase", 3, 'pp')

              , ("Automatic Purchase", "Automatic Purchase", 2, 'ap')
              , ("Acquisition (Non Open Market)", "Acquisition (Non Open Market)", 2, 'a')

              , ("Option Exercise", "Option Exercise", 1, 'oe')
              , ("Statement of Ownership", "Statement of Ownership", 1, 'so') #XXX -> 0 ?

              , ("Dividend Reinvestment", "Dividend Reinvestment", 0, 'dr') #XXX
              , ("Indirect", "Indirect", 0, 'i') #XXX
              , ('Gift at', 'Gift', 0, 'g')

              , ("Planned Sale", "Planned Sale", -1, 'pls')

              , ("Disposition (Non Open Market", "Disposition (Non Open Market)", -2, 'd')
              , ("Automatic Sale", "Automatic Sale", -2, 'as')

              , ("Sale", "Sale", -3, 's')
              , ("Private Sale", "Private Sale", -3, 'prs')
              )

    def __init__(self, date, name, title, link, type, shares, 
                 value=0, direct="Direct"):
        super(Insiders_Entry, self).__init__(date, name, title, link,
                                             type, shares, value=value)
        assert direct in ('Direct', 'Indirect', 'Combined'), direct
        self.direct = direct
    
    def priority(self):
        for a, b, c, d in self.Actions:
            if self.type.startswith(a):
                return c
        assert 0, self.type

    def abbr(self):
        for a, b, c, d in self.Actions:
            if self.type.startswith(a):
                return d
        raise ValueError(self.type)
# #endif

class Insiders(YahooPage):
    CachePrefix = "yahoo_insider_transactions"
    _URL = "http://finance.yahoo.com/q/it?s=%s"

# #ifndef VERSION_SPIDER
    Entry = Insiders_Entry
# #endif

    def _validate(self, data, title):
        super(Insiders, self)._validate(data, title)
        if data.find('Result of ') != -1:
            print "XXX: Invalid insiders???: %s" % self.cache_fn(abs=True)  #XXX
            self.valid = False
            raise browser.FetchLater()
        if data.find('$(') != -1:
            print "XXX: Invalid insiders???: %s" % self.cache_fn(abs=True)  #XXX
            self.valid = False
            raise browser.FetchLater()
        if data.find('There is no  data available for') != -1:
            self.valid = False

# #ifndef VERSION_SPIDER
    def _init(self, data):
        self.data = []
        p = parser.parse(data)
        raw = p.find('b', text='INSIDER &amp; RULE 144 TRANSACTIONS REPORTED - LAST TWO YEARS')
        if raw is None: # changed on 2006-11-01
            raw = p.find('b', text='INSIDER TRANSACTIONS REPORTED - LAST TWO YEARS')
        if raw:
            self.data = self._from_table(parser.tablify(raw.findNext('table'), 0, grab_urls=True))
        self.summary_raw = None
        raw = p.find('b', text='Insider Purchases')
        if raw:
            self.summary_raw = str(raw.findPrevious('table'))

    def _from_table(self, table):
        result = []
        assert table[1] == [[u'Date'], [u'Insider'], [u'Shares'], [u'Type'], 
                            [u'Transaction'], [u'Value*']]
        for line in table[2:]:
            shares, direct, type, value = [str(e[0]) for e in line[3:]]
            value = value.strip()
            if value.startswith('$'):
                value = value[1:]
            if value == 'N/A':
                value = None
            else:
                value = util.atof(value)
            if len(line[2]) == 1:
                name, title = str(line[2][0]), None
            else:
                name, title = line[2]
            if shares == 'N/A':
                shares = None
            else:
                shares = util.atoi(shares)
            date = util.Date(str(line[0]))
            link = line[1]
            result.append(self.Entry(date, name, title, link, type, shares,
                                     value=value, direct=direct))
        return result
# #endif

class TA_5d(BinaryPage):
    CachePrefix = "yahoo_TA_5d" 
    _URL = "http://ichart.finance.yahoo.com/z?s=%s&t=5d&q=b&l=on&z=l&p=m200,m50,s,v&a=vm,fs"

class Keystats(YahooPage):
    CachePrefix = "yahoo_keystats"
    _URL = "http://finance.yahoo.com/q/ks?s=%s"

    def _validate(self, data, title):
        super(Keystats, self)._validate(data, title)
        pat = 'Shares Short (as of '
        if data.find(pat) != -1:
            start = data.find(pat) + len(pat)
            end = data.find(')', start)
            data_from = util.Date(data[start:end])
            fetched = self._market_time(data)
            diff = float(fetched.diff(data_from))/(3600*24)
            if diff > 60: #magic
                print "XXX: invalid keystats: %s" % self.name
                self.valid = False
                raise browser.FetchLater()

# #ifndef VERSION_SPIDER
    def _init(self, data):
        if data.find('There is no  data available for ') != -1:
            self.valid = False
            return 
        conv = self.convert
        p = parser.parse(data)
        t = p.find('b', text='VALUATION MEASURES').findAllNext('table')[2]
        self.valuation, self.valuation_raw = conv(t, heading=False)
        t = p.find('b', text='FINANCIAL HIGHLIGHTS').findAllNext('table')
        self.fiscal_year, self.fiscal_year_raw = conv(t[2])
        self.margins, self.margins_raw = conv(t[5])
        self.mgmt, self.mgmt_raw = conv(t[8])
        self.income, self.income_raw = conv(t[11])
        self.balance, self.balance_raw = conv(t[14])
        self.cashflow, self.cashflow_raw = conv(t[17])
        t = p.find('b', text='TRADING INFORMATION').findAllNext('table')
        self.history, self.history_raw = conv(t[3])
        self.share_stats, self.share_stats_raw = conv(t[6])

        self.share_stats_raw = highlight(self.share_stats_raw, 'Short % of Float')
        self.share_stats_raw = highlight(self.share_stats_raw, 'Shares Short')
        self.share_stats_raw = highlight(self.share_stats_raw, 'Short Ratio')
        self.div_splits, self.div_splits_raw = conv(t[9])

        self.avg_10d_vol_raw = self.share_stats.get('Average Volume (10 day)')

        # float
        self.float = None
        v = self.share_stats.get('Float')
        if v is not None:
            self.float = util.atof(v)
        # short of float
        self.short_of_float = None
        k = filter(lambda x: x.startswith('Short % of Float'), self.share_stats.keys())
        v = self.share_stats[k[0]]
        if v is not None:
            self.short_of_float = v.strip()
            if self.short_of_float[-1] == '%':
                self.short_of_float = self.short_of_float[:-1]
            self.short_of_float = util.atof(self.short_of_float)
        # short ratio
        self.short_ratio = None
        k = filter(lambda x: x.startswith('Short Ratio'), self.share_stats.keys())
        v = self.share_stats[k[0]]
        if v is not None:
            self.short_ratio = v.strip()
            self.short_ratio = util.atof(self.short_ratio)

    def convert(self, p, heading=True):
        result = {} 
        #XXX introduce case insensitive AbbrDict instead
        #(because of entries like this: 'Short Ratio (as of 12-Jun-06)')
        table = parser.tablify(p)
        if heading:
            table = table[1:]
        for k, v in table:
            if k[-2:] in ('1:', '2:', '3:' ,'4:' ,'5:'):
                k = k[:-2]
            elif k[-1] == ':': 
                k = k[:-1]
            #k = k[:k.find('(')]
            if not k:
                assert 0, v
            if v in ('N/A', 'NaN%', 'NaN'):
                v = None
            if v is not None:
                v = str(v)
            result[str(k).strip()] = v
        return result, sanitize(p.findPrevious('table'))
# #endif
 
class Quotes(_Quotes):
    CachePrefix = "yahoo_quotes"
    _URL = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%02d&b=%d&c=%04d&d=%02d&e=%d&f=%d&g=d&ignore=.csv"

# #ifndef VERSION_SPIDER
    def _init(self, data):
        result = {}
        lines = data.splitlines()
        prev = None
        assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj. Close*' or \
               lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close' #od 17.1.2007
        for line in reversed(lines[1:]):
            d, o, h, l, c, v, _ = line.split(',')
            d = util.Date(d)
            v = int(v)
            o, h, l, c = map(decimal.Decimal, [o, h, l, c])
            result[d] = e = self.Entry(d, o, h, l, c, v)
            e.prev = prev
            if prev:
                prev.next = e
            prev = e
        self.data = result

    def get(self, date, default=None):
        date = util.Date(date).date_obj()
        if self.data.has_key(date):
            return self.data[date]
        return default

    def get_before_report(self, date):
        d = date.timedelta()
        if d < TimeDelta(hours=9, minutes=30):
            return self.get(date-1)
        elif d >= TimeDelta(hours=16):
            return self.get(date)
        else:
            return self.get(date-1)
# #endif

    def url(self):
        last = (1, 1, 2000) #XXX
        a, b, c = last
        now = util.now()
        d = now.month
        e = now.day
        f = now.year
        return self._URL % (self.name, a - 1, b, c, d - 1, e, f)

class News(MultiPage):
    CachePrefix = "yahoo_news" 
    _URL = "http://finance.yahoo.com/q/h?s=%s"
    _TimePat = re.compile('\(\w+\s+(\d+:\d{2}(am|pm))\)$')

    Entry = News_Entry

    def __init__(self, archive, name, start_date, stop_after=None):
        super(News, self).__init__(archive, name, stop_after=stop_after)
        self.start_date = start_date
        self.data = []

    def _validate(self, data, title):
        super(News, self)._validate(data, title)
        if not _validate(data, title):
            self.valid = False

    def _parse(self, p):
        if not self.valid:
            raise StopIteration
        table = p.find('table', attrs={'class':'yfncnhl'})
        if table is None:
            raise StopIteration
        last_date = None
        for line in parser.tablify(table, grab_urls=True, split_by=['b']):
            if len(line) == 1:
                last_date = util.Date(line[0])
                if last_date < self.start_date:
                    raise StopIteration
            else:
                date = last_date
                paid = False
                _, url, source, headline = (line)
                if headline.startswith('[$$] '):
                    headline = headline.lstrip('[$$] ')
                    paid = True
                match = self._TimePat.search(headline)
                if match:
                    time, _ = match.groups()
                    date = util.Date("%s %s" % (date.date_str(), time))
                headline = headline[:headline.rfind(' (')] 
                headline = headline[:headline.find(source)]
                e = self.Entry(date, headline, source, url, paid=paid)
                self.data.append(e)
        return 'follow_link', (), dict(text='Older Headlines')

# #ifndef VERSION_SPIDER
class Options_Entry(object):
    def __init__(self, strike, symbol, last, change, bid, ask, volume,
                 open_int):
        self.strike = strike
        self.symbol = symbol
        self.last = last
        self.change = change
        self.bid = bid
        self.ask = ask
        self.volume = volume
        self.open_int = open_int

    def __str__(self):
        return ":".join(map(str, [self.strike, self.symbol, self.last,
                                  self.change, self.bid, self.ask,
                                  self.volume, self.open_int]))
    __repr__ = __str__
# #endif


class Options(YahooPage):
    CachePrefix = "yahoo_options"
    _URL = "http://finance.yahoo.com/q/op?s=%s"

# #ifndef VERSION_SPIDER
    Entry = Options_Entry

    def _init(self, data):
        if data.find('There is no  data available for') != -1:
            self.valid = False
            return
        p = parser.parse(data)
        self.market_time = self._market_time(data)
        self.calls, self.calls_raw, self.calls_expire = \
            self.from_table(p, 'CALL OPTIONS')
        self.puts, self.puts_raw, self.puts_expire = \
            self.from_table(p, 'PUT OPTIONS')

    def from_table(self, p, heading):
        options = p.find('b', text=heading).findAllNext('table')[2]
        expire = p.find('b', text=heading).findNext('td').string.split()
        expire = util.Date(" ".join(expire[-3:]))
        table = parser.tablify(options)
        assert table[0] == [u'Strike', u'Symbol', u'Last', u'Chg', u'Bid', u'Ask', u'Vol', u'Open Int']
        result = []
        for line in table[1:]:
            strike, symbol, last, change, bid, ask, volume, open_int = line
            strike = util.atof(strike)
            last = util.atof(last)
            change = float(change)
            if bid in ('N/A'):
                bid = None
            if ask in ('N/A'):
                ask = None
            open_int = util.atoi(open_int)
            volume = util.atoi(volume)
            result.append(self.Entry(strike, symbol, last, change, bid, ask,
                                     volume, open_int))
        raw = str(options)
        raw = raw.replace('<img width="10" height="14" border="0" src="http://us.i1.yimg.com/us.yimg.com/i/us/fi/03rd/down_r.gif" alt="Down" />', '')
        raw = raw.replace('<img width="10" height="14" border="0" src="http://us.i1.yimg.com/us.yimg.com/i/us/fi/03rd/up_g.gif" alt="Up" />', '')
        return result, raw, expire

class BasicChart(SymbolPage):
    _URL = "http://finance.yahoo.com/q/bc?s=%s"

class Industry(SymbolPage):
    _URL = "http://finance.yahoo.com/q/in?s=%s"

class ResearchReports(SymbolPage):
    _URL = "http://finance.yahoo.com/q/rr?s=%s"

class StarAnalysts(SymbolPage):
    CachePrefix = "yahoo_star_analysts"
    _URL = "http://finance.yahoo.com/q/sa?s=%s"

class MajorHolders(SymbolPage):
    _URL = "http://finance.yahoo.com/q/mh?s=%s"
