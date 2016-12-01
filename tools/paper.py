from trading import util

# short_outlook: rychla akcia
short_outlook_bad = {
    '2007-01-03': ['merx'],
    # hele, lwsn: gap - usiel vlak
    # exfo: hrozny outlook -> +7%. maly volume, dlhodobo vypredana
    '2007-01-09': ['hele', 'lwsn', 'exfo', 'gbx'],
    '2007-01-16': ['lltc', 'amtd', 'mnro'],
    '2007-01-18': ['cof', 'xlnx', 'bgg', 'camd'],
    '2007-01-19': ['jci'],
    '2007-01-22': ['pkg', 'plt'],
    '2007-01-23': ['mdp', 'tlab', 'smg', 'stm', 'cyn', 'idti', 'yhoo'],
    '2007-01-24': ['acat', 'cps', 'glw', 'exc', 'kmt', 'pmtc', 'eglt', 'kex', 
                   'smtl', 'stts', 'txt', 'ffiv', 'isil'],
}
short_outlook_neriesit = {
    '2007-01-03': ['sonc'],
    '2007-01-04': ['xrtx', 'arro'],
    '2007-01-08': ['lifc'],
    '2007-01-09': ['ri'],
    '2007-01-11': ['srr', 'ihs'],
    '2007-01-16': ['lcbm', 'ful', 'amtd'],
    '2007-01-17': ['dox', 'aph'], 
    '2007-01-18': ['cree', 'vivo', 'molx'],
    '2007-01-19': ['ge', 'mot'],
    '2007-01-22': ['txn', 'wgov', 'aos', 'mspd'],
    '2007-01-23': ['utx', 'ctx', 'ctxs', 'avy', 'xrx', 'rfmd'],
    '2007-01-24': ['ame', 'hsy', 'symc', 'px', 'rgs', 'fic', 'wlp'],
}
short_outlook_good = {
    '2007-01-03': ['intv'],
    '2007-01-04': ['stz', 'uaph', 'hway', 'mon'],
    '2007-01-09': ['snx', 'oxm'],
    '2007-01-11': ['camp'],
    '2007-01-17': ['aapl', 'snv'],
    '2007-01-18': ['ait', 'smts', 'unh', 'dgii'],
    '2007-01-22': ['aldn', 'etn'], #etn = next Q down, this Y up
    '2007-01-23': ['dd', 'amd', 'cgnx', 'ptv'],
    # plxs: moc gapol, uz sa nedalo rozumne nastupit
    # acxm: nastup by bol tazky
    # var : mixed, next Q down, this Y up
    '2007-01-24': ['plxs', 'fdc', 'rok', 'acxm', 'lsi', 'qcom', 'ryl', 'ssti', 
                  'ter', 'var'], 
    #'2007-01-25': ['bebe', 'agr', 'bms', 'chic', 'cnxt', 'csh', 'gisx', 'har',
    #'ikn', 'imn', 'plxt'],
    #'2007-01-26': ['fo'],
    #'2007-01-29': ['cool', 'gnss'],
    #'2007-01-30': ['cls', 'mtw', 'tup'],
    #'2007-01-31': ['ads', 'newp', 'slab', 'srx'] # ads = mixed, next Q up, year down
}

# short_overbought: rychla akcia
# inline (mierne lepsie = +1-2c) zverejnenie, (silne) prekupena akcia
short_overbought_bad = {
    '2007-01-09': ['gbx', 'ri'],
    '2007-01-16': ['mnro'],
    # STT sice nie je iba +1c, ale aj hrozne prekupena
    '2007-01-17': ['stt'], 
    '2007-01-19': ['jci'],
    '2007-01-22': ['csx', 'cbss'],
    '2007-01-23': ['bni', 'eat', 'mdp', 'smg', 'utx', 'vcbi'],
    '2007-01-24': ['flws', 'abt', 'cxg', 'eth', 'nyb', 'rgs', 'kex'],
}

