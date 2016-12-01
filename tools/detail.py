from trading.data import yahoo, reuters, earnings, nasdaq, google, zacks, morningstar
from trading.data import clearstation, briefing, stockta, marketwatch, msn, arca
from trading.htmlgen import T, font, pct_str_color
from trading import util
from trading import config
from mx.DateTime import TimeDelta

from decimal import Decimal

import codecs
import traceback
import os
import sha
import sys
import shutil

def _copy(src, dst):
    try:
        shutil.copy(src, dst)
    except IOError:
        pass

def ignore_errors(f, *args):
    try:
        f(*args)
        return 0
    except Exception, e:
        traceback.print_exc()
        return 1

def _copy_from_zip(page, dir, fni=None, fno=None):
    if os.path.exists(page.archive):
        a = util.ZipFile(page.archive, mode='r')
        fns = a.namelist()
        a.close()
        fni = fni or page.cache_fn() 
        fno = fno or page.cache_fn() 
        if fni in fns:
            a = util.ZipFile(page.archive)
            data = a.read(fni)
            f = open(os.path.join(dir, fno), 'w')
            f.write(data)
            f.close()
            a.close()

def fmt_guidance(data):
    result = T.table
    def _fmt(text):
        if text.find("Upside:") != -1: #XXX move to data.briefing
            return font(text, color="green", bold=True)
        if text.find("Downside:") != -1:
            return font(text, color="red", bold=True)
        return text
    for e in data:
        result += T.tr(bgcolor="lightgray")[
                       T.td[e.date.date_str()],
                       T.td[e.period],
                       T.td[e.end or "&nbsp;"],
                       T.td[e.eps_est or "&nbsp;"],
                       T.td[e.eps_rev and _fmt(e.eps_rev) or "&nbsp;"],
                       T.td[e.rev_est or "&nbsp;"],
                       T.td[e.rev_rev and _fmt(e.rev_rev) or "&nbsp;"],
                      ]
    return result

def _navbar(name):
    result = []
    for n, l in [ 
                  ('summary', '#summary'),
                  ('history', '#history'),
                  ('analyst estimates', '#ae'),
                  ('AO', '#ao'),
                  ('ownership', '#ownership'),
                  ('insiders', '#insiders'),
                  ('news', '#news'),
                  ('TA', '#TA'),
                  ('options', '#options'),
                  ('aftermatch', '#aftermatch'),
                ]:
        if n == name:
            result.append(T.b(name, style='font-size:12pt;'))
            result.append(T.a(name=l[1:]))
        else:
            result.append(T.a(n, href=l))
    bar = "&nbsp;".join(map(str, result))
    return T.table(width="100%")[T.tr[T.td(bgcolor='#eeeeee')[bar]]]

def _hr():
    return '<hr noshade size="1">'

def _link_to_top(name):
    print >> f, T.a(name=name)
    print >> f, T.a(href="#summary")[ "top" ]

def html_ownership(f, m, y):
    print "ownership"
    print >> f, _navbar('ownership')
    print >> f, m.url2("msn/Ownership"), T.br, y.url2("yahoo/MajorHolders")

def html_news(f, m, y, g):
    print "news"
    print >> f, _navbar('news')
    print >> f, m.url2("marketwatch/News"), T.br, y.url2("yahoo/Headlines"), T.br, g.url2("google/Summary")

def html_options(f, mwo, mso, yo, ro):
    print "options"
    print >> f, _navbar('options')
    print >> f, mwo.url2("marketwatch/Options"), T.br, yo.url2("yahoo/Options"), T.br, ro.url2("reuters/Options")
    print >> f, T.p, mso.url2("morningstar/Options")
    print >> f, T.p, T.a(href=yo.cache_fn())["ARCHIVED: yahoo/Options"]

def html_insiders(f, summary, insiders, h, date, output_dir):
    def fmt_insiders(i, h, date, have_direct=False):
        last = e = h.last(date)
        data = i.data
        table = T.table(**{'class':'dashed_border', 'cellspacing':0, 'cellpadding':2})
        table += T.tr(*map(T.th, ['Date', 'Insider', 'Amount', 'I', 'Type', 'Value']))
        for i in data:
            type = i.type
            prio = i.priority()
            if prio <= -2:
                type = font(type, color="red", bold=1)
            elif prio >= 2:
                type = font(type, color="green", bold=1)
            if prio == -1:
                type = font(type, color="red")
            elif prio == 1:
                type = font(type, color="green")
            t_tr = lambda *x: T.tr(*x)
            if last and last.date and last.date < i.date:
                t_tr = lambda *x: T.tr(bgcolor='lavender', *x)
            if e and e.date and i.date < e.date:
                table += T.tr(bgcolor='beige')[
                           T.td[e.date.date_str()],
                           T.td(colspan=5)[T.b[e.title]],
                         ]
            direct = "&nbsp;"
            if have_direct: 
                if i.direct == 'Indirect':
                    direct = "*" 
            table += t_tr( T.td[ i.date.date_str()],
                           T.td[ u"%s<br>%s" % \
                                  (T.a(href=i.link)[i.name],
                                   i.title or ""
                                  )],
                           T.td[ util.fmt_number(i.shares) or "&nbsp;"],
                           T.td[ direct],
                           T.td[ type],
                           T.td[ util.fmt_number(i.value) or "&nbsp;"],
                         )
            while e and e.date:
                if i.date < e.date:
                    e = e.prev
                else:
                    break
        return table
    print "insiders"
    print >> f, _navbar('insiders')
    if insiders.valid:
        f.write(unicode(T.table[
                          T.tr[
                            T.td[
                                fmt_insiders(insiders, h, date, have_direct=True),
                            ],
                            T.td[
                                insiders.summary_raw,
                            ],
                          ]
                        ]))
    else:
        print >> f, 'N/A'

