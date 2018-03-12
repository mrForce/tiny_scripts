import editdistance
import random
#import matplotlib.pyplot as plt
from enum import Enum
#from sklearn.decomposition import PCA
import Bio
import os
import sys
from scipy.stats import binom
from Bio.Alphabet import IUPAC
letters = IUPAC.IUPACProtein.letters
class Move(Enum):
    INSERT = 1
    DELETE = 2
    SUBSTITUTE = 3
"""
We want to produce k clusters of variations on a protein. The clusters are defined by the levenshtein distance.

"""

def createChild(seed, distance):
    current_distance = 0
    moves = [Move.INSERT, Move.DELETE, Move.SUBSTITUTE]
    string = seed
    while True:
        if len(string) > 2*len(seed) or len(string) < 0.5*len(seed):
            string = seed
        current_distance = editdistance.eval(seed, string)

        if current_distance == distance:
            return string
        move = random.choice(moves)
        if move == Move.INSERT:
            location = random.choice(range(0, len(string)))
            insertion = random.choice(letters)
            if location == 0:
                string = insertion + string
            elif location == len(string) - 1:
                string = string + insertion
            else:
                string = string[0:location] + insertion + string[location::]
        elif move == Move.DELETE:
            location = random.choice(range(0, len(string)))
            if location == 0:
                string = string[1::]
            elif location == len(string) - 1:
                string = string[0:-1]
            else:
                string = string[0:location] + string[(location + 1)::]
        elif move == Move.SUBSTITUTE:
            location = random.choice(range(0, len(string)))
            letter = random.choice(letters.replace(string[location], ''))
            if location == 0:
                string = letter + string[1::]
            elif location == len(string) - 1:
                string = string[0:-1] + letter
            else:
                string = string[0:location] + letter + string[(location + 1)::]
    return string
            


class Cluster:
    def __init__(self, center_sequence, radius):
        self.center_sequence = center_sequence
        self.radius = radius
        self.children = []
    def generateChildren(self, num_children):
        i = 0
        while i < num_children:
            child = createChild(self.center_sequence, random.choice(range(1, self.radius + 1)))
            if child not in self.children:
                self.children.append(child)
                i += 1
    def getChildren(self):
        return self.children

    def getCenterSequence(self):
        return self.center_sequence


def randomlyDistribute(num_buckets, num_objects):
    buckets = [0]*num_buckets
    for x in range(0, num_objects):
        bucket = random.choice(range(0, num_buckets))
        buckets[bucket] += 1
    return buckets

#return a tuple of the form (n, p)
def random_np_value(mean):
    while True:
        p = random.random()
        n = int(mean/p)
        #got rules of thumb from here: https://en.wikipedia.org/wiki/Binomial_distribution#Normal_approximation
        if n > 9.0*(1 - p)/p and n > 9.0*p/(1 - p):
            return (n, p)

if len(sys.argv) != 5:
    print("Usage: python make_leven_clusters.py seed_file num_clusters mean_cluster_radius num_sequences")
    print("The seed_file should be a plain text file containing the seed sequence on the first line")
else:
    seed_file = sys.argv[1]
    seed = ''
    with open(seed_file, 'r') as f:
        seed = f.read().strip()
    num_clusters = int(sys.argv[2])
    mean_cluster_radius = int(sys.argv[3])
    num_sequences = int(sys.argv[4])
    n, p = random_np_value(mean_cluster_radius)
    print('n: {0}, p: {1}'.format(n, p))
    rv = binom(n, p)
    cluster_radii = rv.rvs(size=num_clusters)
    buckets = randomlyDistribute(num_clusters, num_sequences)
    clusters = []
    print('distributed clusters')
    sequences = list()
    for i in range(0, num_clusters):
        cluster_seed = createChild(seed, random.choice(range(8*mean_cluster_radius, 16*mean_cluster_radius + 1)))
        cluster = Cluster(cluster_seed, cluster_radii[i])
        cluster.generateChildren(buckets[i])
        print('cluster: {0}, sequence: {1}, radius: {2}'.format(i + 1, cluster_seed, cluster_radii[i]))
        for x in cluster.getChildren():
            assert(editdistance.eval(cluster_seed, x) <= cluster_radii[i])
            sequences.append(x)
            print(x)
    i = 0
    for sequence in sequences:
        print('> {0}'.format(i))
        print(sequence)
        i += 1
        
