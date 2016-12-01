from trading.page import SymbolPage, RawPage
from trading import util
from trading.htmlgen import T
import json

# INTC news from 200091010 20 pieces
'http://www.marketwatch.com/news/headline/getheadlines?ticker=INTC&dateTime=00:00+20091010&docType=806&count=20'


def news_fn(date, headline, fn='marketwatch_pr_%s.html'): #XXX integrate somehow with News_Entry
    name = "%s_%s" % (date.datetime_str().replace(' ', '_'),
                      headline.replace('/', '_'))
    name = _truncate(name)
    return fn % name

def _truncate(string, max=220, postfix = "_(more)"):
    # max filesize is 255, we need some place for the filename and extension too
    if len(string) < max:
        return string
    return string[:max-len(postfix)] + postfix

class NewsPage(RawPage):
    def _validate(self, data, title):
        if data.find('<b><font size="5">System Outage</font></b>') != -1:
            raise browser.FetchLater()

class NewsEntry(object):

    BASE_URL = "http://www.marketwatch.com/story/"

    def __init__ (self, headline, date, uri, provider):
        self.headline = headline
        self.date = date
        self.uri = uri
        self.provider = provider

    def is_earnings_report(self):
        patterns = [('reports', 'results', ),
                    ('reports', 'quarter', ),
                    ('reports', 'earnings', ),
                    ('announces', 'income', ),
                    ('announces', 'earnings', ),
                    ('announces', 'revenue', ),
                    ('announces', 'results', ),
                    ('announces', 'profit', ),
                    ('announces', 'quarter', ),
                    ('announces', 'sales growth'), 
                    ('achieves', 'revenue', ),
                    ('achieves', 'operating', 'profit', 'of'),
                    ('reports', 'income', ),
                    ('reports', 'growth', ),
                    ('reports', 'earnings', ),
                    ('reports', 'revenue', ),
                    ('reports', 'eps', ),
                    ('reports', 'net loss', ),
                    ('reports', 'profit', ),
                    ('posts', 'profit', ),
                    ('posts', 'income', ),
                    ('results', 'quarter', ),
                    ('produces', 'earnings', ),
                    ('income', 'up', 'quarter', ),
                    ('reports',  'improved', 'performance', ), #2006-11-09:AEG 2007-01-30:NI
                    ('deliver', 'strong', 'results', ), # 2006-07-20 PFE
                    ('deliver', 'record', 'results', ), # 2006-08-03 CRYP
                    ('achieves record quarter',), # 2006-07-18 AMTD
                    ('quarter revenue',), # 2006-07-19 INTC
                    ('quarter', 'earnings per share', ), # 2006-07-20 UNP
                    ('eps', 'up', 'quarter', ), # 2006-07-20 WB
                    ('business conditions strengthen', ), # 2006-07-20 NCX
                    ('drive', 'quarter', 'earnings', ), # 2006-07-21 TAC
                    ('cash flow', 'quarter', ), # 2006-07-25 MOEH, ECA
                    ('earns', 'per', 'share', 'quarter'), # 2006-07-26 AGP
                    ('significantly improves its performance', ), # 2006-07-26 GIB
                    ('quarter', 'earnings', ), # 2006-07-27 FFH
                    ('revenue up', 'income', ), # 2006-07-31 EXAC
                    ('sales', 'grow', 'quarter', ), # 2006-08-01 STAA
                    ('net profit up', ), # 2006-08-08 GIGM
                    ('income triples', 'quarter'), # 2006-08-03 SRE
                    ('first half', 'results', ), # 2006-07-27 TMS
                    ('reports', 'financial performance', ), # 2006-08-02 PCG
                    ('quarter', 'income increases', 'revenue'), # 2006-08-03 UBET
                    ("operating profit", 'increases', 'quarter', ), # 2006-07-27 DCX
                    ("annual", 'increases', 'revenue', ), # 2006-08-03 CAH
                    ('results in line with guidance', ), # 2006-08-03 MZ
                    ('revenue at top end of guidance', ), # 2006-08-03 MZ
                    ('increase in net earnings to', ), # 2006-08-10 CBJ
                    ('preliminary results for the year ended', ), # 2006-09-25 WOS
                    ('deliver', 'record', 'revenue', ), #2006-10-24 RFMD
                    ('strong third quarter from hydro', ), #2006-10-24 NHY
                    ('interim review january-september', ), #2006-10-26 SEO
                    ('eps reaches', 'on revenue growth', ), #2006-10-26 ARTC
                    ('quarter', 'delivers', 'revenue growth of', ), #2006-10-26 CNXT
                    ('earns over', 'in first nine months of' ), #2006-11-02 ABX
                    ('acquisitions strengthen profitable growth', ), #2006-11-02 BF
                    ('double-digit growth in sales and earnings', ), #2006-11-02
                    ("Posts", "Record Sales", "for", "Quarter",), #PPG:2007-07-19
                    ("Records", "Growth", "in Total Revenue",), #WIT:2007-07-19
        ]
        antipatterns = [
            ('conference call',),
            ('to announce',),
            ('announces dividend',),
        ]
        headline = self.headline.lower()

        for pat in antipatterns:
            assert type(pat) in (list, tuple)
            found = True
            for p in pat:
                if headline.find(p.lower()) == -1:
                    found = False
                    break
            if found:
                return False
        for pat in patterns:
            assert type(pat) in (list, tuple)
            found = True
            for p in pat:
                if headline.find(p.lower()) == -1:
                    found = False
                    break
            if found:
                return True
        return False
    
    def url(self):
        return NewsEntry.BASE_URL + self.uri

    def __str__(self):
        return "%s %s (%s)" % (self.date.datetime_str(),
                               self.headline,
                               self.provider)

    __repr__ = __str__

    def fn(self, fn='marketwatch_pr_%s.html'): 
        name = "%s_%s" % (self.date.datetime_str().replace(' ', '_'),
                          self.headline.replace('/', '_'))
        name = _truncate(name)
        return fn % name

    def fetch(self, output_dir, browser, obfuscate=0, fn='marketwatch_pr_%s.html'):
        fn = news_fn(self.date, self.headline, fn=fn)
        if self.url():
            msg = NewsPage(output_dir, self.url(), fn)
            data = msg.fetch(browser, obfuscate=obfuscate)
        else:
            print "XXX: marketwatch.News_Entry without a url()"

