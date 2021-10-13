import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir):
    print("nice")

if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    paths = sys.argv[1:]
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    data_list = [pd.read_csv(path) for path in paths]
    plot(data_list, test_names, graph_dir)