from trading.page import SymbolPage

class Book(SymbolPage):
    _URL = "http://65.171.227.144/arcadataserver/ArcaBookData.php?Symbol=%s"
