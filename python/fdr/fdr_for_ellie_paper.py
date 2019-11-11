import argparse
import re
from enum import Enum
import csv
class CutoffType(Enum):
    Q_VALUE = 1
    FDR = 2
def fdr_cutoff(entries, cutoff, score_direction, cutoff_type):
    """
    entries should be a list of dictionaries, each of the form {'score':, 'label':, 'peptide':}

    label is -1 for decoy, 1 for target
    """
    #first, sort by score in descending order if score_direction is +, ascending order if score_direction is -

    assert(score_direction in ['+', '-'])
    assert(cutoff_type is CutoffType.Q_VALUE or cutoff_type is CutoffType.FDR)
    for i in range(0, len(entries)):
        entries[i]['index'] = i
    sorted_entries = []
    if score_direction == '+':
        sorted_entries = sorted(entries, key=lambda x: float(x['score']), reverse=True)
    elif score_direction == '-':
        sorted_entries = sorted(entries, key=lambda x: float(x['score']))
    assert(sorted_entries)
    #if a peptide has multiple entries, take the one with the best score
    peptides = []
    unique_peptide_entries = []
    for x in sorted_entries:        
        if x['peptide'] not in peptides:
            peptides.append(x['peptide'])
            unique_peptide_entries.append(x)
    num_targets = 0
    num_decoys = 0
    cutoff_index = -1
    for i in range(0, len(unique_peptide_entries)):
        entry = unique_peptide_entries[i]
        if entry['label'] == -1:
            num_decoys += 1
        elif entry['label'] == 1:
            num_targets += 1
        if num_targets == 0:
            fdr = 1.0
        else:
            fdr = 1.0*num_decoys/num_targets
        if cutoff_type is CutoffType.FDR and fdr >= cutoff:
            break
        if fdr < cutoff:
            cutoff_index = i
    if cutoff_index == -1:
        return []
    else:
        return [x['index']  for x in unique_peptide_entries[0:(cutoff_index + 1)] if x['label'] == 1]
    
def parse_peptide(peptide, peptide_regex, ptm_removal_regex):
    match = peptide_regex.match(peptide)
    if match and match.group('peptide'):
        matched_peptide = match.group('peptide')
        return ptm_removal_regex.sub('', matched_peptide)
    else:
        return None

peptide_regex = re.compile('^[A-Z\-]\.(?P<peptide>.*)\.[A-Z\-]$')
ptm_removal_regex = re.compile('\[[^\]]*\]')

parser = argparse.ArgumentParser(description='Given TSV file(s), a peptide column, score column, score direction, target/decoy column, FDR threshold, and output directory, apply the peptide level FDR threshold with slight variations. The first variant is whether or not to remove PTMs before removing peptide duplicates. The second variant is whether to use the first (FDR) or last threshold crossing (Q-value). Output files should be target rows from input TSV file(s) that pass the FDR/Q-value threshold')
parser.add_argument('peptide_column', description='Which column contains the peptide')
parser.add_argument('score_column', description='Which column contains the score')
parser.add_argument('score_direction', description='+ if a higher score is better, - if a lower score is better', choices=['+', '-'])
parser.add_argument('td_column', description='Column that indicates if the row is for a target match (is a 1), or a decoy match (is a -1)')
parser.add_argument('output_directory', description='Where to put the output files')
parser.add_argument('input_files', nargs=argparse.REMAINDER)

args = parser.parse_args()
for input_file in args.input_files:
    rows = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        reader.__next__()
        for row in reader:
            assert(args.peptide_column in row)
            assert(args.score_column in row)
            assert(args.td_column in row)
            assert(row[args.td_column] in ['1', '-1'])
            rows.append(row)