def html_head(f, s, h, date):
    _html_pre = '''
    <html>
    <head>
    <LINK href="http://www.reuters.com/resources/css/rcom-main.css" rel="StyleSheet" type="text/css">
    <LINK href="http://www.reuters.com/resources/css/rcom-datachart.css" rel="StyleSheet" type="text/css">
    <LINK href="http://www.reuters.com/resources/css/rcom-tertiary.css" rel="StyleSheet" type="text/css">
    <LINK href="http://us.js2.yimg.com/us.js.yimg.com/i/us/fi/03rd/yfnc_200712171510.css" rel="StyleSheet" type="text/css">

    <style type="text/css">
    * { font-size: 10pt; 
        font-family: arial, helvetica, sans-serif
      }
    td {
        vertical-align: top;
    }
    .dashed_border {
        border-style: dashed; 
        border-width: 1px;
    }
    </style>
    <title>%s</title>
    </head>
    <body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0">'''
    e = h.next(now=date)
    title = "%s / %s / %s / $%s / %s / %s" % \
        (s.name,
         e and e.period() or 'N/A', 
         e and e.raw_date() or 'N/A', 
         s.summary['Last Trade'], 
         e and e.est or 'N/A',
         e and e.year_ago or 'N/A'
        )
    print >> f, _html_pre % (title)

def html_tail(f):
    _html_post = """
    </body>
    </html>"""
    print >> f, _html_post

_fmt_cci = lambda x: x is not None and ("%.2f" % x) or '&nbsp;' #XXX copy paste
def fmt_cci(x):
    val = _fmt_cci(x)
    if val is not None:
        color = None
        if x > 0:
            color = 'red'
        else:
            color = 'navy'
        val = T.font(val, color=color)
        if x > 100 or x < -100:
            val = T.b[val]
    return val

def _est_table(re, ae):
    est = '&nbsp;'
    try:
        if re.est and re.hist and ae.rev_est and ae.eps_est:
            r_est = map(lambda x: x[2], re.est)
            r_est = r_est[2:6] + r_est[7:11]
            r_hist = map(lambda x: x[2], re.hist)
            tdc = lambda cell: T.td(T.b[cell], bgcolor='yellow')
            est = T.table(**{'class':'dashed_border', 'cellpadding':1})[
                              T.tr[
                                T.th["&nbsp"], 
                                T.th(colspan=2)['reuters'],
                                T.th(colspan=2)['yahoo'],
                              ],
                              T.tr[
                                T.td["Q -4"], 
                                T.td[r_hist[11]],
                                T.td[r_hist[5]],
                                T.td[ae.eps_est[5][1]],
                                T.td[ae.rev_est[5][1]],
                              ],
                              T.tr[
                                T.td["Q -1"], 
                                T.td[r_hist[8]],
                                T.td[r_hist[2]],
                                T.td[ae.eps_hist[2][4]],
                                T.td['&nbsp;'],
                              ],
                              T.tr[
                                T.td["Q 0"], 
                                tdc(r_est[4]),
                                tdc(r_est[0]),
                                T.td[T.b[ae.eps_est[1][1]]],
                                T.td[T.b[ae.rev_est[1][1]]],
                              ],
                              T.tr[
                                T.td["Q 1"], 
                                T.td[r_est[5]],
                                T.td[r_est[1]],
                                T.td[ae.eps_est[1][2]],
                                T.td[ae.rev_est[1][2]],
                              ],
                              T.tr[
                                T.td["Y 0"], 
                                tdc(r_est[6]),
                                tdc(r_est[2]),
                                T.td[T.b[ae.eps_est[1][3]]],
                                T.td[T.b[ae.rev_est[1][3]]],
                              ],
                              T.tr[
                                T.td["Y 1"], 
                                T.td[r_est[7]],
                                T.td[r_est[3]],
                                T.td[ae.eps_est[1][4]],
                                T.td[ae.rev_est[1][4]],
                              ],
                            ]
    except Exception, e:
        traceback.print_exc()
        pass
    return est