short_overbought_neriesit = {
    '2007-01-08': ['horc'], # firma bude odkupena
    '2007-01-11': ['srr'],  # vypredana, dobre zverejenenie
    '2007-01-16': ['lltc',  # sa znacne vypredala, na druhy den nasledoval
                            # mierny pullback, long term, den na to padla 3.3%
                   'fult', 'cbh'],
    # cit: vypredana, dobre zverejenenie a outlook
    '2007-01-17': ['cit', 'sov', 'ibkc', 'vly', 'sov', 'wfc'],  
    '2007-01-18': ['vivo', 'fnb', 'molx'], 
    '2007-01-19': ['aco', # skor vypredana, slusne zverejnenie
                  'c',    # skor vypredana, slusne zverejnenie (E +3%, R +5%)
                  'mot', 'key'
                  ], 
    '2007-01-22': ['txn'],
    # aks: moc dobre zverejnenie
    '2007-01-23': ['qi', 'blk', 'av', 'emc', 'sbib', 'stm', 'ucbi', 'xrx',
                   'tlab', 'aks'], 
    # swft: takeover, takze neriesit
    # eglt: zaujimavost, silne vypredana, dobre zverejnila, ale dala 
    #       hrozny outlook a hrozne narastla 
    # cvg:  silne prekupena, avsak velmi dobre zverejnenie
    # ame:  mierne prekupena, velmi dobre zverejnenie
    # fic:  velmi mierne prekupena, zmiesany outlook
    # var, komg:  po zverejneni sa rychlo vypredala, malo priestoru na nastup
    # talx: dobre E, zle R, dobry outlook, len mierne prekupene
    '2007-01-24': ['ame', 'cps', 'cvg', 'fcfs', 'mkc', 'mwrk', 'eglt', 'plxs',
                   'pssi', 'swft', 'wstl', 'fic', 'var', 'wlp', 'komg', 'talx'],
}

short_overbought_good = {
    '2007-01-03': ['sonc'],
    '2007-01-04': ['hway'], # hway je skor outlook hra a je znacne vypredana
    '2007-01-05': ['gpn'],
    # mtb: target je startovaci bod spekulacie z predosleho dna
    '2007-01-11': ['mtb'], 
    '2007-01-16': ['intc', 'pvtb', 'mi'],
    '2007-01-17': ['cnb', 'ntrs', 'luv'],
    '2007-01-18': ['cree', 'ait', 'nite', 'chz', 'hog', 'smts', 'unh', 'ibm', 
                   'igt'],
    '2007-01-19': ['ge', 'sti'],
    # cgnx: (dovod =) inline zverejnenie, zly outlook
    '2007-01-23': ['ptv', 'bac', 'cmco', 'dd', 'jnj', 'cgnx', 'phhm'], 
    '2007-01-24': ['ati', 'gd', 'mcd', 'nsc', 'cbst', 'knx', 'xjt', 'tsm', 
                   'fdc', 'lsi', 'sns'],
    #'2007-01-25': ['cvd', 'dde', 'swks', 'zigo'],
}

quality = {
    '2007-01-04': ['mtrx'],
    '2006-12-18': ['joyg'],
    '2006-12-05': ['wwe'],
    '2006-12-04': ['cmtl'],
    '2006-11-30': ['grb'],
    '2006-11-27': ['dci'],
    '2006-11-21': ['jbx', 'gco'],
    '2006-11-16': ['ptry'],
    '2006-11-15': ['dakt'],
    '2006-11-13': ['knot'],
    '2006-11-07': ['ftek', 'igt'],
    '2006-11-02': ['djo'],
    '2006-10-26': ['ltm', 'hot'],
    '2006-10-24': ['idti'],
    '2006-10-23': ['radn'],
}

reactions_wait_in_EH = { # cakat na profit v EH 
    '2007-01-23': ['pcp'], 
    '2007-01-18': ['mer'], # necakat moc dlho, silne prepredana
    '2007-01-17': ['asml'], # nedal, tak brat co bolo
    '2007-01-04': ['mtrx', 'blud'],
    '2006-12-22': ['wag'],
    '2006-12-14': ['cien', 'becn/s', 'asfi'], 
    '2006-12-18': ['joyg'],
    '2006-12-05': ['layn'], 
    '2006-12-04': ['cmtl'], 
}

