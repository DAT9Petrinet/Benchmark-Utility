import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NAMESPACE = '{http://www.pnml.org/version-2009/grammar/pnml}'
ET.register_namespace('', 'http://www.pnml.org/version-2009/grammar/pnml')
INHIB_PERCENTAGE = 10
MCC_DIRECTORY = sys.argv[1]

if len(sys.argv) < 2:
    print("You did not give a path to the MCC directory")

models = [model for model in Path(MCC_DIRECTORY).rglob('*.pnml')]
num_models = len(models)
converted_models = 0

for model in models:
    if converted_models % 10 == 0:
        print(f"Converted models: {converted_models}/{num_models}")

    mytree = ET.parse(model)
    myroot = mytree.getroot()

    net = myroot.find(f'{NAMESPACE}' + 'net')
    page = net.find(f'{NAMESPACE}' + 'page')
    arcs = page.findall(f'{NAMESPACE}' + 'arc')
    transitions = page.findall(f'{NAMESPACE}' + 'transition')

    transition_ids = [transition.attrib.get('id') for transition in transitions]
    arcs_to_transitions = [arc for arc in arcs if arc.attrib.get('target') in transition_ids]
    num_arcs_to_convert = round(len(arcs_to_transitions) * (INHIB_PERCENTAGE / 100.0))

    arcs_to_convert = random.sample(arcs_to_transitions, num_arcs_to_convert)

    for arc in arcs:
        if arc in arcs_to_convert:
            arc.set('type', 'inhibitor')
        else:
            arc.set('type', 'normal')

    tree = ET.ElementTree(myroot)
    tree.write(model, xml_declaration=True)
    converted_models += 1