def html_summary(f, s, h, p, ks, etrade, quotes, date, re, ae, gs, ro, nrt, ab, y5d):
    print 'summary'
    e = h.next(now=date)

    est = _est_table(re, ae)

    print >> f, _navbar('summary')
    print >> f, font("%s:%s, " % (s.name, s.market), size=16, bold=1)
    print f.write(unicode(font(T.a(href=p.homepage)[ s.fullname], size=12)))
    print >> f, " , ", font('%s, ' % (e and e.raw_date() or 'N/A'), color="navy", bold=1, size=12)
    print >> f, font('%s, ' % (e and e.period() or 'N/A'), color="navy", bold=1, size=12)
    print >> f, font('Estimated EPS: <b>$%s</b>, ' % (e and e.est or 'N/A'), color="navy", size=12)
    print >> f, font('Year Ago EPS: <b>$%s</b>, ' % (e and e.year_ago or 'N/A'), color="navy", size=12)
    print >> f, font("Generated: %s" % util.now().strftime("%Y-%m-%d %H:%M:%S"))

    table = T.table[
                T.tr[
                  T.td[
                    s.summary_raw,
                    ks.valid and ks.share_stats_raw or 'ks.share_stats_raw: N/A',
                    est
                  ],
                  T.td[
                    T.img(src=etrade.cache_fn()),
                    T.br,
                    s.delinquent and font("DELINQUENT", color="red", bold=True) or "",
                    T.br,
                    "Sector: <b>%s</b>, Industry: <b>%s</b>" % (p.sector, p.industry),
                    T.br,
                    gs.url2("google/Summary"),
                    T.br,
                    s.url2("yahoo/Summary"),
                    T.br,
                    y5d.url2("yahoo/5D_Chart"),
                    T.br, T.a(href="pre_%s" % y5d.cache_fn())["ARCHIVED yahoo/5D_Chart"],
                    T.p,
                    nrt.url2("nasdaq/RealTime"),
                    T.p,
                    ab.url2("arca/Book"),
                  ],
                ]
            ]
    f.write(unicode(table))

