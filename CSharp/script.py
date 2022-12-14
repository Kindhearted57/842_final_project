'''
In order to make it easier the linear figure is created outside Go, and using a Python script instead here
'''

import json
import os
import sys
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from typing import List

sample_size = 100
# Generate fig based on two lists
def draw_result_plt(x, y, column_name, xlabel, ylabel, fig_name):
    # We require xy to be of same size here
    data = []
    for i in range(len(x)):
        data.append([x[i],y[i]])
    df = pd.DataFrame(data, columns = column_name)
    sns_plot = sns.scatterplot(data = df, x= column_name[0], y = column_name[1])
    plt.savefig(fig_name+".pdf")
    plt.clf()


# Baseline ---

def baseline():
    # First do baseline test based on different allocation size
    # In order to do allocation size base line the allocation size has
    # to be changed into a parameter to the function

    baseline_size_result = []
    commands = []
    size_list = []
    start_size = 16
    for i in range(sample_size):
        size_list.append(start_size+ i*10)
        commands.append("dotnet run --project App/GCBurn.App.csproj -c Release -f net5.0 -- -d 10 -u "
        + str(size_list[i])
        + " -f "
        + " allocation_size_baseline_result.json"
        + " -r a"
        + " -p m")

    # Baseline test based on Allocation Size
    for command in commands:
        os.system(command)

    # Open the json file to get the result
    with open("allocation_size_baseline_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        x = []
        y = []
        for item in content:
            x.append(item["UnitSize"])
            y.append(item["AllocationSpeed"])

        # draw fig based on that
        draw_result_plt(x, y, ["UnitSize", "AllocationSpeed"], "UnitSize", "AllocationSpeed", "allocation_size_baseline")

    # Baseline test based on Duration time

def gc():
    # First do
    pass
def main(argv: List[str]):

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clean", action="store_true")
    parser_subs = parser.add_subparsers(dest="cmd")
    parser_raw = parser_subs.add_parser("baseline", help="Run the benchmarks on baseline")
    parser_gc = parser_subs.add_parser("gc", help="Run then benchmarks on Garbage Collectors")

    args = parser.parse_args(argv)

    if args.clean == True:
        #if clean flag is on, remove all the pdf/json file
        os.remove("baseline_duration.pdf")
        os.remove("duration_baseline_result.json")
        os.remove("allocation_size_baseline_result.json")
        os.remove("allocation_size_baseline.pdf")
    if args.cmd == "baseline":

        baseline()
    if args.cmd == "gc":
        pass
if __name__ == "__main__":

    main(sys.argv[1:])