import argparse
import csv
import pyteomics.mgf as mgf
parser = argparse.ArgumentParser()
parser.add_argument('run_one_mgf', help='MGF file path for run 1')
parser.add_argument('run_two_mgf', help='MGF file path for run 2')
parser.add_argument('run_one_percolator', help='Location of percolator.target.peptides.txt file for first run')
parser.add_argument('run_two_percolator', help='Location of percolator.target.peptides.txt file for second run')
parser.add_argument('fdr', help='FDR Cutoff to use')
parser.add_argument('output', help='Output file')

args = parser.parse_args()

def get_rt(file_location):
    #returns a dictionary mapping each scan to the RT
    retention_times = {}
    with open(file_location, 'r') as f:
        reader = mgf.MGF(f)
        for spec in reader:
            rt = spec['params']['rtinseconds']
            scan = spec['params']['scans']
            assert(scan not in retention_times)
            retention_times[scan] = rt
    return retention_times

def get_peptides(file_location, fdr):
    #map each peptide to its scan number.
    peptides = {}
    with open(file_location, 'r') as f:
        tsv_reader = csv.DictReader(f, delimiter='\t')
        for row in tsv_reader:
            q_value = row['percolator q-value']
            if float(q_value) <= fdr:
                scan = row['scan']
                peptide = row['sequence']
                assert(peptide not in peptides)
                peptides[peptide] = scan
    return peptides

fdr = float(args.fdr)
run_one_peptides = get_peptides(args.run_one_percolator, fdr)
run_two_peptides = get_peptides(args.run_two_percolator, fdr)
run_one_rts = get_rt(args.run_one_mgf)
run_two_rts = get_rt(args.run_two_mgf)
shared_peptides = run_one_peptides.keys() & run_two_peptides.keys()
rows = []
for peptide in shared_peptides:
    run_one_scan = run_one_peptides[peptide]
    run_two_scan = run_two_peptides[peptide]
    run_one_rt = run_one_rts[run_one_scan]
    run_two_rt = run_two_rts[run_two_scan]
    rows.append({'peptide': peptide, 'run_one_scan': run_one_scan, 'run_two_scan': run_two_scan, 'run_one_rt': run_one_rt, 'run_two_rt': run_two_rt})

with open(args.output, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['peptide', 'run_one_scan', 'run_two_scan', 'run_one_rt', 'run_two_rt'], delimiter='\t')
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    