reactions_run_in_EH = { # brat co davaju v EH ci zdrhat - XXX mam tu blbosti
    '2007-01-30': ['axe', 'cl'],
    '2007-01-23': ['coh', 'avy', 'utx', 'qi', 'alb', 'qlgc'],
    '2007-01-22': ['aos', 'cbu', 'nwk', 'boh', 'axp'],
    '2007-01-18': ['cma', 'camd', 'molx', 'bk', 'dgii', 
                   'vivo', # sakra prekupene
                    'hog', # -"-
                   ],
    '2007-01-17': ['jpm', 'len', 'lrcx', 'aph', 'iivi', 'snv',
                  'dox', # dobre vysledky ale horsi outlook ... -> run,
                  ],
    '2007-01-16': ['fcx', 'mnro'],
    '2007-01-11': ['mtb', 'ihs'],
    '2007-01-10': ['dna', 'igte'],
    '2007-01-09': ['lwsn', 'ri', 'snx'],
    '2007-01-05': ['azz'],
    '2007-01-04': ['msm', 'rpm', 'saba'],
    '2006-12-21': ['tibx', 'rimm'],
    '2006-12-20': ['fdo', 'fdx', 'coms', 'hei'],
    '2006-12-19': ['ms', 'chap', 'palm', 'smod', 'fsii'],
    '2006-12-14': ['bsc', 'leh', 'adbe'], 
    '2006-12-12': ['gs', 'matk'],
    '2006-12-08': ['siro'],
    '2006-12-07': ['cae', 'shwc'],
    '2006-12-06': ['gii', 'lqdt', 'issc'], 
    '2006-12-05': ['gil' # nidky taky maly EPS surprise -> nedufat a run
                  ,'ttc' , 'nsm' , 'pay'],
    '2006-12-05': ['tol/s', 'wwe'], 
    '2006-12-04': ['cnqr'], 
}

reactions_short = { # shorty po a revertnute longy
    '2007-01-30': ['glyt'],
    '2007-01-23': ['dd', 'ptv'],
    '2007-01-18': ['unh', 'igt'],
    '2007-01-17': ['aapl'],
    '2007-01-05': ['gpn'],
    '2006-12-20': ['pke', 'air'],
    '2006-12-19': ['cc'],
    '2006-12-14': ['tek'],
    '2006-12-06': ['kfy'],
}

reactions_wait_for_open = { # mame dovod cakat na open -> blbost vybrat v EH
    '2007-01-31': ['hsc'],
    '2007-01-30': ['bkc'],
    '2007-01-22': ['bkuna'],
    '2007-01-17': ['mel'],
    '2007-01-11': ['crai'],
    '2006-12-21': ['cag'],
    '2006-12-12': ['abm'],
}

reactions_nightmare = {
    '2007-01-23': ['coh', # lepsi outlook nic nove
                   'alb',
                  ],
    '2007-01-18': ['cma'],
    '2007-01-17': ['mel', # silne prekupeny - brat co bolo?
                   'len',
                   'svn', # silne prekupeny
                   ], 
    '2007-01-11': ['ihs'],
    '2006-12-14': ['adbe'],
    '2006-12-08': ['siro'],
    '2006-12-06': ['issc'],
}

# "tricky" reactions
reactions = {
    '2007-01-26': ['crs'],
    '2007-01-23': ['coh'],
    '2006-10-04': ['arro'],
    '2006-10-05': ['mar'],
    '2006-10-11': ['yum'], # preco YUM narastla? TA stock?
    '2006-10-13': ['fnfg'],
    '2006-10-18': ['kea', 'stj', 'seic', 'wdfc'],
    '2006-10-23': ['athr'],
    '2006-10-25': ['snwl', 'rnow'],
    '2006-10-26': ['hot'],
    '2006-10-27': ['nni', 'vvi'],
    '2006-10-31': ['etr', 'pg'],
    '2006-11-01': ['shoo', 'diod', 'cam'],
    '2006-11-02': ['prft'],
    '2006-11-03': ['omg'],
    '2006-11-07': ['cse'],
    '2006-11-27': ['dci'],
    '2006-11-09': ['urbn'],
    '2006-12-06': ['gef'],
    '2006-12-07': ['dmnd', 'ttc', 'utiw'],
    '2006-12-20': ['pke', 'air'],
}

