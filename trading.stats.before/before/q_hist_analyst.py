from trading.stats.before.q_hist_yy import YYSurprise, main

class AnalystSurprise(YYSurprise):
    Abbr = "A_surp"
    Significance = dict(gap_up=3, gap_down=3)

    def _compute(self, data):
        earnings = filter(lambda x: x.date is not None, data)
        earnings = filter(lambda x: x.date < self.date, earnings)
        result = []
        for e in earnings[:self.Periods]:
            if e.act is not None and e.year_ago is not None:
                result.append(cmp(e.act, e.year_ago))
            else:
                result.append(0)
        return result

if __name__ == '__main__':
    main(AnalystSurprise)
