from trading.data import reuters
from trading.stats.before.question import Question, main
from trading import util

import os

def summarize_estimates(re, re2): #XXX move to a better place?
    # now + year ago
    yago_rev = util.atof(re2.hist[6][2])
    yago_eps = util.atof(re2.hist[12][2])
    now_rev = util.atof(re2.hist[2][2])
    now_eps = util.atof(re2.hist[8][2])
    est_rev = util.atof(re2.hist[2][1])
    est_eps = util.atof(re2.hist[8][1])
    # next q
    nq_rev_old = util.atof(re.est[3][2])
    nq_eps_old = util.atof(re.est[8][2])
    nq_rev_new = util.atof(re2.est[2][2])
    nq_eps_new = util.atof(re2.est[7][2])
    # this/next y
    if re.est[4][0] != re2.est[4][0]:
        o_rev_old = util.atof(re.est[5][2])
        o_eps_old = util.atof(re.est[10][2])
        o_rev_new = util.atof(re2.est[4][2])
        o_eps_new = util.atof(re2.est[9][2])
    else:
        o_rev_old = util.atof(re.est[4][2])
        o_eps_old = util.atof(re.est[9][2])
        o_rev_new = util.atof(re2.est[4][2])
        o_eps_new = util.atof(re2.est[9][2])
    return yago_rev, yago_eps, now_rev, now_eps, est_rev, \
           est_eps, nq_rev_old, nq_rev_new, nq_eps_old, \
           nq_eps_new, o_rev_old, o_rev_new, o_eps_old, o_eps_new

class PostReaction(Question):
    CacheFN = "%s.cache" % os.path.splitext(__file__)[0]
    Abbr = "post_reaction"

    def answer(self, data, strategy):
        yago_rev, yago_eps, now_rev, now_eps, est_rev, \
        est_eps, nq_rev_old, nq_rev_new, nq_eps_old, \
        nq_eps_new, o_rev_old, o_rev_new, o_eps_old, o_eps_new = data
        return yago_rev < now_rev and yago_eps < now_eps and \
               now_rev > est_rev and now_eps > est_eps and \
               o_rev_old < o_rev_new and o_eps_old < o_eps_new

    def _data_from_db(self):
        re = self.cache_page('reuters.Estimates', reuters.Estimates)
        re2 = util.cache_page(self.pages, 'reuters.Estimates/3',
                              reuters.Estimates, self.dir[:-2]+'3', self.symbol
                             )
        if not re.valid or not re2.valid:
            return
        if not re2.hist or not re2.est or not re.est:
            return
        return summarize_estimates(re, re2)

if __name__ == '__main__':
    main(PostReaction)
