import csv
import glob
import os
import sys
import subprocess
from decimal import *
CRITERIA_ROW = 0
VALUE_ROW = 1
COMMENT_COLUMN = -1
TOTAL_COLUMN = -2
NETID_COLUMN=0
FIRST_COLUMN=1
LAST_COLUMN=-3
START_ROW=2

GIT_PUSH = True
COMMIT_MESSAGE = 'Exam II Q4 comments'
scores = '/home/jforce/Documents/comments/exam_II_q4.txt'
students_path = '/home/jforce/gitolite-admin/bin2018f/cse3100f18.{NETID}/exam2/q4.txt'




with open(scores, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    fieldnames = reader.fieldnames
    if LAST_COLUMN + 1 == 0:
        fields_to_show = fieldnames[FIRST_COLUMN::]
    else:
        fields_to_show = fieldnames[FIRST_COLUMN:(LAST_COLUMN + 1)]
    points_row = reader.__next__()
    netid_fieldname = fieldnames[NETID_COLUMN]
    comment_fieldname = fieldnames[COMMENT_COLUMN]
    total_fieldname = fieldnames[TOTAL_COLUMN]
    for row in reader:
        netid = row['NetID']
        path = students_path.replace('{NETID}', netid)
        comment = row[comment_fieldname]
        total = row[total_fieldname]
        if os.path.exists(os.path.dirname(path)):
            with open(path, 'w') as g:
                g.write('NetID: ' + netid + '\n')
                g.write('Comment: ' + comment + '\n')
                g.write('Points: ' + total + ' out of ' + points_row[total_fieldname] + '\n')
                g.write('\n\nPoints breakdown: \n\n\n')
                total_points = Decimal('0')
                for field in fields_to_show:
                    field_value = Decimal(row[field]) if len(row[field]) > 0 else 0
                    num_points = field_value*Decimal(points_row[field])
                    total_points += num_points
                    a = float(str(num_points))
                    g.write(field + ': ' + str(num_points) + ' out of: ' + points_row[field] + '\n')
                assert(Decimal(total) == total_points)
            subprocess.run(['git', 'add', os.path.basename(path)], cwd = os.path.dirname(path))
            subprocess.run(['git', 'commit', '-m', COMMIT_MESSAGE], cwd = os.path.dirname(path))
            if GIT_PUSH:
                subprocess.run(['git', 'push'], cwd=os.path.dirname(path))

