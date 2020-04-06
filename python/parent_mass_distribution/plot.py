import argparse
from pyteomics import mgf
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Take MGF files, and plot the parent mass. Pass in arbitrary number of files, each of which contains a name and a bunch of MGF file paths to plot the parent masses of.')
parser.add_argument('plot', help='Where to save the Histogram')
parser.add_argument('files', nargs='+', help='Each file contains a name on the first line, and the remaining lines contain paths to MGF files')
args = parser.parse_args()

mgf_sets = {}

colors = ['red', 'green', 'blue']

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
for name, mgf_set in mgf_sets.items():
    masses = []
    for mgf_file in mgf_set:
        f = open(mgf_file, 'r')
        spec_iter = mgf.MGF(f)
        for x in spec_iter:
            masses.append(x['params']['pepmass'][0])
    mass_sets[name] = masses

    
nums, bins, patches = plt.hist(list(mass_sets.values()), label=list(mass_sets.keys()), density=True)
plt.legend(loc='upper right')
plt.savefig(args.plot)