def html_history(f, h, quotes, short_int, date, re, ae, guidance):
    print "price history"
    print >> f, _navbar('history')
    result = []
    result.append('<table border=0 cellspacing=1 cellpadding=2 class=dashed_border>')

    e = filter(lambda x:x.date is not None and x.date.date_obj() == date, h.data)
    if e:
        e = e[0]
        q = quotes.last()
        while q and q.date >= date:
            q = q.prev
        if q is not None:
            # next line is true when there are quotes in $symbol/3
            have_last_quote = util.next_trading_day(q.date) == date 
            if q and q.prev and q.prev.prev and q.prev.prev.prev and q.prev.prev.prev.prev:
                tr1 = T.tr()
                tr2 = T.tr()
                tr3 = T.tr()
                tr4 = T.tr()
                td = lambda x: T.td(bgcolor='#eeeeee')[x]
                tr1 += td(e.raw_date())
                tr1 += td(T.b[e.est])
                tr1 += td('&nbsp;')
                tr1 += td(e.year_ago)
                if have_last_quote:
                    tr1 += td(q.prev.prev.prev.prev.close)
                    tr1 += td(q.prev.prev.prev.close)
                    tr1 += td(q.prev.prev.close)
                    tr1 += td(q.prev.close)
                    tr1 += td(q.close)
                else:
                    tr1 += td(q.prev.prev.prev.close)
                    tr1 += td(q.prev.prev.close)
                    tr1 += td(q.prev.close)
                    tr1 += td(q.close)
                    tr1 += td('&nbsp;')
                if e.amc and q.next:
                    tr1 += td('&nbsp;')
                    tr1 += td('&nbsp;')
                    tr1 += td('&nbsp;')
                    tr1 += td(q.next.close)
                if e.amc and q.next:
                    tr2 += T.td(q.next.date.date_str())
                else:
                    tr2 += T.td(q.date.date_str())
                tr2 += T.td(colspan=3)["&nbsp;"]
                fmt = lambda a, b: pct_str_color(a, b, invert=True)
                if have_last_quote:
                    tr2 += T.td(fmt(q.close, q.prev.prev.prev.prev.close))
                    tr2 += T.td(fmt(q.close, q.prev.prev.prev.close))
                    tr2 += T.td(fmt(q.close, q.prev.prev.close))
                    tr2 += T.td(fmt(q.close, q.prev.close))
                else:
                    tr2 += T.td(fmt(q.close, q.prev.prev.prev.close))
                    tr2 += T.td(fmt(q.close, q.prev.prev.close))
                    tr2 += T.td(fmt(q.close, q.prev.close))
                    tr2 += T.td('&nbsp;')
                if len(re.est) > 7 and None not in (re.est[2][2], re.est[7][2]):
                    tr3 += T.td(re.est[7][0])
                    tr3 += T.td(re.est[7][2])
                    tr4 += T.td(re.est[2][0])
                    tr4 += T.td(re.est[2][2])
                else:
                    tr3 += T.td("&nbsp;")
                    tr3 += T.td("&nbsp;")
                    tr4 += T.td("&nbsp;")
                    tr4 += T.td("&nbsp;")
                tr3 += T.td("&nbsp;")
                tr3 += T.td("&nbsp;")
                tr3 += T.td[util.fmt_number(q.prev.prev.prev.volume)]
                tr3 += T.td[util.fmt_number(q.prev.prev.volume)]
                tr3 += T.td[util.fmt_number(q.prev.volume)]
                tr3 += T.td[util.fmt_number(q.volume)]
                if e.amc and q.next:
                    tr3 += T.td("&nbsp;")
                    tr3 += T.td(align="center", colspan=3)[util.fmt_number(q.next.volume)]
                tr4 += T.td("&nbsp;")
                tr4 += T.td("&nbsp;")
                if have_last_quote:
                    tr4 += T.td(fmt_cci(q.prev.prev.prev.prev.cci()))
                    tr4 += T.td(fmt_cci(q.prev.prev.prev.cci()))
                    tr4 += T.td(fmt_cci(q.prev.prev.cci()))
                    tr4 += T.td(fmt_cci(q.prev.cci()))
                    tr4 += T.td(fmt_cci(q.cci()))
                else:
                    tr4 += T.td(fmt_cci(q.prev.prev.prev.cci()))
                    tr4 += T.td(fmt_cci(q.prev.prev.cci()))
                    tr4 += T.td(fmt_cci(q.prev.cci()))
                    tr4 += T.td(fmt_cci(q.cci()))
                    tr4 += T.td("&nbsp;")
                tr4 += T.td(colspan=3)['&nbsp;']
                if e.amc and q.next:
                    tr4 += T.td(fmt_cci(q.next.cci()))
                result.append(tr1)
                result.append(tr2)
                result.append(tr3)
                result.append(tr4)
                prev_date = None
                if e.prev:
                    prev_date = e.prev.date
                g = guidance.from_to(prev_date, e.date-1)
                if g:
                    result.append(T.tr[T.td(colspan=16)[fmt_guidance(g)]])
    else:
        print "XXX no earnings.History entry found"

    tr = T.tr(*map(T.th, ['Date/Period', 'est', 'act', 'Y ago', '-5 close',
                          '-4 close', '-3 close', '-2 close', '-1 close', 
                          'open', 'high', 'low', 'close',
                          '+1 open', '+1 high', '+1 low', '+1 close',
                          '+2 close', '+3 close']))
    filtered = filter(lambda x:x.date is not None and x.date < date, h.data)
    current = filter(lambda x:x.date is not None and x.date >= date, h.data)
    if current:
        current = current[-1]
    if filtered:
        result.append(tr)
    opens, highs, lows, closes, surprises = [], [], [], [], []
    e_next = None
    for i, e in enumerate(filtered[:10]):
        td = lambda *args, **kw: T.td(bgcolor="#eeeeee", *args, **kw)
        tr = T.tr
        q = e.quote(quotes)
        tr += td(e.raw_date())

        #XXX bez dalsieho riadku sa neda vygenerovat KOOL/7.9.6 ???
        #XXX aj IG:2007-04-10
        if not q or not q.prev or not q.prev.prev or not q.prev.prev.prev \
                 or not q.next or not q.next.next.next:
            continue

        # est, highlight if act > est
        color = None
        if (e.est is not None and e.act is not None):
            if e.act < e.est:
                color = "red"
            elif e.act > e.est:
                color = "green"
        est = e.est
        if est is None:
            est = ""
        tr += td(font("%s" % est, color=color, bold=True))
        # act, highlight if previous act < act
        color = None
        if (e.prev is not None and e.act and e.prev.act):
            if e.act < e.prev.act:
                color = "red"
            elif e.act > e.prev.act:
                color = "green"
        act = e.act
        if e.act is None:
            act = ""
        tr += td(font("%s" % act, color=color))
        # year_ago, highlight if year_ago < act
        color = None
        if (e.year_ago and e.act):
            if e.act < e.year_ago:
                color = "red"
            elif e.act > e.year_ago:
                color = "green"
        tr += td(font(e.year_ago or "", color=color))
        tr += td(q.prev.prev.prev.prev.prev.close)
        tr += td(q.prev.prev.prev.prev.close)
        tr += td(q.prev.prev.prev.close)
        tr += td(q.prev.prev.close)
        tr += td(q.prev.close)
        tr += td(q.open)
        tr += td(q.high)
        tr += td(q.low)
        tr += td(q.close)
        tr += td(font(q.next.open))
        tr += td(q.next.high)
        tr += td(q.next.low)
        tr += td(q.next.close)
        tr += td(q.next.next.close)
        tr += td(q.next.next.next.close)
        result.append(tr)

        td = lambda a, b, color='white': T.td(util.pct_str(b, a), bgcolor=color)
        def tdc(base, close, bold=False, color='white', invert=False):
            return T.td(pct_str_color(close, base, bold=bold, invert=invert), bgcolor=color)
        tr2 = T.tr()
        if e.period():
            tr2 += T.td("Q%d %d" % (e.quarter, e.year))
        else:
            tr2 += T.td("&nbsp;")
        if e.est and e.act:
            pct = util.pct(e.est, e.act)
            if (e.act > e.est and e.act > 0 and e.est < 0):
                pct *= -1
            data = "%.2f%%" % pct
            surprises.append(pct)
        else:
            data = "&nbsp;"
        tr2 += T.td(colspan=2, align="center")[font(data)]
        tr2 += T.td("&nbsp;")
        tr2 += tdc(q.prev.prev.prev.prev.prev.close, q.prev.close, invert=1)
        tr2 += tdc(q.prev.prev.prev.prev.close, q.prev.close, invert=1)
        tr2 += tdc(q.prev.prev.prev.close, q.prev.close, invert=1)
        tr2 += tdc(q.prev.prev.close, q.prev.close, invert=1)
        tr2 += T.td("&nbsp;")
        
        color = 'white'
        bmo = 0
        if e.bmo or not e.bmo and not e.amc and q.volume > q.next.volume and q.volume > q.prev.volume: # BMO
            color = 'lightgrey'
            bmo = 1
        tr2 += tdc(q.open, q.prev.close, bold=bmo, color=color)
        tr2 += tdc(q.high, q.prev.close, color=color)
        tr2 += tdc(q.low, q.prev.close, color=color)
        tr2 += tdc(q.close, q.prev.close, bold=bmo, color=color)

        color = 'white'
        amc = 0
        c = q.prev.close
        if e.amc or not e.bmo and not e.amc and q.next.volume > q.volume and q.next.volume > q.next.next.volume: # AMC
            color = 'lightgrey'
            amc = 1
            c = q.close
        tr2 += tdc(q.next.open, c, bold=amc, color=color)
        tr2 += tdc(q.next.high, c, color=color)
        tr2 += tdc(q.next.low, c, color=color)
        tr2 += tdc(q.next.close, c, bold=amc, color=color)

        tr2 += tdc(q.next.next.close, q.prev.close)
        tr2 += tdc(q.next.next.next.close, q.prev.close)

        result.append(tr2)

        fmt = lambda x: x is not None and ("%.2f" % x) or '&nbsp;'
        def fmt_re_hist(est, act, bold=True):
            result = T.td["&nbsp;"]
            if util.atof(est) and act:
                a, e = util.atof(act), util.atof(est)
                color = "black"
                val = util.pct(e, a)
                if a > e:
                    color = "green"
                    val = abs(val)
                elif e > a:
                    color = "red"
                    val = abs(val) * -1
                val = font("%.2f%%" % val, bold=bold, color=color)
                result = T.td[val]
            return result

        if i < 5:
            eps = re.hist_eps(i, e.period())
            rev = re.hist_rev(i, e.period())
            eps_pct = eps[2] and fmt_re_hist(eps[1], eps[2]) or T.td['&nbsp;']
            rev_pct = rev[2] and fmt_re_hist(rev[1], rev[2], bold=False) or T.td['&nbsp;']
            fmt_a_b = lambda x, y: '&nbsp;' #XXX rename
            tr3 = T.tr[ 
                T.td[eps[0] is None and '&nbsp;' or eps[0]],
                T.td[eps[1] or "&nbsp;"],
                T.td[eps[2] is None and '&nbsp;' or eps[2]],
                eps_pct,
                T.td[util.fmt_number(q.prev.prev.prev.prev.prev.volume)],
                T.td[util.fmt_number(q.prev.prev.prev.prev.volume)],
                T.td[util.fmt_number(q.prev.prev.prev.volume)],
                T.td[util.fmt_number(q.prev.prev.volume)],
                T.td[util.fmt_number(q.prev.volume)],
                T.td(colspan=4, align="center")[util.fmt_number(q.volume)],
                T.td(colspan=4, align="center")[util.fmt_number(q.next.volume)],
                T.td[util.fmt_number(q.next.next.volume)],
                T.td[util.fmt_number(q.next.next.next.volume)],
            ]
            tr4 = T.tr[
                T.td[rev[0] is None and '&nbsp;' or rev[0]],
                T.td[rev[1] or "&nbsp;"],
                T.td[rev[2] is None and '&nbsp;' or rev[2]],
                rev_pct,
                T.td()[fmt_cci(q.prev.prev.prev.prev.prev.cci())],
                T.td()[fmt_cci(q.prev.prev.prev.prev.cci())],
                T.td()[fmt_cci(q.prev.prev.prev.cci())],
                T.td()[fmt_cci(q.prev.prev.cci())],
                T.td()[fmt_cci(q.prev.cci())],
                T.td(colspan=3, align='center')["&nbsp;"],
                T.td()[fmt_cci(q.cci())],
                T.td(colspan=3, align='center')['&nbsp;'],
                T.td()[fmt_cci(q.next.cci())],
                T.td()[fmt_cci(q.next.next.cci())],
                T.td()[fmt_cci(q.next.next.next.cci())],
            ]
            result.append(tr3)
            result.append(tr4)
            prev_date = None
            if e.prev is not None:
                prev_date = e.prev.date
            g = guidance.from_to(prev_date, e.date)
            if g:
                result.append("<tr><td colspan=16>%s</td></tr>" % (fmt_guidance(g)))

        if e.bmo:
            opens.append(util.pct(q.prev.close, q.open))
            highs.append(util.pct(q.prev.close, q.high))
            lows.append(util.pct(q.prev.close, q.low))
            closes.append(util.pct(q.prev.close, q.close))
        else: # ID unknown is treated like AMC
            opens.append(util.pct(q.prev.close, q.next.open))
            highs.append(util.pct(q.prev.close, q.next.high))
            lows.append(util.pct(q.prev.close, q.next.low))
            closes.append(util.pct(q.prev.close, q.next.close))
        e_next = e
    result.append("</table>")
    history = "\n".join(map(str, result))
    f.write(unicode(history))

