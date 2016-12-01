from trading.stats.before.q_inst_shares import InstitutionsShares, main, activity_data

class InstitutionsShares2(InstitutionsShares):
    Significance = dict(gap_up=2)
    Abbr = "inst_shares2"

    def answer(self, data, strategy):
        info, activity = data
        if activity_data(activity, idx=1):
            buyers, sellers, total, new, soldout = activity_data(activity)
            if strategy == 'gap_up':
                return total < new*1.5

if __name__ == '__main__':
    main(InstitutionsShares2)
