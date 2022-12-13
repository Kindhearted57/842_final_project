'''
This script is for creating final results
'''
import os
import args
import seaborn as sns
import pandas as pd 
import matplotlib.pyplot as plt
import sys
# Generate fig based on two lists
def draw_result_plt(x, y, column_name, xlabel, ylabel):
    # We require xy to be of same size here
    for i in len(x):
         df = pd.DataFrame(x, y, columns = [column_name])
         sns.lineplot(data = df)


def run_baseline():
    # Based on different allocation size
    # Return a list of
    # Create
    baseline_size_result = [] 
    
    size_list = []
    start_size = 100
    for i in range(10):
        size_list.append(start_size+ i*10)

    # First test the 
    for i in range(10):

        base_command = ["-m"]
        base_command.append(str(i))
        base_command.append("baseline")
        baseline_size_result.append(args.args(base_command))
        

    # draw the figure with size as x-axis and result as y-axis
    # draw_result_plt(size_list, baseline_size_result)



if __name__ == "__main__":
    run_baseline()

    