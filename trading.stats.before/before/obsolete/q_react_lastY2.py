from trading.stats.before.obsolete.q_react_lastY import LastYearReaction, main

class LastYearReaction2P(LastYearReaction):
    Abbr = 'react_lastY2'
    Periods = 2

if __name__ == '__main__':
    main(LastYearReaction2P)