def html_analysts_estimates(f, ae, re, ze):
    print 'analysts estimates'
    print >> f, _navbar('analyst estimates')

    table = T.table[ T.tr[ T.td[( #AttributeError: 'Estimates' object has no attribute 'hist_raw'
                                 re.hist_raw or 'hist_raw: N/A<br>',
                                 re.trend_raw or 'trend_raw: N/A<br>', 
                                 re.rev_raw or 'rev_raw: N/A<br>',
                                )],
                           T.td[T.table[
                                  T.tr[
                                    T.td(colspan=2)[ 
                                      T.table[T.tr[
                                        T.td[ 
                                            re.est_raw or 'est_raw: N/A', 
                                        ],
                                        T.td[ 
                                            re.url2('reuters/Estimates'),
                                            T.br,
                                            ae.url2('yahoo/Estimates'),
                                            T.br,
                                            ze.url2('zacks/Estimates'),
                                        ]]]
                                    ]
                                  ],
                                  T.tr[
                                    T.td[
                                      ae.eps_est_raw,
                                      ae.rev_est_raw,
                                      ae.eps_hist_raw,
                                    ],
                                    T.td[
                                      ae.eps_trends_raw,
                                      ae.eps_rev_raw,
                                      ae.growth_est_raw
                                    ]
                                  ]
                                ]]]]
    print >> f, table

