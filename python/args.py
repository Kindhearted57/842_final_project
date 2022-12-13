import speed_tester
import GC.burn_tester as gb
import argparse
import sys
from typing import List
import threading
import json

def runWarmup():
    baselineTester = speed_tester.NewWarmupSpeedTester()
    baselineTester.Run()
    
def runSpeedTest():
    speedTester = speed_tester.NewSpeedTester()
    # invoke the run function from speed_tester
    result = speed_tester.run_speed_tester(speedTester)
    return result
def GCTest(setsize):
    gcTester = gb.NewGCTester(setsize)

def write_json_to_file(data, file_name):
    with open(file_name, "w") as f:
        json.dump(data , f)

def args(argv: List[str]):
    print("hi!")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--duration",help="Test pass duration (seconds)",default=10)
    # Change the default value later
    parser.add_argument("-m", "--setsize",help = "Static set size (GB)", default = 1)
    parser.add_argument("-t", "--thread-num", help = "Number of threads to use", default = 10)
    # Change the default value later
    parser.add_argument("-o", "--object-size", help = "Maximum of object size", default = 10)
    parser_subs = parser.add_subparsers(dest="cmd")

    parser_test_subs_raw = parser_subs.add_parser("baseline", help = "Baseline Test")
    parser_test_subs_gc = parser_subs.add_parser("gc", help = "GC Test")
    
    args = parser.parse_args(argv)
    print(args)
    if args.cmd == "baseline":
       
        result = runSpeedTest()
        
        # collect the result and hand to the drawing part

    elif args.cmd == "gc":
        result = GCTest(args.setsize)
    else:
        parser.print_help()



