from Bio import SeqIO

import sys

if len(sys.argv) > 2:
    fasta_file_name = sys.argv[1]
    lengths = []
    for x in sys.argv[2::]:
        lengths.append(int(x))
    with open(fasta_file_name, 'r') as handle:
        for record in SeqIO.parse(handle, "fasta"):
            protein = record.seq
            for length in lengths:
                for i in range(0, len(protein) - length + 1):
                    print(protein[i:(i + length)])
