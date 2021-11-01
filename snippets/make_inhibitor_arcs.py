import random
import sys
import threading
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

NAMESPACE = '{http://www.pnml.org/version-2009/grammar/pnml}'
INHIB_PERCENTAGE = 10
MCC_DIRECTORY = sys.argv[1]
NUM_THREADS = 3
if len(sys.argv) < 2:
    print("You did not give a path to the MCC directory")


def add_inhibitors(models):
    num_models = len(models)
    converted_models = 0

    for model in models:
        if converted_models % 10 == 0:
            print(f"{threading.current_thread().getName()}: Converted models: {converted_models}/{num_models}")
        ET.register_namespace('', 'http://www.pnml.org/version-2009/grammar/pnml')
        mytree = ET.parse(model)
        myroot = mytree.getroot()

        page = myroot[0][0]
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


models = [model for model in Path(MCC_DIRECTORY).rglob('*.pnml')]
chunks = np.array_split(models, NUM_THREADS)
for i in range(NUM_THREADS):
    chunk = [chunks[i]][0]
    threading.Thread(target=add_inhibitors, name=f"T{i}",
                     args=[chunk]).start()
