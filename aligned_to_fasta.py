import sys

if len(sys.argv) == 2:
    with open(sys.argv[1], 'r') as f:
        i = 1;
        for x in f:
            print('> {0}'.format(i))
            print(x.strip())
            i += 1
