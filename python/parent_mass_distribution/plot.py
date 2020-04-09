import argparse
from pyteomics import mgf
import matplotlib.pyplot as plt
import os
from scipy import stats
import math

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
for name, mgf_set in mgf_sets.items():
    masses = []
    for mgf_file in mgf_set:
        f = open(mgf_file, 'r')
        spec_iter = mgf.MGF(f)
        mgf_masses = []
        for x in spec_iter:
            mgf_masses.append(x['params']['pepmass'][0]*x['params']['charge'][0])
        kernel = stats.gaussian_kde(mgf_masses)
        kernels[mgf_file] = (kernel, name)
        masses.extend(mgf_masses)
        """
        pre, extension = os.path.splitext(mgf_file)
        png_name = pre + '.png'
        nums, bins, patches = plt.hist(mgf_masses, label=name, density=True)
        plt.legend(loc='upper right')
        plt.savefig(png_name)
        masses.extend(mgf_masses)
        plt.clf()
        """
    mass_sets[name] = masses

min_mass = int(min([min(x) for x in mass_sets.values()]))
max_mass = math.ceil(max([max(x) for x in mass_sets.values()]))

x_vals = list(range(min_mass, max_mass + 1))
for name, value in kernels.items():
    kernel, mgf_set_name = value
    plt.plot(x_vals, kernel.evaluate(x_vals), label=mgf_set_name)
    plt.legend(loc='upper right')
    pre, ext = os.path.splitext(name)
    png_name = pre + '.png'
    plt.savefig(os.path.join(args.plot_dir, png_name))
    plt.clf()

fig, ax = plt.subplots()
for name, masses in mass_sets.items():
    kernel = stats.gaussian_kde(masses)
    y_points = kernel.evaluate(x_vals)
    ax.plot(x_vals, y_points, label=name)

plt.legend(loc='upper right')
plt.savefig(os.path.join(args.plot_dir, 'combined.png'))
"""
combined_kernels = {k: stats.gaussian_kde(v) for k,v in mass_sets.items()}
combined_yvals = [(k, v.evaluate(x_vals)) for k,v in combined_kernels.items()]
plt.plot(x_vals, [x[1] for x in combined_yvals], label=[x[0] for x in combined_yvals])
plt.savefig(args.plot)

nums, bins, patches = plt.hist(list(mass_sets.values()), label=list(mass_sets.keys()), density=True)
plt.legend(loc='upper right')
plt.savefig(args.plot)
"""
