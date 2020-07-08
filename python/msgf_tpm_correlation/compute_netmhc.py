"""
This is similar to the add_netmhc.py script, but rather than inserting the score into a PIN file, we take a list of peptides, call NetMHC, and add the scores, but also report the best score.

"""
import argparse
import sys
import csv
import re
import subprocess

NETMHC_LOCATION='/home/jforce/Downloads/netMHC-4.0a.Linux/netMHC-4.0/netMHC'





ptm_removal_regex = re.compile('\[[^\]]*\]')
def parse_peptide(peptide, ptm_removal_regex):
    return ptm_removal_regex.sub('', peptide)
parser = argparse.ArgumentParser(description='Take a list of peptides, and add the NetMHC scores. ')
parser.add_argument('txt_input')
parser.add_argument('tsv_output')
parser.add_argument('alleles', nargs='+')

args = parser.parse_args()


"""
Returns a dictionary mapping the peptide to its affinity
"""
def call_netmhc(peptides, hla):
    f = open('netmhc_input.txt', 'w')
    output_location = 'netmhc_output.txt'
    for x in peptides:
        f.write(x + '\n')
    f.close()
    command = [NETMHC_LOCATION, '-a', hla, '-f', 'netmhc_input.txt', '-p', '-xls', '-xlsfile', output_location]
    print('command: ' + ' '.join(command))
    subprocess.call(command)
    results = {}
    with open(output_location, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        reader.__next__()
        second_row = reader.__next__()
        assert(second_row[1] == 'Peptide')
        assert(second_row[3] == 'nM')
        for row in reader:
            peptide = row[1]
            affinity = row[3]
            if len(peptide.strip()) > 0:
                x = float(affinity)
                results[peptide.strip()] = affinity

    return results


netmhc_alleles = args.alleles


"""
First, extract the peptides from the PIN file
"""
peptides = set()

with open(args.txt_input, 'r') as f:
    for line in f:
        if len(line.strip()) > 0:
            peptide = parse_peptide(line.strip(), ptm_removal_regex)
            print('line')
            print(line)
            assert(peptide)
            peptides.add(peptide)

peptide_affinity = {}
for allele in netmhc_alleles:
    peptide_affinity[allele] = call_netmhc(peptides, allele)

fields = ['peptide'] + netmhc_alleles + ['best']


with open(args.tsv_output, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t')
    writer.writeheader()
    for peptide in list(peptides):
        row = {'peptide': peptide}
        best_score = -1
        for allele in netmhc_alleles:
            row[allele] = str(peptide_affinity[allele][peptide])
            score = float(peptide_affinity[allele][peptide])
            if best_score == -1:
                best_score = score
            elif score < best_score:
                best_score = score
        row['best'] = str(best_score)
        writer.writerow(row)
