from trading.stats.before.q_inst_holders import InstitutionsHolders, main, activity_data

class InstitutionsHoldersContra(InstitutionsHolders):
    Abbr = "inst_holders_contra"
    Significance = dict(gap_up=1)

    def answer(self, data, strategy):
        info, activity = data
        if activity_data(activity):
            buyers, sellers, total, new, soldout = activity_data(activity)
            if strategy == 'gap_up':
                return sellers > buyers*5

if __name__ == '__main__':
    main(InstitutionsHoldersContra)
