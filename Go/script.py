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
import multiprocessing
sample_size = 100
maxStaticSize = 16
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

def draw_gc_result_plt(data, column_name, xlabel, ylabel, fig_name):
    # We require xy to be of same size here

    df = pd.DataFrame(data, columns = column_name)
    g=sns.PairGrid(df, y_vars = [column_name[0]], x_vars =[column_name[1],column_name[2],column_name[3]])
    g=g.map(sns.scatterplot)
    #sns_plot = sns.scatterplot(data = df, x= column_name[0], y = [column_name[1],column_name[2],column_name[3]])
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
        commands.append("./program -u "
        + str(size_list[i])
        + " -dir "
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
        draw_result_plt(x, y, ["UnitSize", "Allocation Speed"], "UnitSize", "AllocationSpeed", "allocation_size_baseline")

    # Baseline test based on Duration time

    start_size = 10
    commands = []
    for i in range(sample_size):

        commands.append("./program -d "+
        str(start_size + i * 10)
        + " -dir "
        + "duration_baseline_result.json"
        + " -r a"
        + " -p m"
        )

    for command in commands:
        print(command)
        os.system(command)
    # Open the json file to get the result
    with open("duration_baseline_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        x = []
        y = []
        for item in content:
            x.append(item["Duration"])
            y.append(item["AllocationSpeed"])

        # draw fig based on that
        draw_result_plt(x, y, ["Duration", "Allocation Speed"], "Duration", "AllocationSpeed", "baseline_duration")

def gc():

    # First do different thread, limited choice here, so we only do from zero to the max number of thread
    '''
    thread_num = []
    thread = 1
    commands = []
    while thread <= multiprocessing.cpu_count():

        commands.append("./program -t "
        + str(thread)
        + " -dir "
        + " thread_num_gc_result.json"
        + " -r b"
        + " -p m")

        thread = thread + 1

    for command in commands:
        os.system(command)

    with open("thread_num_gc_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        data = []
        for i in content:
            data.append([i['ThreadCount'], i['RAMUseBefore']-i['RAMUseAfter'], i["AllocationSpeed"],i["GCrate"]])

        draw_gc_result_plt(data, ["Thread Count", "RAMUsage", "Allcation Speed", "GC Rate"], "Thread Count", ["RAMUsage", "Allcation Speed", "GC Rate"], "thread_num_gc_result")

    # Different Duration
    start_size = 10
    commands = []
    for i in range(sample_size):

        commands.append("./program -d "+
        str(start_size + i * 10)
        + " -dir "
        + "duration_gc_result.json"
        + " -r b"
        + " -p m"
        )

    for command in commands:
        print(command)
        os.system(command)

    with open("duration_gc_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        data = []
        for i in content:
            data.append([i['Duration'], i['RAMUseBefore']-i['RAMUseAfter'], i["AllocationSpeed"],i["GCrate"]])

        draw_gc_result_plt(data, ["Duration", "RAMUsage", "Allcation Speed", "GC Rate"], "Duration", ["RAMUsage", "Allcation Speed", "GC Rate"], "duration_gc_result")

    # Different time factor
    start_size = 1
    commands = []
    for i in range(sample_size):

        commands.append("./program -w "+
        str(start_size + i * 0.5)
        + " -dir "
        + "time_factor_gc_result.json"
        + " -r b"
        + " -p m"
        )

    for command in commands:
        print(command)
        os.system(command)

    with open("time_factor_gc_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        data = []
        for i in content:
            data.append([i['MaxTime'], i['RAMUseBefore']-i['RAMUseAfter'], i["AllocationSpeed"],i["GCrate"]])

        draw_gc_result_plt(data, ["MaxTime", "RAMUsage", "Allcation Speed", "GC Rate"], "Time Factor", ["RAMUsage", "Allcation Speed", "GC Rate"], "time_factor_gc_result")



    start_size = 32
    commands = []
    for i in range(sample_size):

        commands.append("./program -o "+
        str(start_size + i*10 )
        + " -dir "
        + "cap_size_gc_result.json"
        + " -r b"
        + " -p m"
        )

    for command in commands:
        print(command)
        os.system(command)

    with open("cap_size_gc_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        data = []
        cnt = 1

        # I cannot figure out why staticsetsize does not show up in the json file.....
        for i in content:
            data.append([i["MaxSize"], i['RAMUseBefore']-i['RAMUseAfter'], i["AllocationSpeed"],i["GCrate"]])
            cnt = cnt +1
        draw_gc_result_plt(data, ["Size Base", "RAMUsage", "Allcation Speed", "GC Rate"], "Size Base", ["RAMUsage", "Allcation Speed", "GC Rate"], "cap_size_gc_result")
    '''
    # Static Size
    start_size = 1
    commands = []
    for i in range(16):

        commands.append("./program -m "+
        str(start_size + i )
        + " -dir "
        + "static_size_gc_result.json"
        + " -r b"
        + " -p m"
        )

    for command in commands:
        print(command)
        os.system(command)

    with open("static_size_gc_result.json", "r") as f:
        # json format here
        content = json.load(f)
        # collect out the x-axis and y-axis seperately
        data = []
        cnt = 1

        # I cannot figure out why staticsetsize does not show up in the json file.....
        for i in content:
            data.append([cnt, i['RAMUseBefore']-i['RAMUseAfter'], i["AllocationSpeed"],i["GCrate"]])
            cnt = cnt +1
        draw_gc_result_plt(data, ["staticSetSize", "RAMUsage", "Allcation Speed", "GC Rate"], "Static Set Size", ["RAMUsage", "Allcation Speed", "GC Rate"], "static_size_gc_result")

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
        gc()
if __name__ == "__main__":

    main(sys.argv[1:])