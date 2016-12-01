from trading.stats.before.q_inst_holders import InstitutionsHolders, activity_data, main

class InstitutionsShares(InstitutionsHolders):
    Significance = dict(gap_up=1)
    Abbr = "inst_shares"

    def answer(self, data, strategy):
        info, activity = data
        if activity_data(activity, idx=1):
            buyers, sellers, total, new, soldout = activity_data(activity)
            if strategy == 'gap_up':
                return soldout < new*.15
                #return soldout < new*.2
                #return soldout < new*.15 and buyers > sellers*5
            if strategy == 'gap_down':
                return 

    def _optimalize(self, data):
        info, activity = data
        return activity_data(activity, idx=1)

if __name__ == '__main__':
    main(InstitutionsShares)