juggler = { 
    '2007-11-20': ['bcsi'], # nakup okolo 33, vyber zisku u 37
    '2007-11-14': ['gigm'], # necakal na zverejnenie, buy za 17, sell u 18 a 19
    '2007-02-28': ['joyg', 'mso', 'vphm', 'wolf', 'ocr/s'],
    '2007-02-27': ['vtiv', 'nmrx', 'geo', 'lkqx', 'fdp/s', 'msa/s'],
    # crdn najskor ohodnotil na 62, neskor si to premyslel a bral u 61
    '2007-02-26': ['crdn', 'mvl', 'abbi', 'dco'], 
    '2007-02-22': ['ksws'], # obratil na short
    '2007-02-21': ['jbx', 'gpi', 'nice', 'poss/s'],
    '2007-02-14': ['ko', 'micc', 'jah', 'kdn'],
    '2007-02-09': ['ma/s'], # short po
    '2007-02-07': ['whr/s', 'rl/s'], # shorty po
    '2007-01-31': ['holx', 'hsc', 'www', 'ctec'],
    '2007-01-30': ['glyt', 'axe', 'man', 'arm', 'dbd', 'ipsu'],
    '2007-01-24': ['ati', 'pjc', 'wat', 'mkc'],
    '2007-01-23': ['jec', 'pcp', 'coh', 'tlab/s'],
    '2007-01-22': ['bkuna'],
    '2007-01-18': ['smts', 'ait', 'igt', 'mer', 'bgg/s'],
    '2007-01-16': ['lltc'],
    '2007-01-05': ['gpn'],
    '2007-01-04': ['mtrx', 'stz/s'],
    '2006-12-07': ['josb'],
    '2006-11-30': ['vip', 'grb', 'hnz'],
    '2006-11-22': ['hrl', 'poss/s'],
    '2006-11-21': ['jbx', 'tecd/s', 'gco', 'bws'],
    '2006-11-20': ['pvh'],
    '2006-11-16': ['ptry', 'shld', 'zoll', 'big'],
    '2006-11-15': ['cpa', 'chrs', 'twb', 'dakt'],
    '2006-11-14': ['fosl', 'nafc/s'],
    '2006-11-13': ['knot'],
    '2006-11-07': ['ftek'],
    '2006-11-03': ['cryp'],
    '2006-11-01': ['grmn'],
    '2006-08-31': ['joyg'],
    '2006-08-21': ['low'],
    '2006-08-18': ['ann'], # vyber zisku u 42.99, short u 43.99
    '2006-08-16': ['dakt'],
    '2006-08-15': ['jrjc/s'],
    '2006-08-09': ['asei'],
    '2006-08-08': ['jbx'],
    '2006-08-07': ['aes', 'hans', 'ftek', 'lojn'],
    '2006-08-03': ['cryp'],
    '2006-08-02': ['grmn'],
}

