from trading.page import BinaryPage

class TA_1y(BinaryPage):
    CacheExtension = "gif"
    CachePrefix = "clearstation_TA_1y" 
    _URL = "https://chart.etrade.com/cgi-bin/rgraph?Symbol=%s&olay=None&gr=3&gtyp=Ohlc&tic=1-year&gs=Default&i1=None&i2=None&i3=Stochastic&i4=Will&e1=50&e2=26&e3=13&cs=&ci=None&event=1&int=&rl=0"
