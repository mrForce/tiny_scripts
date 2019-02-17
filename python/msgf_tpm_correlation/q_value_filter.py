"""
The point of this script is parse an MZIdentML file from MSGF+, extract the Uniprot ID from the FASTA headers (specified by "accession"). 

Then, convert the Uniprot ID to either Gene name, or RefSeq (depending on what the user specifies), and get the TPM for that gene.

"""
import numpy
import collections
import math
from pyteomics import mzid
import argparse
import matplotlib.pyplot as plt
import statistics
import sys
from scipy.cluster.vq import vq, kmeans, whiten
from scipy import stats
import csv
import re
import subprocess

def write_fasta(output_location, sequences):
    with open(output_location, 'w') as f:
        i = 0
        for x in list(sequences):
            f.write('>%d\n' % i)
            f.write(x + '\n')
            i += 1


ptm_removal_regex = re.compile('\[[^\]]*\]')

def clean_peptide(seq):
    return ptm_removal_regex.sub('', seq).replace('.', '').strip()
parser = argparse.ArgumentParser(description='correlate the max MSGF+ score for the peptides with their TPM value')
parser.add_argument('mzid_file')
parser.add_argument('pin_file')
args = parser.parse_args()


mzid_parser = mzid.DataFrame(args.mzid_file)




q_value_threshold = 0.01

initial_peptides = set()

all_peptides = set()
#Note: DO NOT USE itertuples HERE! Unfortunately, namedtuple takes MS-GF:RawScore and converts it to a positional parameter.
for i, row in mzid_parser.iterrows():
    spectrum_id = row['spectrumID'].split('=')[1]
    if float(row['MS-GF:PepQValue']) <= q_value_threshold:
        initial_peptides.add(row['PeptideSequence'])

with open(args.pin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    next(reader)
    for row in reader:
        scan_number = int(row['ScanNr'])
        peptide = clean_peptide(row['Peptide'])
        all_peptides.add(peptide)

    
peptides_list = list(all_peptides)
initial_peptide_fasta = input('Where to put FASTA containing initial peptides? ')
all_peptides_fasta  = input('Where to put FASTA containing all peptides? ')

write_fasta(initial_peptide_fasta, initial_peptides)
write_fasta(all_peptides_fasta, peptides_list)

alignment_location = input('Where to put alignment? ')
subprocess.call(['clustalo', '-i', initial_peptide_fasta, '-o', alignment_location, '--force'])
hmm_location = input('Where to put HMM? ')
subprocess.call(['hmmbuild', hmm_location, alignment_location])
subprocess.call(['hmmpress', hmm_location])
table_output = input('Enter table output location: ')
subprocess.call(['hmmscan', '--max', '--incT', '0', '--tblout', table_output, hmm_location, all_peptides_fasta])
#input('wrote FASTA of initial peptides. Please run hmmbuild on this, then hmmpress on the hmm file. Press enter when done')
#input('Now run the following, replacing <table output> and <hmm location>: hmmscan --max --incT 0 --tblout <table output>  <hmm location>  %s. Press enter. ' % all_peptides_fasta)

peptides_to_hmmer_score = {}
with open(table_output, 'r') as f:
    for line in f:
        line = line.strip()
        if line[0] != '#':
            line_parts = line.split()
            fasta_header = int(line_parts[2])
            score = float(line_parts[5])
            peptide = clean_peptide(peptides_list[fasta_header])
            peptides_to_hmmer_score[peptide] = score

pin_output = input('Enter pin output: ')
            
with open(args.pin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    fieldnames = list(reader.fieldnames)
    fieldnames.insert(6, 'HMMERScore')
    with open(pin_output, 'w') as g:        
        writer = csv.DictWriter(g, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        next(reader)
        for row in reader:
            peptide = clean_peptide(row['Peptide'])
            row_copy = dict(row)
            row_copy['HMMERScore'] = peptides_to_hmmer_score[peptide]
            writer.writerow(row_copy)
            