paper = { 
    '2007-12-20': ['am', 'cag'],
    '2007-12-18': ['gs', 'fds'],
    '2007-12-17': ['adbe'],
    '2007-12-12': ['adct', 'mgln'],
    '2007-02-01': ['sta', 'seic', 'cvs', 'onnn'],
    '2007-01-30': ['bkc', 'axe', 'glyt', 'cl'],
    '2007-01-23': ['pcp', 'coh'],
    '2007-01-22': ['boh', 'bkuna'],
    '2007-01-18': ['nite'],
    '2007-01-17': ['asml', 'aapl'],
    '2007-01-09': ['snx'],
    '2007-01-05': ['gpn'],
    '2006-12-19': ['cc'],
    '2006-12-07': ['utiw', 'josb', 'gil', 'mov'],
    '2006-12-06': ['kfy'],
    '2006-12-05': ['tol/s', 'wwe'],
    '2006-12-04': ['cmtl'],
    '2006-11-30': ['hnz'],
    '2006-11-28': ['jtx', 'ccc', 'amwd'],
    '2006-11-27': ['dci'],
    '2006-11-22': ['hrl', 'poss/s'],
    '2006-11-21': ['dltr', 'mesa/s', 'fred/s'],
    '2006-11-20': ['low/s'],
    '2006-11-17': ['ctrn'],
    '2006-11-16': ['smrt/s', 'cle/s', 'ptry', 'scvl'],
    '2006-11-14': ['spls', 'tjx', 'tecua/s'],
    '2006-11-13': ['knot', 'tsn/s', 'wnr'],
    '2006-11-09': ['urbn/s', 'won/s', 'bid', 'rsti', 'win'],
    '2006-11-07': ['mwiv', 'pfgc', 'igt', 'fcl/s', 'cse'],
    '2006-11-02': ['djo', 'glt', 'wres/s', 'faf/s', 'prft/s'],
    '2006-11-01': ['grmn', 'cam', 'cinf/s', 'ag/s', 'diod', 'svm/s'],
    '2006-10-31': ['pg', 'asvi/s', 'etr', 'agr', 'safc', 'nte/s'],
    '2006-10-30': ['hum', 'tri/s', 'dco/s'],
    '2006-10-27': ['vvi', 'nni/s', 'cah/s', 'itt', 'avp'],
    '2006-10-26': ['lii', 'tdy', 'sta', 'ltm', 'gr', 'hot'],
    '2006-10-25': ['talx', 'bebe', 'woof', 'ba', 'apd', 'ati', 'ber', 'px'],
    '2006-10-24': ['ajg', 'idti', 'cr', 'cmco', 'pnr', 'axe', 'ips', 'pcp', 'omc'], 
    '2006-10-23': ['athr', 'pre', 'grp', 'cnet/s', 'f/s', 'has', 'wft'],
}

long_before = { 
    '2006-10-23': ['t', # +r, ~i, ~t
                   'has',  # insider game, ~t, ~r, +ao
                   'kmb', # -i, ~r, +t -> redukovat
                   'wft', # ~r, -t, +i -> redukovat
                   'bucy', # ~r, 0 t, +i XXX
                   'grp',  # ~r (mierne +), +t -> mensia pozicia
                   'nati', # +r, +t, ~i
                   'pre', # +r, +t, +i
                   'rga', # +r, ~t, +i -> mensia pozicia (prepredanost)
                   'uctt', # +history, +r, zvysok 0
                   'inin', # +r, +t, +ins
                   'nflx', # ~r, +i, +ao -> zistit dovod preco padli naposledy
                   'athr', # +t, +i, ~/+ r
                   #'rok', # ~i, -r, ~t => neriesit
                   #'dspg', # +r, -t => neriesit
                   #'kft',  # -r, -i, -ao => neriesit
                   #'ptp', # -r -> mensia pozicia / neriesit
                   #'xprsa', # 0 i, -r, +t => neriesit
                   #'radn', # -i, +r, 0 t => neriesit
                   ],
    '2006-10-24': ['axe',
                   'bkuna', # +r, +t, ~/+ i
                   'cls', # mala pozicia, short po
                   'cmco', 
                   'cbe', # +t, +r, ~/- i
                   'dd', # +t, ~r, ~i
                   'epe', # ~t, +r, +i (asi by som neriesil - male volume)
                   'ips', # +t, ~/+ r, ~/+ i
                   'ryn', # ~/+ t, +r, +ao
                   #'tlab', #~t, ~r, -i
                   #'',
                   'ajg', # +r, ~t, +i
                   #'glw', # -t, ~i, +r => neriesit
                   'cr', # rychlo zdrhat
                   'wire', # +r, 0r, 0i -> mensia pozicia / neriesit
                   'enwv', # ~t, 0 r, +i
                   'idti', 
                   'mtw', # ~/+ t, +r, ~i => mala pozicia
                   #'qlgc', # ~/- t, +r, ~/+ i
                   'seab', # insider gamble: ~r, 0r, +i
                   #'sie', # -t, ~r, +i, neriesit!
                   #'sgtl', #-t, +r, ~i => neriesit
                   'trmb', # +t, 0 r, +/~ i => XXX
                   #'coh', # ~/+ t, +r, -/~ i => neriesit (hoci vysla)
                   'cmc',
                   'cymi', # XXX, preco padol naposledy, moc sa vypredal v AMC
                   'iivi', # +t, ~r, ~/- i -> mensia pozicia XXX
                   # 'lvlt', #-t, +r, ~/+ i -> neriesit
                   'ntri',
                   'omc', # ~t, +r, ~i
                   'pcp', # ~/+t, +r, ~i
                  ],
    '2006-10-25': ['apd', # ~/+t, +r, ~i
                   'ati',
                   'abi', # +r, +t, ~/+ i
                   #'avx', # ~/+ t, 0r, ~i  -> neriesit
                   'ctec', # r 0, ~ i, +t -> t gamble
                   'cnh', # r 0, i 0, +t -> t gamble
                   'cfr', #+i, +t, +/~ r (obratit na shorta?)
                   'edgw', # +i, +/~ t, ~/- r -> insider gamble
                   'ise', # +t, ~i, +r
                   #'lifc', # +/~ t, 0r, -i -> neriesit
                   'leco', # +t, 0r, 0i -> t gamble
                   #'mdp', # ~/+ t, +r, -i neriesit
                   'snwl',  # ~/+ t, +r, 0i 
                   'ber',  
                   'arg',  
                   'ahl', # ~/+ t, +r, 0i 
                   'cns',  # ~t, +r, +i 
                   #'cci',  # -t, +r, -i => neriesit
                   #'dgin',  # -i, -/~ t, +r (long after)
                   'kem',  
                   'ntct', # +r, 0r, 0i -> t gamble 
                   #'newp', # ~/- i, +t, 0r -> t gamble (neriesit)
                   'srcl',  # +t, ~i, 0i -> t gamble
                   #'talx', # +t, +i, -r => neriesit XXX
                   'tgi', # +r, +t, ~i
                   'micc', #
                   'aeis', # -i, +r, +/~ t => mensia pozicia 
                   'cvg', # ~/-i, +t, +r
                   'px', # ~/+ i, +r, +t
                   'var', # +t, 0i, 0r -> t gamble
                  ],
}

