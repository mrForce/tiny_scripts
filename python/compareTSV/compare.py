import argparse
import csv
import sys
parser = argparse.ArgumentParser(description='Compares TSV files where row of columns and rows can be permuted')
parser.add_argument('first')
parser.add_argument('second')

args = parser.parse_args()

first = open(args.first, 'r')
second = open(args.second, 'r')
firstReader = csv.DictReader(first, delimiter='\t')
secondReader = csv.DictReader(second, delimiter='\t')
if not set(firstReader.fieldnames) == set(secondReader.fieldnames):
    print('fieldnames do not match')
    print(firstReader.fieldnames)
    print(secondReader.fieldnames)
    sys.exit()

def sortDictList(dictList, keys):
    for key in reversed(keys):
        dictList.sort(key=lambda x: x[key])
keys = list(firstReader.fieldnames)
firstRows = []
secondRows = []
for x in firstReader:
    firstRows.append(dict(x))
for x in secondReader:
    secondRows.append(dict(x))
if len(firstRows) != len(secondRows):
    print('There are ' + str(len(firstRows)) + ' rows in the first TSV file')
    print('There are ' + str(len(secondRows)) + ' rows in the second TSV file')
    print('These are not equal.')
    sys.exit()
sortDictList(firstRows, keys)
sortDictList(secondRows, keys)
for i in range(0, len(firstRows)):
    if not firstRows[i] == secondRows[i]:
        print('Conflicting rows:')
        print(firstRows[i])
        print(secondRows[i])
        print('Files are not equal')
        sys.exit()
print('Files are equal')
