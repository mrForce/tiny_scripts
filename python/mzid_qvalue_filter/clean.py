import argparse
import csv

parser = argparse.ArgumentParser(description='Remove DefaultDirection row, and join Proteins column')

parser.add_argument('input', help='input PIN file')
parser.add_argument('output', help='Output file')
args = parser.parse_args()
with open(args.input, 'r') as f:
    reader = csv.DictReader(f, restkey='Proteins', delimiter = '\t')
    new_rows = []
    for row in reader:
        if row['SpecId'] != 'DefaultDirection':
            if isinstance(row['Proteins'], list):
                temp = row['Proteins'].join(',')
                row['Proteins'] = temp
            new_rows.append(row)
    with open(args.output, 'w') as g:
        writer = csv.DictWriter(g, delimiter='\t')
        writer.writeheader()
        for row in new_rows:
            writer.writerow(row)
