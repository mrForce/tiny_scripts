from Bio import SeqIO

import sys

if len(sys.argv) > 2:
    fasta_file_name = sys.argv[1]
    lengths = []
    j = 0
    for x in sys.argv[2::]:
        lengths.append(int(x))
    num_proteins = 0
    with open(fasta_file_name, 'r') as handle:
        for x in SeqIO.parse(handle, 'fasta'):
            num_proteins += 1
    with open(fasta_file_name, 'r') as handle:
        protein_i = 0
        for record in SeqIO.parse(handle, 'fasta'):
            protein = record.seq
            for length in lengths:
                for i in range(0, len(protein) - length + 1):
                    print('>' + str(j))
                    j += 1
                    print(protein[i:(i + length)])
            protein_i += 1
            print('progress: ' + str(100.0*protein_i/num_proteins), file=sys.stderr)
