import argparse
from pyteomics import mgf
import sys
import bisect
import random
import csv
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio import SeqIO
import math
from Bio.Alphabet import IUPAC
import progressbar
import networkx as nx

def compute_chromatic(masses, window):
    G = nx.Graph()
    for i in range(0, len(masses)):
        G.add_node(i)
    for i in range(0, len(masses)):
        for j in range(i + 1, len(masses)):
            if abs(masses[j] - masses[i]) <= window*2.0:
                G.add_edge(i, j)
            else:
                break
    assert(nx.is_chordal(G))
    setlist = nx.chordal_graph_cliques(G)
    return max([len(x) for x in setlist])
    
    

def get_window(mass, window):
    return (mass - window, mass + window)
    #return (mass/(1. + window/10**6), mass/(1.0 - window/10**6))

def get_mass_indices(masses, min_mass, max_mass):
    """
    This gives you the indices of peptides within the mass range.
    min_mass is a floating point
    max_mass is a floating point.
    """    
    min_index = bisect.bisect_left(masses, min_mass)
    max_index = bisect.bisect_right(masses, max_mass)
    return (min_index, max_index)



parser = argparse.ArgumentParser(description='Given a set of spectra, and a list of peptides, pair each spectra with a randomly selected peptide within the mass range.')
parser.add_argument('spectra', help='MGF format')
parser.add_argument('peptides')
#parser.add_argument('spectra_pairing', help='File to save the spectra-peptide pairing in. Will be a CSV file with two fields: spectra and peptide')
parser.add_argument('output_peptides', help='File to save the selected peptides. Will be in FASTA format')

args = parser.parse_args()


spectra_reader = mgf.read(args.spectra)
#map the spectra scan to mass.
spectra = {}

print('reading spectra')
i = 1

proton_mass = 1.00727646677
for x in spectra_reader:
    params = x['params']
    scan = None
    if 'scans' in params:
        scan = params['scans']
    else:
        #scan = params['title']
        scan = str(i)
    assert(scan not in spectra)
    assert('pepmass' in params)
    assert('charge' in params)
    #This is confusing: apparently the PEPMASS field is m/z of precursor, so we should multiply by the charge to get the precursor mass.
    mass_to_charge = params['pepmass'][0]
    assert(len(params['charge']) == 1)
    charge = params['charge'][0]
    
    mass = (mass_to_charge - proton_mass)*charge
    assert(scan not in spectra)
    spectra[scan] = mass
    i += 1
    
peptides_with_mass = {}

print('reading peptides')
with open(args.peptides, 'r') as f:
    for line in f:
        line = line.strip()
        if len(line) > 0:
            parts = line.split()
            assert(len(parts) == 2)
            peptide = parts[0]
            mass = float(parts[1])
            peptides_with_mass[peptide] = mass

peptide_mass_list = list(peptides_with_mass.items())
peptide_mass_list.sort(key=lambda x: x[1])

peptides = [x[0] for x in peptide_mass_list]
masses = [x[1] for x in peptide_mass_list]
#default is a window of +- 3 Da
window = 3.0
psms = []
peptide_to_spectra = {}
print('going to match spectra to peptide')
bar = progressbar.ProgressBar(max_value=len(spectra.items()))
i = 0
j = 0
for scan, mass in spectra.items():
    min_mass, max_mass = get_window(mass, window)
    if min_mass <= masses[-1] or max_mass >= masses[0]:
        min_index, max_index = get_mass_indices(masses, min_mass, max_mass)
        if min_index < max_index:
            print('Num choices for spectrum %s is %d' % (str(scan), max_index - min_index))
            j += 1
            #exclusive on the end, as it should be
            index = random.randrange(min_index, max_index)
            peptide = peptides[index]
            #psms.append({'scan': scan, 'scanMass': mass, 'peptide': peptide, 'peptideMass': masses[index]})
            if peptide in peptide_to_spectra:
                peptide_to_spectra[peptide]['scans'].append({'scan': scan, 'scanMass': mass})
            else:
                peptide_to_spectra[peptide] = {'scans': [{'scan': scan, 'scanMass': mass}], 'peptideMass': masses[index]}
    i += 1
    bar.update(i)
print('scans with a matching peptide: %d, out of %d scans' % (j, i))
#print('chromatic number: %d' % compute_chromatic(sorted(spectra.values()), window))
"""
with open(args.spectra_pairing, 'w') as f:
    writer = csv.DictWriter(f, fieldnames= ['scan', 'scanMass', 'peptide', 'peptideMass'], delimiter='\t')
    writer.writeheader()
    for psm in psms:
        writer.writerow(psm)
"""
peptide_records = []
i = 1
for peptide, value in peptide_to_spectra.items():
    description = 'peptide mass: %f, ' % value['peptideMass'] + ', '.join(['scan %s, mass %f' % (str(x['scan']), x['scanMass']) for x in value['scans']])
    record = SeqRecord(Seq(peptide, IUPAC.protein), id = str(i), description = description)
    peptide_records.append(record)
    i += 1
        
with open(args.output_peptides, 'w') as output_handle:
    SeqIO.write(peptide_records, output_handle, 'fasta')
