"""
The point of this script is parse an MZIdentML file from MSGF+, extract the Uniprot ID from the FASTA headers (specified by "accession"). 

Then, convert the Uniprot ID to either Gene name, or RefSeq (depending on what the user specifies), and get the TPM for that gene.

"""

import collections
from pyteomics import mzid
import argparse
import matplotlib.pyplot as plt
import sys
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


parser = argparse.ArgumentParser(description='correlate the max MSGF+ score for the peptides with their TPM value')
parser.add_argument('mzid_file')
parser.add_argument('tpm_file')
parser.add_argument('uniprot_file')
parser.add_argument('identifier', choices=['RefSeq', 'RefSeq_NT', 'Gene_Name'])

args = parser.parse_args()

tpm_data = parse_tpm(args.tpm_file)

uniprot_data = parse_uniprot_mapper(args.uniprot_file, args.identifier)


mzid_parser = mzid.DataFrame(args.mzid_file)

peptides = collections.defaultdict(lambda: [-10000000, ''])




for row in mzid_parser.to_dict(orient='records'):
    accession = row['accession']
    if len(accession) == 1 and not row['isDecoy'] and 'MS-GF:RawScore' in row:
        uniprot_id = accession[0].split('|')[1]
        tpm_id_list = uniprot_data[uniprot_id]
        print('tpm id list')
        print(tpm_id_list)
        if len(tpm_id_list) == 1:
            tpm_id = tpm_id_list[0]
            if tpm_id in tpm_data and tpm_data[tpm_id] > 0.0:
                print('yay')
                if peptides[row['PeptideSequence']][0] < row['MS-GF:RawScore']:
                    peptides[row['PeptideSequence']][0] = row['MS-GF:RawScore']
                if len(peptides[row['PeptideSequence']][1]) == 0:
                    peptides[row['PeptideSequence']][1] = tpm_id



#for peptide, info in peptides.items():
#    print('%f\t%f' % (tpm_data[info[1]], info[0]))
tpms = []
scores = []
print('peptides')
print(peptides)
for peptide, info in peptides.items():
    tpms.append(tpm_data[info[1]])
    scores.append(info[0])

plt.plot(tpms, scores)
plt.show()
