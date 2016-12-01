from trading.page import SymbolPage 

class Estimates(SymbolPage):
    CachePrefix = "zacks_estimates"
    _URL = 'http://www.zacks.com/research/report.php?type=estimates&t=%s'

    def _init(self, data):
        pass