def html_TA(f, ta, quotes, date):
    print "TA"
    print >> f, _navbar('TA')
    q = quotes.get(date)
    if q is None and quotes.data.keys():
        q = quotes.last()
    MAs = T.table[ T.tr[ T.th[ "MA" ], T.th[ "Value" ] ] ]
    if q is not None:
        for period in (10, 20, 50, 100, 200):
            ma = q.ma(period)
            color = None
            if ma > q.close:
                color = "red"
            elif ma < q.close:
                color = "green"
            MAs += T.tr[ T.td[ 'MA %d' % period ],
                         T.td[ ma and font("%.2f" % ma, color=color) or 'N/A' ],
                   ]
    CCIs = T.table[ T.tr[ T.th["Close"], T.th[ "Percent" ], T.th[ "CCI" ] ] ]
    close = q.close
    tds = []
    for i in xrange(20):
        q.close *= Decimal("0.99")
        tds.append([q.close, i, q.cci()])
    for (a, b, c) in reversed(tds): 
        CCIs += T.tr[ T.td["%.2f" % a], T.td[b], T.td[fmt_cci(c)]]
    q.close = close
    for i in xrange(20):
        if not i: # 0 is included in previous loop
            continue
        q.close *= Decimal("1.01")
        CCIs += T.tr[ T.td["%.2f" % q.close], T.td[i], T.td[fmt_cci(q.cci())]]
    table = T.table[
              T.tr[
                T.td(colspan=2)[
                    ta.analysis_raw,
                ],
                T.td(rowspan=3)[CCIs]
              ],
              T.tr[
                T.td[ 
                      ta.SR_raw,
                      ta.indicators_raw,
                      ta.candlesticks_raw,
                      ta.gaps_raw,
                      MAs,
                    ],
                T.td[ 
                      T.img(src=ta.chart_cache_fn()),
                    ],
                  ],
                ]
    print >> f, table

def html_ao(f, ao, rao, date, last_rel, summary, yrr, ysa, mao, rar):
    print 'analyst opinion'
    print >> f, _navbar('analyst opinion')
    last_trade = summary.summary['Last Trade']
    table = T.table()[
              T.tr[
                T.td[
                    T.table()[
                        T.tr[ T.td(colspan=2)[ ao.recom_trends_raw or 'recom_trends_raw: N/A'],
                            ],
                        T.tr[ T.td[ ao.recom_sum_raw or 'recom_sum_raw: N/A'],
                              T.td[ ao.targets_hl(last_trade) or 'targets: N/A'],
                            ],
                        T.tr[ T.td[ ao.upgrades_hl(last_rel) or 'upgrades: N/A'],
                            ],
                        ],
                    ],
                T.td[ rao.opinion_raw or 'opinion_raw: N/A',
                      T.p,
                      rao.url2("reuters/AnalystOpinion"),
                      T.br,
                      rar.url2("reuters/AnalystResearch"),
                      T.p,
                      ao.url2("yahoo/AnalystOpinion"),
                      T.br,
                      yrr.url2("yahoo/ResearchReports"),
                      T.br,
                      ysa.url2("yahoo/StarAnalysts"),
                      T.p,
                      mao.url2("marketwatch/Ratings")
                    ],
                  ]
            ]
    print >> f, table