class _News(SymbolPage):
    CacheExtension = "json"

    def __init__(self, archive, name):
        super(_News, self).__init__(archive, name)
        self.data = []

    def filter_from(self, date):
        return filter(lambda x: x.date >= date, self.data)

    def _init(self, data):
        list = json.read(data)
        for e in list:
            p = e['Provider']
            d = util.Date(float(e['TimestampUtc'][6:-5]) - 6*3600) 
            h = e['HeadlineText']
            u = e['SeoHeadlineFragment']
            news = NewsEntry(h, d, u, p)
            self.data.append(news)

    def url2(self, link):
        return T.a(href="http://www.marketwatch.com/investing/stock/%s/news" % self.name)[T.b[link]]

class News(_News):
    CachePrefix = "marketwatch_news"
    _URL = 'http://www.marketwatch.com/news/headline/getheadlines?ticker=%%s&dateTime=00:00+%s&docType=806&count=50' % util.Date(".").strftime("%Y%m%d")

class PR(_News):
    CachePrefix = "marketwatch_pr"
    _URL = 'http://www.marketwatch.com/news/headline/getheadlines?ticker=%%s&dateTime=00:00+%s&docType=2007&count=10' % util.Date(".").strftime("%Y%m%d")

    def get_earnings_report(self, from_date):
        result = None
        if len(self.data) == 1:
            return self.data[0]
        data = self.data
        data.sort(lambda x, y: cmp(x.date, y.date))
        if from_date:
            d = util.Date("%s %s" % ((from_date - 1).date_str(), "18:00:00"))
            data = filter(lambda x: x.date >= d, self.data)
        for e in data:
            if e.is_earnings_report():
                result = e
                break
        return result

class Options(SymbolPage):
    _URL = "http://www.marketwatch.com/investing/stock/%s/options"

class Ratings(SymbolPage):
    _URL = "http://www.marketwatch.com/investing/stock/%s/analystestimates?subview=ratings"
