import math
import copy
import pickle
import sys
from enum import Enum
import collections
import numpy as np
from scipy.special import logsumexp
import matplotlib.pyplot as plt
from scipy import stats
class PlotMode(Enum):
    KERNEL = 1
    HIST = 2
#min_length = 2
#max_length = 4
#amino_acids = {4: 0.2, 12: 0.8}
min_mass = 0
max_mass = 4000



amino_acids = {89: 0.0825, 174: 0.0553, 132: 0.0406, 133: 0.0545, 121: 0.0137, 146: 0.098, 147: 0.0675, 75: 0.0707, 155: 0.0227, 131: 0.1562, 149: 0.0242, 165: 0.038599999999999995, 115: 0.047, 105: 0.06559999999999999, 119: 0.054, 204: 0.0108, 181: 0.0292, 117: 0.0687}
total_prob = sum(amino_acids.values())
min_length = 2
max_length = math.ceil(max_mass*1.0/max(amino_acids.keys()))

#subtract np.log(total_prob) to make sure it's a probability distribution
amino_acids_log_freq = {x: np.log(y) - np.log(total_prob) for x, y in amino_acids.items()}

#map the length to a dictionary {mass: log probability}
result = {1: {x: np.log(y) for x, y in amino_acids.items()}}
for i in range(2, max_length + 1):
    length_i_result = {}
    for pep_mass, mass_log_prob in result[i - 1].items():
        for aa_mass, aa_log_freq in amino_acids_log_freq.items():
            if pep_mass + aa_mass in length_i_result:
                #note: since we're storing log probs, we can't simply add their probability if they have the same mass
                #we'll deal with adding at the end.
                length_i_result[pep_mass + aa_mass].append(aa_log_freq + mass_log_prob)
            else:
                length_i_result[pep_mass + aa_mass] = [aa_log_freq + mass_log_prob]
    result[i] = {}
    for k, v in length_i_result.items():
        assert(len(v) > 0)
        if len(v) == 1:
            result[i][k] = v[0]
        else:
            result[i][k] = logsumexp(v)

kernels = {}
x_points = np.arange(min_mass, max_mass, 1)
fig, ax = plt.subplots()
mode = PlotMode.HIST
bin_size = 250.0
num_bins = math.ceil((max_mass - min_mass)*1.0/bin_size)

for i in range(min_length, max_length + 1):
    final_masses = []
    final_probs = []
    for mass, log_prob in result[i].items():
        final_masses.append(mass)
        final_probs.append(np.exp(log_prob))
    print('i: ' + str(i))
    print(final_masses)
    print(final_probs)
    if mode == PlotMode.HIST:
        hist, bin_edges = np.histogram(final_masses, bins=num_bins, density=True, weights=final_probs)
        bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
        ax.plot(bin_centers, hist, label=str(i))
    elif mode == PlotMode.KERNEL:
        kernel = stats.gaussian_kde(final_masses, weights=final_probs)
        y_points = kernel.evaluate(x_points)
        ax.plot(x_points, y_points, label=str(i))
plt.legend(loc='upper right')
plt.savefig('length_mass.png')
average_mass = np.average(list(amino_acids.keys()), weights=list(amino_acids.values()))
print('average mass: ' + str(average_mass))
for x in range(min_length, max_length + 1):
    print('average mass at length {}: {}'.format(x, x*average_mass))
