from trading.stats.before.q_options import Options, main
from trading import util

class Options2(Options):
    Abbr = "options2"

    def answer(self, data, strategy):
        o, s = data
        #XXX factorize computing to a method in Options
        price = s.summary.get('Last Trade')
        puts_vol = sum(map(lambda x:x.volume, o.puts))
        calls_vol = sum(map(lambda x:x.volume, o.calls))
        puts_vol2 = sum(map(lambda x:x.volume*(price-x.strike), o.puts))
        calls_vol2 = sum(map(lambda x:x.volume*(x.strike-price), o.calls))
        puts_vol3 = sum(map(lambda x:x.open_int, o.puts))
        calls_vol3 = sum(map(lambda x:x.open_int, o.calls))
        c, p, c2, p2 = 0, 0, 0, 0
        for e in o.calls:
            if e.volume >= e.open_int: 
                if price > e.strike:
                    c+=1
                else:
                    c2+=1
        for e in o.puts:
            if e.volume >= e.open_int:
                if price < e.strike:
                    p += 1
                else:
                    p2+=1
        r1 = puts_vol and calls_vol/float(puts_vol) or 0
        r2 = puts_vol2 and calls_vol2/float(puts_vol2) or 0
        r3 = puts_vol3 and calls_vol3/float(puts_vol3) or 0
            
        if strategy == 'gap_up':
            return r3 < r1 < r2 and not p2 and not c and not c2
            #return not not (r3 > r1 > r2  and p and c and c2)
        elif strategy == 'gap_down':
            return
 
if __name__ == '__main__':
    main(Options2)
