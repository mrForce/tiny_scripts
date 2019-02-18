from collections import Counter
import sys

from Bio import SeqIO
import math
import pdb
from scipy.stats import binom
import numpy as np
import itertools

from hmmlearn.hmm import MultinomialHMM
class UnalignedSequencesError(Exception):
    def __init__(self):
        self.message = "Not all of the sequences were of the same length"
        

class ProfileHMM:
    """
    I don't think it makes any sense to use a negative HMM. After all, negatives are all the sequences that simply do not bind well to the MHC. 

    Only pass in background_dataset if you want to. It should be a list of sequences, each of the same length as the sequences in the positive and negative datasets

    alphabet should be a list of symbols.

    num_rows should be an integer that specifies the number of rows we want.
    """
    def __init__(self, positive_dataset, alphabet, num_rows):
        positive_pwm = dict()


        self.alphabet = alphabet
        self.amino_acids_in_dataset = list(set(itertools.chain(*positive_dataset)))
        self.residue_mapper = dict(zip(self.amino_acids_in_dataset, range(0, len(self.amino_acids_in_dataset))))
        i = len(self.amino_acids_in_dataset)
        for amino_acid in self.alphabet:
            if amino_acid not in self.residue_mapper:
                self.residue_mapper[amino_acid] = i
                i += 1
    """
            Generate n floating points that add up to 1.0
    """
    @staticmethod
    def compute_random_row(num_elements):
        elements = np.random.uniform(0.0, 1.0, num_elements)
        total = sum(elements)
        return elements/total

    @staticmethod
    def computeHMM(dataset, alphabet, num_matchstates = 9):
        num_sequences = len(dataset)
        best_score = None
        best_model = None
        alphabet = list(alphabet)
        residue_mapper = {alphabet[j]: j for j in range(0, len(alphabet))}
        #one begin, one end, num_matchstates + 1 insert states, num_matchstates match states, num_matchstates deletion states.
        num_states = 3 + 3*num_matchstates
        concat_dataset = np.concatenate([[[residue_mapper[x]] for x in y] for y in dataset])
        dataset_lengths = [len(x) for x in dataset]
        for x in range(0, 10):
            transition_matrix = np.zeros((num_states, num_states))
            emission_matrix = np.zeros((num_states, len(alphabet)))
            #first num_matchstates + 2 are the matchstates (including beginning and end, though those two are mute
            #first do B, then M_1,...,M_m
            #B goes to either I_0 or M_1.
            b_row = ProfileHMM.compute_random_row(2)
            transition_matrix[0][1] = b_row[0]
            transition_matrix[0][2] = b_row[1]
            for i in range(1, num_matchstates + 1):
                #go to either match state, insertion state, or delete state.
                m_row = ProfileHMM.compute_random_row(3)
                #next match state
                transition_matrix[i][i + 1] = m_row[0]
                #insert state
                transition_matrix[i][i + num_matchstates + 2] = m_row[1]
                #deletion state
                print('i: %d' % i)
                transition_matrix[i][i + 2*num_matchstates + 2] = m_row[2]
                emission_matrix[i] = ProfileHMM.compute_random_row(len(alphabet))                
            #now we do the insertion states.
            for i in range(num_matchstates + 2, 2*num_matchstates + 3):
                #either go to self, or next match state.
                row = ProfileHMM.compute_random_row(2)
                transition_matrix[i][i] = row[0]
                transition_matrix[i][i - (num_matchstates + 1)] = row[1]
                emission_matrix[i] = ProfileHMM.compute_random_row(len(alphabet))
            #now do deletion states. In the loop, do all but the last one
            for i in range(2*num_matchstates + 3, 3*num_matchstates + 2):            
                row = ProfileHMM.compute_random_row(2)
                transition_matrix[i][i] = row[0]
                transition_matrix[i][i - 2*num_matchstates - 1] = row[1]                
            model = MultinomialHMM(num_states, params="ets")
            model.n_features = len(alphabet)
            start_prob = np.zeros(num_states)
            start_prob[0] = 1.0
            print('start prob array')
            print(start_prob)
            model.startprob_ = start_prob
            model.transmat_ = transition_matrix
            model.emissionprob_ = emission_matrix
            try:
                model.fit(concat_dataset, dataset_lengths)
            except ValueError:
                pdb.set_trace()
            print('model')
            print(model)
            """
            for row in range(0, len(model.emissionprob_)):
                for col in range(0, len(model.emissionprob_[row])):
                    count = model.emissionprob_[row][col]*num_sequences
                    model.emissionprob_[row][col] = (count + 0.01)/(num_sequences + len(alphabet)*0.01)
            """
            print('emission probabilities')
            print(model.emissionprob_)
            score = model.score(concat_dataset, dataset_lengths)
            if x == 0:
                best_score = score
                best_model = model
            elif score > best_score:
                best_score = score
                best_model = model
        return best_model

    
alphabet = 'ACDEFGHIKLMNPQRSTVWY'

sequences = list()
with open('eg7_initial.fasta', 'r') as f:
    for record in SeqIO.parse(f, 'fasta'):
        sequences.append(str(record.seq))

ProfileHMM.computeHMM(sequences, alphabet)
