import argparse
import csv



def length_filter(peptides, min_length = None, max_length = None):
    if min_length:
        peptides = [x for x in peptides if len(x) >= min_length]
    if max_length:
        peptides = [x for x in peptides if len(x) <= max_length]
    return peptides

def get_peptides(dict_reader, peptide_column):
    peptides = set()
    for row in dict_reader:
        peptide = row[peptide_column]
        peptides.add(peptide.upper())
    return peptides


parser = argparse.ArgumentParser(description='Create a Venn Diagram of the overlap in peptides between TSV files. Provide a Q-value cutoff.')
parser.add_argument('fileOne', help='First TSV file')
parser.add_argument('fileTwo', help='Second TSV file')
parser.add_argument('peptideColumn', help='Peptide column')
parser.add_argument('--minLength', help='Minimum peptide length', type=int)
parser.add_argument('--maxLength', help='Maximum peptide length', type=int)
args = parser.parse_args()
print('first file: %s, second file: %s, peptide column: %s'% (args.fileOne, args.fileTwo, args.peptideColumn))
print('min length: ' +  str(args.minLength))
print('max length: ' + str(args.maxLength))
file_one = open(args.fileOne, 'r')
file_one_reader = csv.DictReader(file_one, delimiter='\t')
file_one_peptides = get_peptides(file_one_reader, args.peptideColumn)
print('file one non-alphabetic peptides: ')
for x in file_one_peptides:
    if not x.isalpha():
        print(x)

file_one.close()
file_two = open(args.fileTwo, 'r')
file_two_reader = csv.DictReader(file_two, delimiter='\t')
file_two_peptides = get_peptides(file_two_reader, args.peptideColumn)
print('file two non-alphabetic peptides: ')
for x in file_two_peptides:
    if not x.isalpha():
        print(x)
file_two.close()

file_one_length_filtered_peptides = set(length_filter(list(file_one_peptides), args.minLength, args.maxLength))
file_two_length_filtered_peptides = set(length_filter(list(file_two_peptides), args.minLength, args.maxLength))

overlap = file_one_length_filtered_peptides.intersection(file_two_length_filtered_peptides)
print('# peptides in file one: ' + str(len(file_one_peptides)))
print('# peptides in file two: ' + str(len(file_two_peptides)))
print('# length filtered peptides in file one: ' + str(len(file_one_length_filtered_peptides)))
print('# length filtered peptides in file two: ' + str(len(file_two_length_filtered_peptides)))
print('intersection: ' + str(len(overlap)))

