#!/usr/bin/python3
#-----------------------------------------------------------------------
# File    : chkarm.py
# Contents: examples how to use the arules function of the fim module
# Author  : Christian Borgelt
# History : 2014.09.19 file created
#           2014.10.02 test of python functions apriori/eclat/fpgrowth
#           2015.09.04 adapted to modified value report behavior
#-----------------------------------------------------------------------
from sys        import argv, stderr
from os         import remove, devnull
from subprocess import call, check_output
from time       import time
from random     import seed, random
from fim        import arules, apriori, eclat, fpgrowth

#-----------------------------------------------------------------------

def run_pipe (prog, null):
    res = []                    # traverse the program output
    out = str(check_output(prog +['-'],stderr=null))
    for line in out.split('\n')[:-1]:
        line = line.split()
        head = int(line[0])
        body = [int(x) for x in line[2:-2]]
        res.append((head, body, int(line[-2]), int(line[-1])))
    return res

#-----------------------------------------------------------------------

def run_file (prog, null):
    call(prog +['tmp.txt'], stderr=null)
    res = []
    with open('tmp.txt', 'rt') as inp:
        for line in inp:
            line = line.split()
            head = int(line[0])
            body = [int(x) for x in line[2:-2]]
            res.append((head, body, int(line[-2]), int(line[-1])))
    return res

#-----------------------------------------------------------------------

if __name__ == '__main__':
    runs   = int(argv[1]) if len(argv) > 1 else 1
    tracts = [[i+1 for i in range(100) if random() < 0.1]
                   for k in range(1000)]
    with open('data.txt', 'w') as out:
        for t in tracts:
            for i in t: out.write('%d ' % i)
            out.write('\n')

    if len(argv) > 2:
        rules  = arules(tracts, supp=-2, conf=80, zmin=2,
                        report='ab', appear={None:'in', 1:'out'})
        for r in rules: print(r)
        remove('data.txt'); exit()

    stderr.write('association rules:\n')
    stderr.write('arules ... '); t = time()
    for r in range(runs):
        rules = arules(tracts, supp=-2, conf=80, zmin=2, report='ab')
    stderr.write('done [%.3fs].\n' % (time()-t))
    rules = set([(h, tuple(sorted(list(b))), x, y)
                 for h,b,x,y in rules])
    stderr.write('\n')

    for p,f in [('apriori',  apriori),
                ('eclat',    eclat),
                ('fpgrowth', fpgrowth)]:
        stderr.write(p +' (rules)\n')
        stderr.write('python ... '); t = time()
        for r in range(runs):
            pyrules = f(tracts, target='r', supp=-2, conf=80,
                        zmin=2, report='ab')
        stderr.write('done [%.3fs].\n' % (time()-t))

        prg = [p, '-tr', '-s-2', '-c80', '-m2', '-v %a %b', 'data.txt']
        stderr.write('pipe   ... '); t = time()
        with open(devnull, 'w') as null:
            for r in range(runs):
                exrules = run_pipe(prg, null)
        stderr.write('done [%.3fs].\n' % (time()-t))

        stderr.write('file   ... '); t = time()
        with open(devnull, 'w') as null:
            for r in range(runs):
                exrules = run_file(prg, null)
        stderr.write('done [%.3fs].\n' % (time()-t))

        pyrules = set([(h, tuple(sorted(list(b))), x, y)
                       for h,b,x,y in pyrules])
        exrules = set([(h, tuple(sorted(list(b))), x, y)
                       for h,b,x,y in exrules])

        stderr.write('cmp ok\n' if pyrules == exrules else 'cmp fail\n')
        stderr.write('ref ok\n' if pyrules == rules   else 'ref fail\n')
        stderr.write('\n')

    remove('data.txt')
    remove('tmp.txt')
