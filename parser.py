from xml.sax import saxutils 
import BeautifulSoup as soup

class Parser(soup.BeautifulSoup):
    pass

def unescape(data):
    entities = {'&nbsp;': ' ', 
                '&#160;': ' '}
    return saxutils.unescape(data, entities=entities)

def parse(*args, **kw):
    return Parser(*args, **kw)

def _flatten(tag, result):
    for t in tag:
        if isinstance(t, soup.NavigableString):
            result.append(unescape(t.string))
        elif isinstance(t, soup.Tag):
            _flatten(t, result)
        else:
            assert 0
    return result

def flatten(tag):
# #ifndef VERSION_SPIDER
    """
    >>> flatten(parse('<tag><b>foo</b> bar</tag>').find('tag'))
    [u'foo', u' bar']
    """
# #endif
    return _flatten(tag, [])

def tablify(table, join_tds=True, grab_urls=False, split_by=[]):
    result = []
    for tr in table('tr'):
        row = []
        for td in tr('th')+tr('td'):
            if grab_urls:
                if td('a'):
                    row.append(unescape(td.find('a')['href']))
                for e in split_by:
                    val = td.find(e)
                    if val is not None and val.string is not None:
                        row.append(unescape(val.string))
            if join_tds:
                v = "".join(flatten(td)).strip()
            else :
                v = flatten(td)
            row.append(v)
        result.append(row)
    return result

# #ifndef VERSION_SPIDER
if __name__ == '__main__':
    import doctest, parser
    doctest.testmod(parser)
# #endif
