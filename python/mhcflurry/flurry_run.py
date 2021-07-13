import mhcflurry
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Run MHCFlurry on a list of peptide and set of alleles, output a matrix')
parser.add_argument('peptideFile', help='File with peptides in it')
parser.add_argument('output', help='Where to store the matrix output')
parser.add_argument('allele', nargs='+', help='Alleles to score peptides with')

args = parser.parse_args()
mhcflurry.common.configure_tensorflow(backend='tensorflow-default')
predictor=mhcflurry.Class1AffinityPredictor.load()
with open(args.peptideFile, 'r') as f:
    peptides = f.read().split('\n')
    peptides.remove('')
    arrays = []
    for allele in args.allele:
        arrays.append(predictor.predict(allele=allele, peptides=peptides))
    with open(args.output, 'wb') as g:
        np.save(g, np.stack(arrays, axis=1))    
