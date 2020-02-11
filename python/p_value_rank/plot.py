import matplotlib
import matplotlib.pyplot as plt
import csv
import math
import argparse

def plot_pvals(pvals, sidak_correction):
    #plog log10 of p-value rank on x-axis, and
    if sidak_correction:
        pvals = [1.0 - math.pow(1.0 - p, n) for p, n in pvals]
    else:
        pvals = [p for p, n in pvals]
    sorted_pvals = sorted(pvals)
    log_pvals = [math.log10(x) for x in sorted_pvals]
    num_pvals = len(log_pvals)
    log_rank_pvals = [math.log10(1.0*j/num_pvals) for j in range(1, num_pvals + 1)]
    fig, ax = plt.subplots()
    ax.set_xlabel('log10(rank p-value)')
    ax.set_ylabel('log10(p-value)')
    
    ax.plot(log_rank_pvals, log_pvals, 'bD')
    min_ = min(min(log_pvals), min(log_rank_pvals))
    ax.plot([min_, 0.0], [min_, 0.0], 'k-')
    ax.plot([min_, 0.0], [math.log10(2.0) + min_, math.log10(2.0) + 0.0], 'k--')
    ax.plot([min_, 0.0], [min_ + math.log10(0.5), math.log10(0.5)], 'k--')


parser = argparse.ArgumentParser()
parser.add_argument('tide_search_results')
args = parser.parse_args()

tide_search_results = args.tide_search_results

sidak_correction = True

with open(tide_search_results, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    pvals = []
    for x in reader:
        pvals.append((float(x['exact p-value']), float(x['total matches/spectrum'])))

    plot_pvals(pvals, sidak_correction)
    plt.savefig('plot.png')
        
