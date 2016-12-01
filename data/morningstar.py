from trading.page import SymbolPage

class Options(SymbolPage):
    _URL = 'http://quote.morningstar.com/Option/Options.aspx?sLevel=A&ticker=%s'
