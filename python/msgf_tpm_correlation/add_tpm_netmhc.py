"""
The point of this script is parse an MZIdentML file from MSGF+, extract the Uniprot ID from the FASTA headers (specified by "accession"). 

Then, convert the Uniprot ID to either Gene name, or RefSeq (depending on what the user specifies), and get the TPM for that gene. Then, add the TPM to the PIN file. Also, extract the NetMHC affinity from the FASTA headers.

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

"""
Returns a dictionary like this: {'allele': (affinity, rank)...}
"""
def extract_netmhc_scores(header):
    affinity_dict = dict()
    rank_dict = dict()
    rank_regex = re.compile('netmhc_(?P<allele>.*?)_rank=(?P<rank>\d+\.\d+)')
    affinity_regex = re.compile('netmhc_(?P<allele>.*?)_affinity=(?P<affinity>\d+\.\d+)')
    for x in rank_regex.finditer(header):
        allele = x['allele']
        assert(allele not in rank_dict)
        rank = float(x['rank'])
        rank_dict[allele] = rank

    for x in affinity_regex.finditer(header):
        allele = x['allele']
        assert(allele not in affinity_dict)
        affinity = float(x['affinity'])
        affinity_dict[allele] = affinity
    assert(affinity_dict.keys() == rank_dict.keys())
    return {allele: (affinity_dict[allele], rank_dict[allele]) for allele in affinity_dict.keys()}

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
parser = argparse.ArgumentParser(description='Add TPM values and NetMHC affinity to the output')
parser.add_argument('mzid_file')
parser.add_argument('pin_file')
args = parser.parse_args()


mzid_parser = mzid.DataFrame(args.mzid_file)




for i, row in mzid_parser.iterrows():
    for i, row in mzid_parser.iterrows():
        accession = row['accession']
    if len(accession) == 1 and not row['isDecoy'] and 'MS-GF:RawScore' in row:
        


with open(args.pin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    next(reader)
    for row in reader:
        scan_number = int(row['ScanNr'])
        peptide = clean_peptide(row['Peptide'])
        all_peptides.add(peptide)

    
peptides_list = list(all_peptides)



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
            
