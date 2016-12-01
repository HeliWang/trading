from trading.page import SymbolPage

class Ownership(SymbolPage):
    CachePrefix = 'msn_ownership'
    _URL = 'http://moneycentral.msn.com/ownership?Symbol=%s'
