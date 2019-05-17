import argparse
import csv
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

def get_peptides(dict_reader, peptide_column, qval_column = None, qval_cutoff = None):
    peptides = set()
    for row in dict_reader:
        peptide = row[peptide_column]
        if qval_column and qval_cutoff:
            if float(dict_reader[qval_column]) <= qval_cutoff:
                peptides.add(peptide)
        else:
            peptides.add(peptide)
    return peptides


parser = argparse.ArgumentParser(description='Create a Venn Diagram of the overlap in peptides between TSV files. Provide a Q-value cutoff.')
parser.add_argument('fileOne', help='First TSV file')
parser.add_argument('fileTwo', help='Second TSV file')
parser.add_argument('peptideColumn', help='Peptide column')
parser.add_argument('--qval', nargs=2, help='Q-value column followed by Q-value cutoff. Optional.')

args = parser.parse_args()
qval_column = None
qval_cutoff = None
print('first file: %s, second file: %s, peptide column: %s'% (args.fileOne, args.fileTwo, args.peptideColumn))
if args.qval:
    print('Q-value column: %s, Q-value cutoff: %f' % (args.qval[0], float(args.qval[1])))
    qval_column = args.qval[0]
    qval_cutoff = float(args.qval[1])
file_one = open(args.fileOne, 'r')
file_one_reader = csv.DictReader(file_one, delimiter='\t')
file_one_peptides = get_peptides(file_one_reader, args.peptideColumn, qval_column, qval_cutoff)
file_one.close()
file_two = open(args.fileTwo, 'r')
file_two_reader = csv.DictReader(file_two, delimiter='\t')
file_two_peptides = get_peptides(file_two_reader, args.peptideColumn, qval_column, qval_cutoff)
file_two.close()
venn2(subsets = (len(file_one_peptides), len(file_two_peptides), len(file_one_peptides.intersection(file_two_peptides))), set_labels = ('Replicate 1', 'Replicate 2'))
plt.show()