def html_aftermatch(f, re, ae, re3, g, quotes, pr, date, ts, y5d):
    if not re3.valid:
        print "XXX: invalid re3"
        return
    print "aftermatch"
    print >> f, _navbar('aftermatch')
    rev_act = util.atof(re3.hist[2][2])*1000000 
    eps_act = util.atof(re3.hist[-5][2]) 
    r = pr.get_earnings_report(date)
    if r:
        q = quotes.get_before_report(r.date)

        t = T.table(**{'class': 'dashed_border'})[
            T.tr[
                T.td[ "Ticker" ],
                T.td(colspan=5)[ "%s (%s)" % (re.name, str(r)) ],
            ],
            T.tr[
                T.td[ "Close" ],
                T.td(colspan=5)[ T.b[q.close] ],
            ],
            T.tr[
                T.td[ "CCI" ],
                T.td(colspan=5)[ fmt_cci(q.cci()) ],
            ],
            T.tr[
                T.td[ "EPS Q0" ],
                T.td[ re.q0.eps],
                T.td[ T.i[ae.q0.eps]],
                T.td[ eps_act ],
                T.td[ T.b[pct_str_color(re.q0.eps, eps_act)]],
                T.td[ T.i[pct_str_color(ae.q0.eps, eps_act)]],
            ],
            T.tr[
                T.td[ "REV Q0" ],
                T.td[ util.fmt_number(re.q0.rev)],
                T.td[ T.i[util.fmt_number(ae.q0.rev)]],
                T.td[ util.fmt_number(rev_act) ],
                T.td[ T.b[pct_str_color(re.q0.rev, rev_act)]],
                T.td[ T.i[pct_str_color(ae.q0.rev, rev_act)]],
            ],
            #T.tr[T.td[ "EPS Q1" ], T.td[re.q1.eps], T.td(colspan=4)[ae.q1.eps]],
            #T.tr[T.td[ "REV Q1" ], T.td[util.fmt_number(re.q1.rev)], T.td(colspan=4)[util.fmt_number(ae.q1.rev)]],
            #T.tr[T.td[ "EPS Y0" ], T.td[re.y0.eps], T.td(colspan=4)[ae.y0.eps]],
            #T.tr[T.td[ "REV Y0" ], T.td[util.fmt_number(re.y0.rev)], T.td(colspan=4)[util.fmt_number(ae.y0.rev)]],
            #T.tr[T.td[ "EPS Y1" ], T.td[re.y1.eps], T.td(colspan=4)[ae.y1.eps]],
            #T.tr[T.td[ "REV Y1" ], T.td[util.fmt_number(re.y1.rev)], T.td(colspan=4)[util.fmt_number(ae.y1.rev)]],
        ]
        for e in g.from_to(date-1, date):
            t += T.tr[T.td(colspan=6, bgcolor="darkgrey")[e.fmt_html()]]
        for d in reversed(pr.filter_from(util.prev_trading_day(date))):
            t += T.tr[T.td(colspan=6)[str(d)]]
        print >> f, t
        print >> f, T.img(src=y5d.cache_fn())
        t = T.table
        next = ts.get(r.date)
        while next and next.date.timedelta() < TimeDelta(hours=10):
            t += T.tr[T.td[next.date.datetime_str()], T.td[next.volume], T.td[next.close]]
            next = next.next
        print >> f, t
    else:
        print "No earning report for: %s" % pr.name



