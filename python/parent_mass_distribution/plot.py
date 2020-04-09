import argparse
from pyteomics import mgf
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats
import math
import itertools
parser = argparse.ArgumentParser(description='Take MGF files, and plot the parent mass. Pass in arbitrary number of files, each of which contains a name and a bunch of MGF file paths to plot the parent masses of.')
parser.add_argument('plot_dir', help='Where to save the plots')
parser.add_argument('files', nargs='+', help='Each file contains a name on the first line, and the remaining lines contain paths to MGF files')
args = parser.parse_args()

mgf_sets = {}

for file_path in args.files:
    with open(file_path, 'r') as f:
        name = f.readline().strip()
        assert(len(name) > 0)
        assert(name not in mgf_sets)
        mgf_paths = []
        for x in f:
            if len(x.strip()) > 1:
                mgf_paths.append(x.strip())
        mgf_sets[name] = mgf_paths

mass_sets = {}
kernels = {}
bin_size = 250
for name, mgf_set in mgf_sets.items():
    masses = []
    for mgf_file in mgf_set:
        f = open(mgf_file, 'r')
        spec_iter = mgf.MGF(f)
        mgf_masses = []
        for x in spec_iter:
            mgf_masses.append(x['params']['pepmass'][0]*x['params']['charge'][0])
        masses.append(mgf_masses)
    mass_sets[name] = masses

min_mass = int(min([min(itertools.chain(*x)) for x in mass_sets.values()]))
max_mass = math.ceil(max([max(itertools.chain(*x)) for x in mass_sets.values()]))
print('min mass {}'.format(min_mass))
print('max mass {}'.format(max_mass))
num_bins = math.ceil((max_mass - min_mass)*1.0/bin_size)
for name, mgf_set_masses in mass_sets.items():
    print('plotting')
    for x in mgf_set_masses:
        hist, bin_edges = np.histogram(x, bins=num_bins, density=True)
        bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
        plt.plot(bin_centers, hist)
    
    
    #bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
    #plt.plot(bin_centers, hist.shape[0])
    plt.savefig(os.path.join(args.plot_dir, name + '.png'))
    plt.clf()

for name, mgf_set_masses in mass_sets.items():
    hist, bin_edges = np.histogram(list(itertools.chain.from_iterable(mgf_set_masses)), bins = num_bins, density=True)
    bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
    plt.plot(bin_centers, hist, label=name)
plt.legend(loc='upper right')
plt.savefig(os.path.join(args.plot_dir, 'combined.png'))
"""
nums, bins, patches = plt.hist(list(itertools.chain.from_iterable(mass_sets.values())), label=list(mass_sets.keys()), density=True, bins=num_bins, histtype='step')
plt.legend(loc='upper right')
plt.savefig(os.path.join(args.plot_dir, 'combined.png'))


fig, ax = plt.subplots()
for name, masses in mass_sets.items():
    kernel = stats.gaussian_kde(masses)
    y_points = kernel.evaluate(x_vals)
    ax.plot(x_vals, y_points, label=name)

plt.legend(loc='upper right')
plt.savefig(os.path.join(args.plot_dir, 'combined.png'))
combined_kernels = {k: stats.gaussian_kde(v) for k,v in mass_sets.items()}
combined_yvals = [(k, v.evaluate(x_vals)) for k,v in combined_kernels.items()]
plt.plot(x_vals, [x[1] for x in combined_yvals], label=[x[0] for x in combined_yvals])
plt.savefig(args.plot)

nums, bins, patches = plt.hist(list(mass_sets.values()), label=list(mass_sets.keys()), density=True)
plt.legend(loc='upper right')
plt.savefig(args.plot)
"""
