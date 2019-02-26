"""
The point of this script is parse an MZIdentML file from MSGF+, extract the Uniprot ID from the FASTA headers (specified by "accession"). 

Then, convert the Uniprot ID to either Gene name, or RefSeq (depending on what the user specifies), and get the TPM for that gene. Then, add the TPM to the PIN file. Also, extract the NetMHC affinity from the FASTA headers.

"""
import numpy
import random
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
import tempfile
NETMHC_LOCATION='/home/jforce/Downloads/netMHC-4.0/Linux_x86_64/bin/netMHC'
def parse_tpm(path):
    tpm_data = {}
    with open(path, 'r') as handler:
        for line in handler:
            parts = line.split('\t')
            if len(parts) == 4:
                tpm_data[parts[0]] = float(parts[1])
    return tpm_data


#https://www.uniprot.org/help/api_idmapping
def parse_uniprot_mapper(path, id_type):
    mapper = collections.defaultdict(list)
    with open(path, 'r') as handler:
        for line in handler:
            parts = line.split('\t')
            uniprot_id = parts[0].strip()
            record_type = parts[1].strip()
            value = parts[2].strip()
            if record_type == id_type:
                mapper[uniprot_id].append(value)
    return mapper


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
parser.add_argument('tpm_file')
parser.add_argument('uniprot_file')
parser.add_argument('identifier', choices=['RefSeq', 'RefSeq_NT', 'Gene_Name'])
args = parser.parse_args()

uniprot_data = parse_uniprot_mapper(args.uniprot_file, args.identifier)
tpm_data = parse_tpm(args.tpm_file)
"""
Returns a dictionary mapping the peptide to its affinity
"""
def call_netmhc(peptides, hla):
    file = open('netmhc_input.txt', 'w')
    output_location = 'netmhc_output.txt'
    for x in peptides:
        x.write(x.strip('.-') + '\n')
    command = [NETMHC_LOCATION, '-a', hla, '-f', 'netmhc_input.txt', '-p', '>', output_location]
    subprocess.call(command, shell=True)
    file.close()
    regex = re.compile('^(\s+[^\s]+){2}(\s+(?P<peptide>[A-Z]+))(\s+[^\s]+){10}(\s+(?P<rank>[0-9]{1,2}\.[0-9]+))')
    results = {}
    with open(output_location, 'r') as f:
        for line in f:
            match = regex.match(line)
            if match:
                peptide = match.group('peptide')
                affinity = float(match.group(affinity))
                results[peptide] = affinity
            else:
                print('Could not match line: %s' % line)
    return results

mzid_parser = mzid.DataFrame(args.mzid_file)

netmhc_alleles = ['H-2-Kb']

"""
First, extract the targets and decoys from the PIN file. 
"""
target_peptides = set()
decoy_peptides = set()

with open(args.pin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    next(reader)
    for row in reader:
        label = row['Label'].strip()
        peptide = clean_peptide(row['Peptide'])
        if label == '1':
            target_peptides.add(peptide)
        elif label == '-1':
            decoy_peptides.add(peptide)
        else:
            assert(label == '-')

"""
Call NetMHC on the decoys
"""

decoy_affinity = {}
for allele in netmhc_alleles:
    decoy_affinity[allele] = call_netmhc(decoy_peptides, allele)


target_affinity = {}
target_tpm = {}

"""
Extract the TPM values and NetMHC affinity from the targets
"""


for i, row in mzid_parser.iterrows():
    accession = row['accession']
    if len(accession) == 1 and not row['isDecoy'] and 'MS-GF:RawScore' in row:
        """
        The *actual* accessions are seperated via @@. 
        """
        accessions = accession[0].split('@@')
        assert(accessions)
        tpm = 0
        for acc in accessions:
            uniprot_id = acc.split('|')[1]
            tpm_id_list = uniprot_data[uniprot_id]
            if len(tpm_id_list) == 0:
                tpm += 1
            elif len(tpm_id_list) == 1:
                tpm_id = tpm_id_list[0]
                if tpm_id in tpm_data:
                    tpm += max(1, tpm_data[tpm_id])
                else:
                    tpm += 1
            else:
                print('more than two tpm ids')
                print(tpm_id_list)
                assert(False)
        netmhc_scores = extract_netmhc_scores(accession[0])
        peptide = row['PeptideSequence']
        for allele,scores in netmhc_scores:
            affinity = float(scores[0])
            if peptide in target_affinity[allele]:
                assert(target_affinity[allele][peptide] == affinity)
            else:
                target_affinity[allele][peptide] = affinity
        
#randomly sample from this to assign NetMHC values to decoys
tpms = list(target_tpm.values())        


"""
Now go through PIN file, and insert the TPM and affinity
"""
pin_output = input('Enter pin output: ')
            
with open(args.pin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t', restkey='Proteins')
    fieldnames = list(reader.fieldnames)
    fieldnames.insert(6, 'TPM')
    for allele in netmhc_alleles:
        fieldnames.insert(7, allele)
    with open(pin_output, 'w') as g:        
        writer = csv.DictWriter(g, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        next(reader)
        for row in reader:
            peptide = clean_peptide(row['Peptide'])
            label = row['Label']
            row_copy = dict(row)
            if label == '1':
                #target                                
                assert(peptide in target_tpm)
                row_copy['TPM'] = target_tpm[peptide]
                for allele in netmhc_alleles:
                    assert(peptide in target_affinity[allele])
                    row_copy[allele] = target_affinity[allele][peptide]
            elif label == '-1':
                #decoy, for TPM, just sample randomly
                row_copy['TPM'] = random.choice(tpms)
                for allele in netmhc_alleles:
                    assert(peptide in decoy_affinity[allele])
                    row_copy[allele] = decoy_affinity[allele][peptide]
            writer.writerow(row_copy)
            
