from trading.stats.before.q_insiders_accum import InsidersAccumulation, main

class InsidersPurchases(InsidersAccumulation):
    Abbr = "insid_purch"
    Significance = dict(gap_up=3)

    def answer(self, data, strategy):
        i, quotes, dates = data

        new = filter(lambda x: x.date is not None and (x.date >= self.date-self.DaysBack), i.data)
        if not new:
            return
        acc, dist = self._acc_dist(new, quotes)
        acc2 = []
        dist2 = []
        for a in acc:
            if a.value < 10000 and a.value > 300000:
                continue
            acc2.append(a)
        for d in dist:
            if d.action() < -2:
                dist2.append(d)
        if strategy == 'gap_up':
            return len(acc2) > 0 and len(dist2) == 0


if __name__ == '__main__':
    main(InsidersPurchases)
