import csv
import glob
import os
import subprocess
GIT_COMMIT = True
COMMIT_MESSAGE = 'lab6comments'
scores = '/home/jforce/Documents/comments/lab6.tsv'
students_path = '/home/jforce/gitolite-admin/bin2018f/cse3100f18.{NETID}/lab6/lab6.txt'
with open(scores, 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    out_of = reader.__next__()[0]
    for line in reader:
        netid = line[0]
        comment = line[-1]
        score = line[-2]
        path = students_path.replace('{NETID}', netid)
        with open(path, 'w') as g:
            g.write(comment + '\n')
            g.write('score: %s out of %s' % (score, out_of))
        if GIT_COMMIT:
            subprocess.run(['git', 'add', os.path.basename(path)], cwd = os.path.dirname(path))        
            subprocess.run(['git', 'commit', '-m', COMMIT_MESSAGE], cwd = os.path.dirname(path))
            subprocess.run(['git', 'push'], cwd=os.path.dirname(path))

