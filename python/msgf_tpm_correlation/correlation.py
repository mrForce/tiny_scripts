import collections
from pyteomics import mzid
import argparse

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
            uniprot_id = parts[0]
            record_type = parts[1]
            value = parts[2]
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

for row in mzid_parser:
    accession = mzid_parser['accession']
    if len(accession) == 1 and not mzid_parser['isDecoy']:
        uniprot_id = accession[0].split('|')[1]
        tpm_id_list = uniprot_data[uniprot_id]
        if len(tpm_id_list) == 1:
            tpm_id = tpm_id_list[0]
            if tpm_id in tpm_data and tpm_data[tpm_id] > 0.0:
                print('%f\t%f' % (tpm_data[tpm_id], row['MS-GF:RawScore']))

