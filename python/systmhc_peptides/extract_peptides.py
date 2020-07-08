import csv
import re
import collections

name = 'buffy94_ions.csv'
field_name = 'PeptideIon'
f = open(name, 'r')

peptide_regex = re.compile('^[A-Z\-]\.(?P<peptide>.*)\.[A-Z\-]/')
ptm_removal_regex = re.compile('\[[^\]]*\]')
def parse_peptide(peptide, peptide_regex, ptm_removal_regex):
    match = peptide_regex.match(peptide)
    if match and match.group('peptide'):
        peptide = match.group('peptide')
    return ptm_removal_regex.sub('', peptide)


reader = csv.DictReader(f, quotechar='"')
peptides = collections.defaultdict(list)

for x in reader:
    #print('peptide ion: ' + x[field_name])
    parsed_peptide = parse_peptide(x[field_name], peptide_regex, ptm_removal_regex)
    #print('peptide: ' + parsed_peptide)
    peptides[parsed_peptide].append(x[field_name])

for k, v in peptides.items():
    print(k)
    """
    if len(v) > 1:
        print('peptide: ' + k)
        for x in v:
            print(x)
    """
#for peptide in list(peptides):
#    print(peptide)
    
