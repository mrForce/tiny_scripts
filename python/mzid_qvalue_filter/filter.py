import argparse
from pyteomics import mzid

parser = argparse.ArgumentParser(description='Filter an MzIdentML file by q-value')

parser.add_argument('input', help='input mzid file')
parser.add_argument('threshold', type=float, help='maximum q value')
parser.add_argument('output', help='location of filtered mzid file')
namespace = '{http://psidev.info/psi/pi/mzIdentML/1.1}'
args = parser.parse_args()
m = mzid.MzIdentML(args.input)
m.build_tree()
tree = m._tree
identifications = tree.findall('./*/%sAnalysisData/*/%sSpectrumIdentificationResult' % (namespace, namespace))

num_identifications = 0
num_removals = 0

for ident in identifications:
    items = ident.findall('%sSpectrumIdentificationItem' % namespace)
    for item in items:
        q_value = float(item.find('%scvParam[@name=\'MS-GF:PepQValue\']' % namespace).attrib['value'])
        num_identifications += 1
        if q_value > args.threshold:
            ident.find('..').remove(ident)            
            num_removals += 1
            break

tree.write(args.output, xml_declaration=True)
print('num identifications: %d, num removals: %d, num confident matches: %d' % (num_identifications, num_removals, num_identifications - num_removals))
