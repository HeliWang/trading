from q_est_eps_rev_reuters import EPSRevisionsReuters, main

class RevRevisionsReuters(EPSRevisionsReuters):
    Abbr = "rev_rev_reuters"
    Row = 2
    Significance = dict(gap_down=2, gap_up=2)

if __name__ == '__main__':
    main(RevRevisionsReuters)
