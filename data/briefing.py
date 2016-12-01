from trading.page import SymbolPage 
from trading.data import _Schedule
from trading import util
from trading import parser
from trading.htmlgen import T, font

class _BriefingPage(SymbolPage):
    CacheExtension = "html"

    def url(self):
        return 'http://www.briefing.com/GeneralContent/Active/Investor/TickerSearch/QuickSearch.aspx'

    def _init(self, data):
        pass

class UpgradesDowngrades(_BriefingPage): 
    CachePrefix = "briefing_updown" 

    def url_args(self):
        return {'Ticker': self.name, 'SearchRadio': 'UpgradesDowngrades'}

class Earnings(_BriefingPage):
    CachePrefix = "briefing_earnings" 

    def __init__(self, *args, **kw):
        super(Earnings, self).__init__(*args, **kw)
        self.data = {}

    def _init(self, data):
        p = parser.parse(data)
        cal = p.find('b', text='Earnings Calendar').findNext('table')
        table = parser.tablify(cal)
        assert table[0] == [u'Date', u'FiscalEnd', u'FiscalQtr', u'Time', u'Actual', u'Rtrs/Zcks', u'Yr-ago', u'Rev.Yr-Yr', u'Rev. $mln', u'Yr-ago $mln']
        for line in table[1:]:
            self.data[line[0]] = line

    def url_args(self):
        return {'Ticker': self.name, 'SearchRadio': 'EarningsCalendar',
            'Submit2': 'Search'}

class Guidance_Entry:
    def __init__(self, date, period, end, eps_est, eps_rev, rev_est, rev_rev):
        self.date = date
        self.period = period
        self.end = end
        self.eps_est = eps_est
        self.eps_rev = eps_rev
        self.rev_est = rev_est
        self.rev_rev = rev_rev

    def fmt_html(self):
        result = T.table
        def _fmt(text):
            if text.find("Upside:") != -1: #XXX move to data.briefing
                return font(text, color="green", bold=True)
            if text.find("Downside:") != -1:
                return font(text, color="red", bold=True)
            return text
        result += T.tr[
                       T.td[self.date.date_str()],
                       T.td[self.period],
                       T.td[self.end or "&nbsp;"],
                       T.td[self.eps_est or "&nbsp;"],
                       T.td[self.eps_rev and _fmt(self.eps_rev) or "&nbsp;"],
                       T.td[self.rev_est or "&nbsp;"],
                       T.td[self.rev_rev and _fmt(self.rev_rev) or "&nbsp;"],
                      ]
        return result

    def __str__(self):
        return ":".join([self.date.date_str(),
                         self.period,
                         self.end,
                         self.eps_est,
                         self.eps_rev,
                         self.rev_est,
                         self.rev_rev])
    __repr__ = __str__

class Guidance(_BriefingPage):
    CachePrefix = "briefing_guidance" 

    Entry = Guidance_Entry

    def __init__(self, *args, **kw):
        super(Guidance, self).__init__(*args, **kw)
        self.data = []

    def url_args(self):
        return {'Ticker': self.name, 'SearchRadio': 'EarningsGuidance',
            'Submit2': 'Search'}

    def from_to(self, date1, date2):
        result = []
        for e in self.data:
            if e.date <= date2:
                if date1 is None or e.date > date1:
                    result.append(e)
        return result

    def _init(self, data):
        p = parser.parse(data)
        if data.find('<font color="red">No results found for "') != -1:
            return
        cal = p.find('b', text='Guidance Calendar')
        if cal:
            self.data = []
            #cal = cal.findPrevious('table')
            cal = cal.findNext('table')
            table = parser.tablify(cal)
            assert table[0] == [u'Date', u'Period', u'End', u'EPS Estimate', u'EPS', u'Rev Estimate', u'Rev'], table[0]
            for l in table[1:]:
                date, period, end, eps_est, eps_rev, rev_est, rev_rev = l
                date = util.Date(date)
                e = self.Entry(date, period, end, eps_est, eps_rev, rev_est, rev_rev)
                self.data.append(e)

class Schedule(_Schedule):
    CachePrefix = "briefing_earnings_calendar"
    Filename = 'briefing_schedule.txt'
    DateFmt = '%b-%d-%Y'
    _URL = 'http://briefing.com/GeneralContent/Investor/Active/ArchiveSearch/ArchiveSearchInvestor.aspx?PageName=Earnings%%20Calendar&Date=%s'

    def _init(self, data):
        bmo = "Before The Open"
        id = "During Trading Hours"
        amc = "After The Close"
        p = parser.parse(data)
        # find something to parse
        d = p.find('th', text=bmo)
        if d is None:
            d = p.find('th', text=id)
        if d is None:
            d = p.find('th', text=amc)
        if d is not None:
            d = d.findPrevious('table')
            a = 0
            b = 0
            for line in parser.tablify(d, grab_urls=True):
                confirmed = not not line[0]
                if confirmed:
                    name, symbol = line[3:5]
                else:
                    name, symbol = line[2:4]
                if name == bmo:
                    b = 1
                    continue
                elif name == id:
                    b = 0
                    continue
                elif name == amc:
                    b = 0
                    a = 1
                    continue
                e = self.Entry(symbol, self.date, b, a, confirmed=confirmed)
                self.data.append(e)
