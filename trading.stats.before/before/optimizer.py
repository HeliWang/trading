from trading.stats.before import question
from trading import util

def load_file(filename):
    questions = []
    answers = []
    f = open(filename)
    for line in f.xreadlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('Questions: '):
            questions = line[11:].split(';')
        elif line.startswith('V '):
            symbol, data, _, payoff = line.split()[1:5]
            payoff = float(payoff)
            data = map(int, data.split(';'))
            answers.append((symbol, data, payoff))
    f.close()
    return questions, answers

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "%prog [options] <log.txt> <strategy>"
    parser = OptionParser(usage=usage)
    opts, args = parser.parse_args()

    if len(args) != 2:
        parser.error("please pass a logfile and a strategy")
    else:
        logfile, strategy = args
        assert strategy in question.Question.ValidStrategies

    result = {}
    questions, answers = load_file(logfile)

    for i1, q1 in enumerate(questions):
        for i2, q2 in enumerate(questions):
            if i1 == i2:
                continue
            if "%s:%s" % (q1, q2) in result:
                continue
            if "%s:%s" % (q2, q1) in result:
                continue
            data = []
            for a in answers:
                if a[1][i1] and a[1][i2]:
                    data.append(a[2])
            key = "%s:%s" % (q1, q2)
            if data:
                success = len(filter(lambda x: x>=0, data))
                success_rate = 0
                if success:
                    success_rate = float(success) / len(data) 
                result[key] = (len(data), 
                               success,
                               len(data) - success,
                               success_rate,
                               min(data), 
                               util.mean(data), util.median(data),
                               max(data)
                              )
    result = result.items()
    if strategy == 'gap_up':
        result.sort(lambda x, y: cmp(x[1][0], y[1][0]))
        result.sort(lambda x, y: cmp(x[1][3], y[1][3]))
    if strategy == 'gap_down':
        result.sort(lambda y, x: cmp(x[1][0], y[1][0]))
        result.sort(lambda y, x: cmp(x[1][3], y[1][3]))
    for k, v in result:
        v = list(v[:3]) + map(lambda x: "%.2f" % x, v[3:])
        v = " ".join(map(str, v))
        print "%s > %s" % (k, v)