#XXX premenovat, testujem len stocky s vysokym short ratiom
long_after = { 
    '2006-10-18': ['plxt', 'mogn', 'bcr'],
    '2006-10-19': ['vign'],
    '2006-10-23': ['slab', # dobry reakcie, slusny SI, mozny nastup po open
                   'inin',
                   #'vprt', # +r, +targets, ~/+ si, nemal som dovod verit ze
                            # pojde up
                   #'mtxx', # nemal kam rast neskor, nenastupit
                  ],
    '2006-10-24': ['acf',
                   'bwld', # dalo sa nastupit?
                   #'chb', # neiste zverejnenie, radsej neriesit
                   'supx',
                   #'cake', nezverejnil, delinquent IIRC
                   'plt', # bottomfishing
                  ],
    '2006-10-25': [#'amed', # moc narastena, nezverejnil dobre na nastup
                   #'acat', # neriesit, ~ zverejnenie
                   'eeft',
                   #'lifc', # moc narastena, obratit na short po
                   'pfcb',
                   'affx',
                   'eq', 
                   #'lfg', # neriesit, moc narastena
                   'netl', # => short after
                   #'osi', # nedalo sa nastupit
                   'pnsn',
                   'psys', # nenastupovat, ~ zverejnenie
                   'rnow',
                   #'abax', # nenastupovat, zle zverejnenie
                   'amg',
                   #'fbn', # neriesit, ~zverejnenie
                   'imcl',
                   #'ilse', # neriesit, ~zverejnenie
                   #'loop', # malo historie
                   'nvt', # bottomfishing
                   'res',
                   'tasr', 
                  ],
}

