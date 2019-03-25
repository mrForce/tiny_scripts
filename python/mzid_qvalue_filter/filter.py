import argparse
from pyteomics import mzid

parser = argparse.ArgumentParser(description='Filter an MzIdentML file by q-value')

parser.add_argument('input', description='input mzid file')
parser.add_argument('threshold', type=float, description='maximum q value')
parser.add_argument('output', description='location of filtered mzid file')
namespace = '{http://psidev.info/psi/pi/mzIdentML/1.1}'
args = parser.parse_args()
m = mzid.MzIdentML(args.input)
m.build_tree()
tree = m._tree
identifications = tree.findall('./*/%sAnalysisData/*/%sSpectrumIdentificationResult' % (namespace, namespace))

for ident in identifications:
    items = ident.findall('%sSpectrumIdentificationItem' % namespace)
    assert(len(items) == 1)
    item = items[0]
    q_value = float(item.find('%scvParam[@name=\'MS-GF:QValue\']' % namespace).attrib['value'])
    if q_value > args.threshold:
        ident.find('..').remove(ident)


tree.write(args.output)
