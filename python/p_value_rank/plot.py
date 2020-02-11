import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import csv
import math
import argparse
import random



def plot_pvals(pvals, sidak_correction, fig, ax):
    #plog log10 of p-value rank on x-axis, and
    if sidak_correction:
        pvals = [1.0 - math.pow(1.0 - p, n) for p, n in pvals]
    else:
        pvals = [p for p, n in pvals]
    sorted_pvals = sorted(pvals)
    log_pvals = [math.log10(x) for x in sorted_pvals]
    num_pvals = len(log_pvals)
    log_rank_pvals = [math.log10(1.0*j/num_pvals) for j in range(1, num_pvals + 1)]
    ax.set_xlabel('log10(rank p-value)')
    ax.set_ylabel('log10(p-value)')
    
    ax.plot(log_rank_pvals, log_pvals, 'bD')
    min_ = min(min(log_pvals), min(log_rank_pvals))
    ax.plot([min_, 0.0], [min_, 0.0], 'k-')
    ax.plot([min_, 0.0], [math.log10(2.0) + min_, math.log10(2.0) + 0.0], 'k--')
    ax.plot([min_, 0.0], [min_ + math.log10(0.5), math.log10(0.5)], 'k--')


parser = argparse.ArgumentParser()
parser.add_argument('tide_search_results')
parser.add_argument('output_image')
parser.add_argument('mode', choices=['sidak', 'random'])
args = parser.parse_args()

tide_search_results = args.tide_search_results

#if mode is 'random', then for each spectra, use a random match
#if mode is 'sidak', then use min p-value and correct with Sidak corrections
mode = args.mode
spectra_id_field = 'scan'
spectra_dict = {}
with open(tide_search_results, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for x in reader:
        scan = x[spectra_id_field]
        if scan in spectra_dict:
            assert(spectra_dict[scan]['n'] == x['distinct matches/spectrum'])
            spectra_dict[scan]['pvals'].append(float(x['exact p-value']))
        else:
            spectra_dict[scan]['pvals'] = [float(x['exact p-value'])]
            spectra_dict[scan]['n'] = x['distinct matches/spectrum']
    
    pvals = []
    for scan, val in spectra_dict.items():
        pval = None
        if mode == 'sidak':
            pval = min(val['pvals'])
        elif mode == 'random':
            pval = random.choice(val['pvals'])
        pvals.append((pval, float(val['n'])))
    fig = Figure()
    ax = fig.subplots()
    
    plot_pvals(pvals, sidak_correction, fig, ax)
    fig.savefig(args.output_image, format='png')        
