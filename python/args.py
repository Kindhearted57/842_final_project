import speed_tester
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
    speed_tester.run_speed_tester(speedTester)
    
def GCTest():
    pass

def write_json_to_file(data, file_name):
    with open(file_name, "w") as f:
        json.dump(data , f)

def args(argv: List[str]):

    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--duration",help="Test pass duration (seconds)",default=10)
    # Change the default value later
    parser.add_argument("-m", "--set-size",help = "Static set size (GB)", default = 1)
    parser.add_argument("-t", "--thread-num", help = "Number of threads to use", default = 10)
    # Change the default value later
    parser.add_argument("-o", "--object-size", help = "Maximum of object size", default = 10)
    parser_subs = parser.add_subparsers(dest="cmd")
    parser_test = parser_subs.add_parser(
        "test", help = "Choose which test to run"
    )

    parser_test_subs = parser_test.add_subparsers(dest="cmd_test")
    parser_test_subs_raw = parser_test_subs.add_parser("raw", help = "Test flag for raw allocation")
    parser_test_subs_gc = parser_test_subs.add_parser("gc", help = "Test flag for garbage collection")
    
    args = parser.parse_args(argv)
    if args.cmd_test == "raw":
        result = runSpeedTest()
        return result
        # collect the result and hand to the drawing part

    elif args.cmd_test == "gc":
        pass
    else:
        parser.print_help()



