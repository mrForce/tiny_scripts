from Bio import SeqIO
import collections
import random
num_sequences = 100
seq_length = 11
motifs = ['xxSxAxxKxxx', 'xHTxxQPxxxW']
proteome = 'human.fasta'


aa_counter = collections.Counter()
for record in SeqIO.parse(proteome, 'fasta'):
    for x in record.seq:
        aa_counter[x] += 1
random.seed()
weights = dict()
total = sum(aa_counter.values())
for k, v in aa_counter.items():
    weights[k] = 1.0*v/total

print('weights')
print(weights)
#map motifs to sequences
sequences = {motif:[] for motif in motifs}
for i in range(0, num_sequences):
    motif = random.choice(motifs)
    num_wildcards = motif.count('x')
    num_fixed = seq_length - num_wildcards
    wildcards = random.choices(list(weights.keys()), weights=list(weights.values()), k=num_wildcards)
    wildcard_index = 0
    seq = []
    for x in motif:
        if x == 'x':
            seq.append(wildcards[wildcard_index])
            wildcard_index += 1
        else:
            seq.append(x)
    sequences[motif].append(''.join(seq))
for k, v in sequences.items():
    print("motif: " + k)
    for x in v:
        print(x)
