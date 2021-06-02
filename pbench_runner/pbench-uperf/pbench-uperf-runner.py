# -*- coding=utf-8 -*-


# File Name: pbench-uperf-runner.py
# Description:
#	A wrapper of pbench-uperf, supports 0 or multi test parameters.
# Reversions:
#   v0.0.1 - 03/01/2021 - Built the script.
#   v0.0.2 - 04/02/2021 - Enhanced arguments output.


import os
import argparse
import subprocess


parser = argparse.ArgumentParser(description = "Arguments of Pbench-uperf.")

parser.add_argument("--server_ip", required=True,   help = "Server IP of pbench-uperf.")
parser.add_argument("--client_ip", required=True,   help = "Client IP of pbench-uperf.")
parser.add_argument("--config", required=True,      help = "Unique ID for whole test.")
parser.add_argument("--test_suite_name",            help = "Test suite name.")
parser.add_argument("--protocols",      "-p",       help = "Network performance protocols supports.")
parser.add_argument("--test_types",     "-t",       help = "Network performance test types supports.")
parser.add_argument("--runtime",        "-r",       help = "Run time one case run.")
parser.add_argument("--message_sizes",  "-m",       help = "Message size used in test.")
parser.add_argument("--instances",      "-i",       help = "Counts of threads.")
parser.add_argument("--nr_samples",     "-ns",      help = "Counts of runs.")
parser.add_argument("--max_failures",   "-mf",      help = "Max failures times of one case.")
parser.add_argument("--maxstddevpct",   "-ms",      help = "Max stddevpct to check.")

args = parser.parse_args()


# Define three test suites for pbench-uperf-quick-tests.
def test_suites(test_suite_name):
    # Different test suite, run differet test matrix.
    if test_suite_name == "quick" or test_suite_name == None:
        print("INFO: Run pbench-uperf with quick test suite.")
        protocols = "tcp,udp"
        test_types = "stream,maerts,rr,bidirec"
        instances = "1"
        runtime = 10
        message_sizes = "1,64"
        nr_samples = 3
        max_failures = 3
        maxstddevpct = 5
    elif test_suite_name == "standard":
        print("INFO: Run pbench-uperf with standard test suite.")
        protocols = "tcp,udp"
        test_types = "stream,maerts,rr,bidirec"
        instances = "1,8"
        runtime = 20
        message_sizes = "1,64,1024"
        nr_samples = 3
        max_failures = 3
        maxstddevpct = 5
    elif test_suite_name == "extended":
        print("INFO: Run pbench-uperf with extended test suite.")
        protocols = "tcp,udp"
        test_types = "stream,maerts,rr,bidirec"
        instances = "1,8,64"
        runtime = 60
        message_sizes = "1,64,1024,16384"
        nr_samples = 5
        max_failures = 6
        maxstddevpct = 5
    else:
        print("ERROR: Incorrect test suite name.")
        return False

    return protocols, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct


# Function to execute pbench-uperf command.
def run(server_ip, client_ip, config, protocols, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct):

    command = "pbench-uperf "
    command += "-S {} ".format(server_ip)
    command += "-C {} ".format(client_ip)
    command += "-c {} ".format(config)

    # If parameter isn't provided, will use the default hard-code values in pbench-uperf.
    if test_types:
        command += "-t {} ".format(test_types)
    if runtime:
        command += "-r {} ".format(runtime)
    if message_sizes:
        command += "-m {} ".format(message_sizes)
    if protocols:
        command += "-p {} ".format(protocols)
    if instances:
        command += "-i {} ".format(instances)
    if nr_samples:
        command += "--samples={} ".format(nr_samples)
    if max_failures:
        command += "--max-failures={} ".format(max_failures)
    if maxstddevpct:
        command += "--max-stddev={} ".format(maxstddevpct)
    print("DEBUG: command:", command)

    ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    # Store ret.stdout to a file.


# Main.
if __name__ == '__main__':
    # Get mandatory arguments.
    server_ip = args.server_ip
    client_ip = args.client_ip
    config = args.config
    
    # Ignore others arguments from command line, run test_suite_name test matrix.
    test_suite_name = args.test_suite_name
    if not test_suite_name:
        # Get users arguments from commands when test_suite_name is null.
        print("INFO: Run users parameters in command line.")
        protocols = args.protocols
        print("protocols: ", protocols)
        test_types = args.test_types
        print("test_types: ", test_types)
        instances = args.instances
        print("instances: ", instances)
        runtime = args.runtime
        print("runtime: ", runtime)
        message_sizes = args.message_sizes
        print("message_sizes: ", message_sizes)
        nr_samples = args.nr_samples
        print("nr_samples: ", nr_samples)
        max_failures = args.max_failures
        print("max_failures: ", max_failures)
        maxstddevpct = args.maxstddevpct
        print("maxstddevpct: ", maxstddevpct)

        run(server_ip, client_ip, config, protocols, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct)
    else:
        print("INFO: Run test suite.")
        protocols, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct = test_suites(test_suite_name)

        run(server_ip, client_ip, config, protocols, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct)
