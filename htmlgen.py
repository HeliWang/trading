from UserList import UserList
from trading import util

class Tag(UserList):

    def __init__(self, _name, *data, **attrs):
        UserList.__init__(self)
        self.name = _name
        self.data = list(data)
        self.attrs = attrs
    
    def __call__(self, *data, **attrs):
        return self.__class__(self.name, *data, **attrs) #XXX hackish :)

    def __iadd__(self, what):
        self.append(what)
        return self

    def __getitem__(self, what):
        if type(what) in (list, tuple):
            for i in what:
                self.data.append(i)
        else:
            self.data.append(what)
        return self

    def __str__(self):
        if self.name.lower() in ("br", 'hr'):
            return "<%s>" % self.name
        #XXX what if i[1] contains `"` ?
        result = ["<%s %s>" % (self.name, " ".join(['%s="%s"' % i for i in
                                           self.attrs.items()]))]
        if self.name.lower() not in ("img", ):
            for a in self.data:
                result.append(unicode(a))
            result.append('</%s>' % self.name)
        return "".join(result)

    __repr__ = __str__
    
class Generator:
    """
    >>> T.table[T.td['foo'], T.td['bar']] 
    <table ><td >foo</td><td >bar</td></table>
    >>> t = T.table(border=1, cellspacing=0, cellpadding=10)
    >>> t.append(T.tr(T.td('foo', bgcolor='red'), T.td('bar')))
    >>> t
    <table cellpadding="10" border="1" cellspacing="0"><tr ><td bgcolor="red">foo</td><td >bar</td></tr></table>
    >>> T.tr(*map(T.th, [1, 2, 3]))
    <tr ><th >1</th><th >2</th><th >3</th></tr>
    >>> T.b[ 'foo'] 
    <b >foo</b>
    >>> T.img(src='foo.png')
    <img src="foo.png">
    >>> 
    """

    def __getattr__(self, name):
        return Tag(name)

T = Generator()

def font(text, color=None, bold=False, size=None):
    style = []
    if size is not None:
        style.append("font-size: %d" % size)
    if bold:
        # style.append('font-weight: bold')
        text = T.b(text)
    if color:
        # style.append("color: %s" % color)
        text = T.font(color=color)[text]
    return T.span(style=";".join(style))[text]

def pct_str_color(base, rest, bold=False, invert=False):
    if None in (base, rest) or base == 0:
        return None
    text = util.pct_str(base, rest)
    val = util.pct(base, rest)
    color = None
    if rest < base:
        color = 'red'
    elif rest > base:
        color = 'green'
    if invert:
        if color == 'red':
            color = 'green'
        elif color == 'green':
            color = 'red'
    text = font(text, color=color)
    if bold:
        text = T.b[text]
    return text


if __name__ == '__main__':
    import doctest, htmlgen
    doctest.testmod(htmlgen)