def stock_detail(symbol, date, output_dir, pages):
    root = os.path.join(config.DB_DIR, date.date_str(), 
        "%s_%s_%%s.zip" % (date.date_str(), symbol))
    dir = root % "-1"
    dir0 = root % "0"
    dir3 = root % "3"
    assert os.path.exists(dir), dir

    s = util.cache_page(pages, 'yahoo.summary', yahoo.Summary, dir, symbol)
    if not s.valid:
        print "stock_detail: invalid yahoo.Summary: %s:%s" % \
            (symbol, date.date_str())
        return

    guidance = util.cache_page(pages, 'briefing.Guidance', briefing.Guidance, dir, symbol)
    guidance3 = util.cache_page(pages, 'briefing.Guidance', briefing.Guidance, dir3, symbol)

    p = util.cache_page(pages, 'yahoo.profile', yahoo.Profile, dir, symbol)
    h = util.cache_page(pages, 'yahoo.history', earnings.History, dir, symbol)
    ks = util.cache_page(pages, 'yahoo.keystats', yahoo.Keystats, dir, symbol)
    short_int = util.cache_page(pages, 'nasdaq.ShortInterest', nasdaq.ShortInterest, dir, symbol)
    etrade = util.cache_page(pages, 'clearstation.TA_1y', clearstation.TA_1y, dir, symbol)
    ae = util.cache_page(pages, 'yahoo.AnalystEstimates', yahoo.AnalystEstimates, dir, symbol)
    re = util.cache_page(pages, 'reuters.Estimates', reuters.Estimates, dir, symbol)
    re3 = util.cache_page(pages, 'reuters.Estimates', reuters.Estimates, dir3, symbol)
    ao = util.cache_page(pages, 'yahoo.AnalystOpinion', yahoo.AnalystOpinion, dir, symbol)
    rao = util.cache_page(pages, 'reuters.AnalystOpinion', reuters.AnalystOpinion, dir, symbol)
    insiders = util.cache_page(pages, 'yahoo.Insiders', yahoo.Insiders, dir, symbol)
    quotes = util.cache_page(pages, 'yahoo.Quotes', yahoo.Quotes, dir, symbol)
    quotes3 = util.cache_page(pages, 'yahoo.Quotes', yahoo.Quotes, dir3, symbol)
    sta = util.cache_page(pages, 'stockta.Analysis', stockta.Analysis, dir, symbol)
    ts0 = util.cache_page(pages, 'nasdaq.TimesSales', nasdaq.TimesSales, dir0, symbol, date)
    pr0 = util.cache_page(pages, 'marketwatch.PR', marketwatch.PR, dir0, symbol)
    yahoo_5d3 = util.cache_page(pages, 'yahoo.TA_5d', yahoo.TA_5d, dir3, symbol)
    yahoo_5d = util.cache_page(pages, 'yahoo.TA_5d', yahoo.TA_5d, dir, symbol)
    gs = google.Summary(dir, symbol)
    ro = reuters.Overview(dir, symbol)
    msno = msn.Ownership(dir, symbol)
    ymh = yahoo.MajorHolders(dir, symbol)
    mwo = marketwatch.Options(dir, symbol)
    mwn = marketwatch.News(dir, symbol)
    mso = morningstar.Options(dir, symbol)
    yo = util.cache_page(pages, 'yahoo.Options', yahoo.Options, dir, symbol)
    oo = reuters.Options(dir, symbol)
    ze = zacks.Estimates(dir, symbol)
    yrr = yahoo.ResearchReports(dir, symbol)
    ysa = yahoo.StarAnalysts(dir, symbol)
    mao = marketwatch.Ratings(dir, symbol)
    rar = reuters.AnalystResearch(dir, symbol)
    nrt = nasdaq.RealTime(dir, symbol)
    ab = arca.Book(dir, symbol)
    yh = yahoo.News(dir, symbol, None, None)

    last_rel = h.last(date)
    if last_rel:
        last_rel = last_rel.date

    _copy_from_zip(etrade, output_dir)
    _copy_from_zip(sta, output_dir, fno=sta.chart_cache_fn(), fni=sta.chart_cache_fn())
    _copy_from_zip(yahoo_5d3, output_dir)
    _copy_from_zip(yahoo_5d, output_dir, fno="pre_%s" % yahoo_5d.cache_fn())
    _copy_from_zip(yo, output_dir)

    index_html = os.path.join(output_dir, 'index.html')
    f = codecs.open(index_html, 'w', 'latin1')

    html_head(f, s, h, date)
    ignore_errors(html_summary, f, s, h, p, ks, etrade, quotes, date, re, ae, gs, ro, nrt, ab, yahoo_5d)
    ignore_errors(html_history, f, h, quotes3.valid and quotes3 or quotes, short_int, date, re, ae, guidance)
    ignore_errors(html_analysts_estimates, f, ae, re, ze)
    ignore_errors(html_ao, f, ao, rao, date, last_rel, s, yrr, ysa, mao, rar)
    ignore_errors(html_ownership, f, msno, ymh)
    ignore_errors(html_insiders, f, s, insiders, h, date, output_dir)
    ignore_errors(html_news, f, mwn, yh, gs)
    ignore_errors(html_TA, f, sta, quotes, date)
    ignore_errors(html_options, f, mwo, mso, yo, ro)
    ignore_errors(html_aftermatch, f, re, ae, re3, guidance3, quotes3, pr0, date, ts0, yahoo_5d3)

    html_tail(f)
    f.close()
    print
    print index_html


if __name__ == "__main__" :
    from optparse import OptionParser

    usage = "%prog [options] <date> <symbol> <output_dir>"
    parser = OptionParser(usage=usage)
    opts, args = parser.parse_args()

    if len(args) == 3:
        date, symbol, output_dir = args
        date = util.Date(date)
    else:
        parser.error("please set correct arguments")
    symbol = symbol.upper()

    if os.path.exists(output_dir):
        parser.error("output_dir must not exist")
    util.mkdir(output_dir)

    stock_detail(symbol, date, output_dir, {})
