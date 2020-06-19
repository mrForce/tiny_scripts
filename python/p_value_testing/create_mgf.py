import random
import subprocess
import re
aminos = 'AVMSCKRDPW'
num_peptides = 500
peptide_length = 9

peptides = set()
charge = 2

while len(peptides) < num_peptides:
    peptide = ''.join(random.choices(aminos, k=peptide_length))
    if peptide not in peptides:
        peptides.add(peptide)

mass_regex = re.compile('MONO:(\S*)')
ion_regex = re.compile('(\d+\.\d+)')

def generate_spectrum(peptide, charge, index, mass_regex, ion_regex):
    command = ['/home/jforce/crux', 'predict-peptide-ions', peptide, str(charge)]
    with open('spectra/' + str(index) + '.txt', 'w') as f:
        subprocess.run(command, stdout=f)

    mono_mass = None
    #ion mass to charge ratios
    ions = []
    with open('spectra/' + str(index) + '.txt', 'r') as f:
        for line in f:
            mono_match = mass_regex.search(line)
            if mono_match:
                assert(mono_mass is None)
                mono_mass = mono_match.group(1)
            else:
                ion_match = ion_regex.match(line)
                if ion_match:
                    ion = ion_match.group(1)
                    ions.append(float(ion))
    assert(mono_mass)
    assert(ions)
    return (index, float(charge), float(mono_mass)/float(charge), ions)

def create_mgf(spectra, output_path):
    lines = []

    for spectrum in spectra:
        index = spectrum[0]
        charge = spectrum[1]
        pepmass = spectrum[2]
        ions = spectrum[3]
        lines.append('BEGIN IONS\n')
        lines.append('SCANS=' + str(index)+ '\n')
        lines.append('CHARGE=' + str(charge) + '\n')
        lines.append('PEPMASS=' + str(pepmass) + '\n')
        for ion in sorted(ions):
            lines.append(str(ion) + ' ' + str(random.uniform(1.0, 5.0)) + '\n')
        lines.append('END IONS\n')
    with open(output_path, 'w') as f:
        f.writelines(lines)

peptides_list = list(peptides)
spectra = [generate_spectrum(peptides_list[i], charge, i + 1, mass_regex, ion_regex) for i in range(0, num_peptides)]

create_mgf(spectra, 'thing.mgf')

