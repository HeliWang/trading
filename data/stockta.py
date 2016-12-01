from trading.page import SymbolPage, RawPage
from trading import parser
from decimal import Decimal

import os

class Analysis(SymbolPage):
    CachePrefix = "stockta_analysis"
    _URL = 'http://www.stockta.com/cgi-bin/analysis.pl?symb=%s&num1=7&cobrand=&mode=stock'

    def fetch(self, browser, force=False, obfuscate=0):
        data = super(Analysis, self).fetch(browser, 
            force=force, obfuscate=obfuscate)
        self._fetch_TA(data, browser, force=force)
        return data

# #ifndef VERSION_SPIDER
    def _analysis(self, p):
        raw = p.find('b', text='Overall')
        if raw is None:
            return None, None
        raw = raw.findPrevious('table')
        table = parser.tablify(raw)
        data = zip(table[0][1:], table[1])
        return dict(data), str(raw)

    def _init(self, data):
        p = parser.parse(data)
        self.analysis, self.analysis_raw = self._analysis(p)
        self.indicators = {}
        def extract(text):
            result = p.find('b', text=text)
            if result is None: #XXX 2006-07-19/FMSB has no candlestick analysis
                return None, None
            result = result.findNext('table')
            return result, "%s\n%s" % (result.findPrevious('table'), result)
        indicators, self.indicators_raw = extract('Chart Indicators')
        if indicators:
            for line in parser.tablify(indicators)[1:]:
                name, short, inter, long = line
                self.indicators[name] = (short, inter, long)
        _, self.candlesticks_raw = extract('Recent CandleStick Analysis')
        _, self.gaps_raw = extract('Open Gaps')
        self.SR, self.SR_raw = extract('Support/Resistance')
        self._parse_SR()

    def _parse_SR(self):
        if self.SR is not None:
            SR = []
            table = parser.tablify(self.SR)
            for line in table[1:]:
                val = Decimal(line[1]), int(line[2])
                SR.append(val)
            self.SR = SR
# #endif

    def chart_cache_fn(self):
        return self.cache_fn().replace('analysis', 'chart').replace('.html', '.png')

    def _fetch_TA(self, data, browser, force=False, 
                  filename = "stockta_chart_%s.png"):
        if os.path.exists(os.path.join(self.archive, filename % self.name)):
            return 
        p = parser.parse(data)
        link = None
        for img in p('img'):
            if img['src'].startswith('candle.pl?'):
                link = str(img['src'])
        if link is None:
            return
        link = "http://www.stockta.com/cgi-bin/%s" % link #XXX make it relative
        self.ta = RawPage(self.archive, link, filename % self.name)
        # don't obfuscate here, we already did in fetch
        self.ta.fetch(browser, force=force, obfuscate=0) 

# #ifndef FETCH_VERSION_ONLY
if __name__ == "__main__" :
    from trading.browser import Browser
    b = Browser()
    i = Analysis('/tmp', "INTC")
    i.fetch(b)
# #endif