short_before = {
    '2006-10-23': ['slab', # ~/+ t, -r, ~i => mala pozicia
                   'f/s', # mierne bullish i a t trend
                   'mdu/s', # + reakcie, + history, + targets -> neshortovat
                   'dst', # ~r, -i, 0 t => insiders gamble => mala pozicia
                   'fdc', # +r, ~/+ i, -t => neriesit / mala pozicia
                   'wcn', # ~r, ~t, ~/-i -> mala pozicia
                   'yanb', # -r, -t, +i -> mala pozicia, ak vobec
                  ],
    '2006-10-24': ['glg', # mensia pozicia
                   'lpx',
                   #'bwld', # +/~ t, ~r, ~ i, +si => neriesit
                   #'amzn', # ~ t, ~r, + i, +si => neriesit
                   'ten',
                   'pd',
                   #'clzr', # ~/+t, ~i, -r skor na bottomfishing
                   'lss', # krasa
                   # 'dv', # + t, -r, ~/+ i 
                   'efii',
                  ],
    '2006-10-25': ['frc', 
                   #'pfcb', # moc bullish signalov (rev)
                   'rsh',
                   #'affx', # no bottomfishing
                   #'esst', # no bottomfishing
                   #'har', # +t +i => neriesit
                   #'hlit', # toto je skor na longa vpred
                   'nabi',
                   'phm', 
                   'smbi', 
                   #'uspi', # slabe dovody
                   #'nfx', # ziaden dovod  / moc neiste
                   'rnt', 
                   #'mtsn', # bullish rev -> ziaden dovod
                   #'nvt', # bottomfishing!, zopar bullish rev => ziaden dovod
                   'rgs', # krasa
                   #'see', # zopar bullish rev, ziaden dovod
                  ]
}

short_after = {
    '2006-10-18': ['jef', 'et'], 
    '2006-10-18': ['dltk'], 
    '2006-10-24': [ 'fisv', # neriesit, dobre zverejnil
                  ],
    '2006-10-25': ['prxl', 
                   'lifc', # sledovat na long po
                   'netl',
                  ],
    '2006-11-09': ['gigm', 'rsti'],
    '2006-11-14': ['bwtr'],
    '2006-10-16': ['lab'],
    '2006-11-20': ['dy'],
    '2006-11-30': ['conn'],
    '2006-12-04': ['cqnr'],
    '2006-12-06': ['ncs'],
    '2006-12-07': ['cent'],
    '2006-12-14': ['becn'],
    }

targets = { 'juggler': juggler,
            'reactions' : reactions,
            'paper': paper,
            'quality': quality,
            'long_before': long_before,
            'long_after': long_after,
            'short_before': short_before,
            'short_after': short_after,
            'reactions_short': reactions_short,
            'run_eh' : reactions_run_in_EH,
            'wait_eh' : reactions_wait_in_EH,
            'short_outlook_good' : short_outlook_good,
            'short_outlook_neriesit' : short_outlook_neriesit,
            'short_outlook_bad' : short_outlook_bad,
            'short_overbought_good': short_overbought_good, 
            'short_overbought_bad': short_overbought_bad, 
            'short_overbought_neriesit': short_overbought_neriesit, 
          } 

if __name__ == '__main__':
    parser = util.from_to_parser()
    parser.add_option('-c', '--cmd', default='python ./tools/summary.py')
    parser.add_option('-o', '--output_dir', default='/tmp')
    opts, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide a target: %s' % targets.keys())
    else:
        target = args[0]
        assert target in targets, target

    cmd = "rm -rfv %s/%s; %s %s/%s" % (opts.output_dir, target,
                                       opts.cmd,
                                       opts.output_dir, target)
    do_print = False
    total = 0
    for date in reversed(sorted(targets[target])):
        symbols = targets[target][date]
        date = util.Date(date)
        if opts.begin_date and date < opts.begin_date:
            continue
        if opts.end_date and date > opts.begin_date:
            continue
        symbols = map(lambda x: x.split('/')[0], symbols)
        if symbols:
            total += len(symbols)
            symbols = " ".join(map(lambda x: "%s:%s" % (x, date.date_str()), symbols))
            cmd = "%s %s" % (cmd, symbols)
            do_print = True
    if do_print: 
        print "# %d symbols" % total
        print cmd
    else:
        print '# nothing to do'
