import os



def num_lines_overlap(file_one, file_two):
    lines_one = set()
    lines_two = set()
    with open(file_one, 'r') as f:
        for line in f:
            lines_one.add(line.strip())
    with open(file_two, 'r') as f:
        for line in f:
            lines_two.add(line.strip())
    return len(lines_one.intersection(lines_two))

files = [('2% Combined NetMHC, Prep, NetMHC Decoys', 'combined/five_percent_prep.txt'), ('2% Combined NetMHC, Prep, reversed decoys', 'combined_normal/five_percent_prep.txt'), ('2% Combined NetMHC, Run2, NetMHC Decoys', 'combined/five_percent_run2.txt'), ('2% Combined NetMHC, Run2, Reversed decoys', 'combined_normal/five_percent_run2.txt'), ('1% Combined NetMHC, Prep, NetMHC Decoys', 'combined_one_percent/five_percent_prep.txt'), ('1% Combined NetMHC, Prep, reversed decoys', 'combined_normal_one_percent/five_percent_prep.txt'), ('1% Combined NetMHC, Run2, NetMHC Decoys', 'combined_one_percent/five_percent_run2.txt'), ('1% Combined NetMHC, Run2, Reversed decoys', 'combined_normal_one_percent/five_percent_run2.txt')]

table = [[''] + [x[0] for x in files]]
for name_one, file_path_one in files:
    row = [name]
    for name_two, file_path_two in files:
        row.append(str(num_lines_overlap(file_path_one, file_path_two)))

for row in table:
    print('\t'.join(row))
