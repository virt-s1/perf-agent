# -*- coding=utf-8 -*-


# File Name: pbench-uperf-runner.py
#
# Description:
#	A wrapper of pbench-uperf, supports 0 or multi test parameters.
#
# Owner:
#   Bo Yang <boyang@redhat.com>
#
# Reversions:
#   v0.0.1 - 03/01/2021 - Bo Yang - Built the script.
#   v0.0.2 - 04/02/2021 - Bo Yang - Enhanced arguments output.
#   v0.0.3 - 11/16/2021 - Charles Shih - PEP 8 formating.
#   v0.0.4 - 11/16/2021 - Charles Shih - Update the help message.
#   v0.1.0 - 11/22/2021 - Charles Shih - Add support to the backlog.
#   v0.1.1 - 11/22/2021 - Charles Shih - Add dry-run parameter.


import os
import argparse
import subprocess
import toml


parser = argparse.ArgumentParser(description="Arguments of Pbench-uperf.")

parser.add_argument("--server_ip", required=True,
                    help="Server IP of pbench-uperf.")
parser.add_argument("--client_ip", required=True,
                    help="Client IP of pbench-uperf.")
parser.add_argument("--config", required=True,
                    help="Unique ID for whole test.")
parser.add_argument("--test_suite_name",
                    choices=['quick', 'standard', 'extended', 'backlog'],
                    help="Run as the pre-defined testsuite. "
                    "(By using this, below args will be overwriten)")
parser.add_argument("--protocols", "-p",
                    help="Network performance protocols supports.")
parser.add_argument("--test_types", "-t",
                    help="Network performance test types supports.")
parser.add_argument("--runtime", "-r",
                    help="Run time one case run.")
parser.add_argument("--message_sizes", "-m",
                    help="Message size used in test.")
parser.add_argument("--instances", "-i", help="Counts of threads.")
parser.add_argument("--nr_samples", "-ns", help="Counts of runs.")
parser.add_argument("--max_failures", "-mf",
                    help="Max failures times of one case.")
parser.add_argument("--maxstddevpct", "-ms",
                    help="Max stddevpct to check.")
parser.add_argument("--backlog-file",
                    dest='backlog_file',
                    action='store',
                    help='The backlog file with the testcases to run.',
                    default='backlog.toml',
                    required=False)
parser.add_argument('--dry-run',
                    dest='dry_run',
                    action='store_true',
                    help='Only parse the parameters without running any test cases.',
                    default=None,
                    required=False)

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

    return (protocols, test_types, runtime, message_sizes, instances,
            nr_samples, max_failures, maxstddevpct)


# Function to execute pbench-uperf command.
def run(server_ip, client_ip, config, protocols, test_types, runtime,
        message_sizes, instances, nr_samples, max_failures, maxstddevpct):

    print("protocols: ", protocols)
    print("test_types: ", test_types)
    print("instances: ", instances)
    print("runtime: ", runtime)
    print("message_sizes: ", message_sizes)
    print("nr_samples: ", nr_samples)
    print("max_failures: ", max_failures)
    print("maxstddevpct: ", maxstddevpct)

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

    if not args.dry_run:
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, encoding="utf-8")
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
        test_types = args.test_types
        instances = args.instances
        runtime = args.runtime
        message_sizes = args.message_sizes
        nr_samples = args.nr_samples
        max_failures = args.max_failures
        maxstddevpct = args.maxstddevpct

        run(server_ip, client_ip, config, protocols, test_types, runtime,
            message_sizes, instances, nr_samples, max_failures, maxstddevpct)
    elif test_suite_name == 'backlog':
        # Get users arguments from commands when test_suite_name is null.
        print('INFO: Run users parameters in backlog mode.')

        if args.backlog_file is None:
            print('The "backlog-file" must be specified in "backlog" mode.')
            exit(1)
        else:
            with open(args.backlog_file, 'r') as f:
                backlog = toml.load(f)

        testcases = backlog.get('testcases', [])
        if not testcases:
            print('No testcases have been found in backlog.')
            exit(0)

        for testcase in testcases:
            # Get default arguments
            (protocols, test_types, runtime, message_sizes, instances,
             nr_samples, max_failures, maxstddevpct) = test_suites('standard')

            # Update for the current testcase
            test_types = testcase.get('test-types')
            protocols = testcase.get('protocols')
            message_sizes = testcase.get('message-sizes')
            instances = testcase.get('instances')

            # Run test testcase
            run(server_ip, client_ip, config, protocols, test_types, runtime,
                message_sizes, instances, nr_samples, max_failures, maxstddevpct)
    else:
        print("INFO: Run test suite.")
        (protocols, test_types, runtime, message_sizes, instances, nr_samples,
         max_failures, maxstddevpct) = test_suites(test_suite_name)

        run(server_ip, client_ip, config, protocols, test_types, runtime,
            message_sizes, instances, nr_samples, max_failures, maxstddevpct)
