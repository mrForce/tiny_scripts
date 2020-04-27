import argparse
import csv
import sys
from pyteomics import mgf
import numpy as np
import matplotlib.pyplot as plt
import collections
import os
from scipy import stats
import math
import itertools
parser = argparse.ArgumentParser(description='Take MGF files, and plot the parent mass. Pass in arbitrary number of files, each of which contains a name and a bunch of MGF file paths to plot the parent masses of.')
parser.add_argument('plot_dir', help='Where to save the plots')
parser.add_argument('files', nargs='+', help='Each file contains a name on the first line, and the remaining lines contain paths to MGF files')
args = parser.parse_args()

mgf_sets = []
#path should be a string, and psm_parent_mass_paths is a dictionary that maps the set name to a path
MGF = collections.namedtuple('MGF', ['path', 'psm_parent_mass_paths'])
MGFSet = collections.namedtuple('MGFSet', ['name', 'mgfs', 'psm_parent_names'])
def create_hist(data, num_bins, min_mass, max_mass):
    hist, bin_edges = np.histogram(data, bins=num_bins, range=(1.0*min_mass, 1.0*max_mass))
    bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
    #current area under the curve, divide by it to normalize.
    #auc = np.trapz(hist, bin_centers)
    auc = 1.0*len(data)
    normalized = 100.0*hist/auc
    print('normalized: ' + str(np.sum(normalized)))
    return (hist, normalized, bin_centers, bin_edges)


for file_path in args.files:
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='|')
        headers = list(reader.fieldnames)
        name = headers[0].strip()
        assert(len(name) > 0)
        assert(name not in mgf_sets)
        mgfs = []
        for row in reader:
            mgf_obj = MGF(row[name], {k: row[k] for k in headers[1::]})
            mgfs.append(mgf_obj)
        mgf_sets.append(MGFSet(name, mgfs, headers[1::]))

bin_size = 250

min_mass = 0
max_mass = 10000
print('min mass {}'.format(min_mass))
print('max mass {}'.format(max_mass))
num_bins = int((max_mass - min_mass)*1.0/bin_size)
bin_centers = None
bin_edges = None
MassHist = collections.namedtuple('MassHist', ['name', 'counts'])
Spectrum = collections.namedtuple('Spectrum', ['PEPMASS', 'CHARGE'])
for mgf_set_object in mgf_sets:
    name = mgf_set_object.name
    mgf_objects = mgf_set_object.mgfs
    psm_parent_names = mgf_set_object.psm_parent_names
    fieldnames = ['left', 'center', 'right']
    for mgf_object in mgf_objects:
        mgf_basename = os.path.basename(mgf_object.path)
        fieldnames.append(mgf_basename)
        fieldnames.extend([x + '-' + mgf_basename for x in psm_parent_names])
    histograms = []
    for mgf_object in mgf_objects:
        mgf_basename = os.path.basename(mgf_object.path)
        spectra = {}
        mgf_masses = []
        with open(mgf_object.path, 'r') as g:
            spec_iter = mgf.MGF(g)
            for x in spec_iter:
                assert('scans' in x['params'])
                assert(isinstance(x['params']['scans'], str))
                spectra[x['params']['scans']] = Spectrum(x['params']['pepmass'][0], x['params']['charge'][0])
                mgf_masses.append(x['params']['pepmass'][0]*x['params']['charge'][0])
        mgf_masses.sort()
        unnormalized_hist, hist, temp_bin_centers, temp_bin_edges = create_hist(mgf_masses, num_bins, min_mass, max_mass)
        if bin_centers is None and bin_edges is None:
            bin_centers = list(temp_bin_centers)
            bin_edges = list(temp_bin_edges)
            assert(len(bin_centers) + 1 == len(bin_edges))
        hist = MassHist(mgf_basename, list(unnormalized_hist))
        histograms.append(hist)
        for psm_name, psm_mass_path in mgf_object.psm_parent_mass_paths.items():
            masses = []
            with open(psm_mass_path, 'r') as g:
                psm_reader = csv.DictReader(g, delimiter='\t')
                assert('scan' in psm_reader.fieldnames)
                assert('spectrum neutral mass' in psm_reader.fieldnames)
                for row in psm_reader:
                    scan = row['scan']
                    percolator_mass = row['spectrum neutral mass']
                    assert(scan in spectra)
                    mgf_mass = spectra[scan].PEPMASS*spectra[scan].CHARGE
                    assert(abs(percolator_mass - mgf_mass) < 1.2)
                    masses.append(mgf_mass)
            unnormalized_hist, hist, temp_bin_centers, temp_bin_edges = create_hist(masses, num_bins, min_mass, max_mass)
            histograms.append(MassHist(psm_name + '-' + mgf_basename, list(unnormalized_hist)))
    with open(os.path.join(args.plot_dir, name + '.tsv'), 'w') as f:
        writer = csv.DictWriter(f, fieldnames, delimiter='\t')
        writer.writeheader()
        for i in range(0, len(bin_centers)):
            row = {}
            row['left'] = bin_edges[i]
            row['center'] = bin_centers[i]
            row['right'] = bin_edges[i + 1]
            for hist in histograms:
                row[hist.name] = hist.counts[i]
            writer.writerow(row)


print('DONE')
sys.exit()
