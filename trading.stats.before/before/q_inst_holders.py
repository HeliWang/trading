from trading.data.msn import Ownership
from trading.stats.before.question import Question, main
from trading import util

import os

def activity_data(activity, idx=0):
    buyers = activity['Buyers'][idx]
    sellers = activity['Sellers'][idx]
    total = activity['Total Positions'][idx]
    new = activity['New Positions'][idx]
    soldout = activity['Soldout Positions'][idx]
    if None in (buyers, sellers, total, new, soldout):
        return None
    return buyers, sellers, total, new, soldout


class InstitutionsHolders(Question):
    Abbr = "inst_holders"
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Significance = dict(gap_up=1)

    def answer(self, data, strategy):
        info, activity = data
        if activity_data(activity):
            buyers, sellers, total, new, soldout = activity_data(activity)
            if strategy == 'gap_up':
                return total < new*2 and buyers > sellers*3
                #return soldout < new*.15
            if strategy == 'gap_down':
                return 

    def _data_from_db(self):
        o = self.cache_page('msn.Ownership', Ownership)
        if not o.valid or not o.activity or not o.info:
            return
        return o.info, o.activity

    def _optimalize(self, data):
        info, activity = data
        return activity_data(activity)

if __name__ == '__main__':
    main(InstitutionsHolders)
