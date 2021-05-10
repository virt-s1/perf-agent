#!/usr/bin/env python
"""Make TestRunID.

Make TestRunID based on the information provided by the user.
"""

import argparse
import time

ARG_PARSER = argparse.ArgumentParser(description="Make TestRunID based on \
the information provided by the user.")

ARG_PARSER.add_argument('--type',
                        dest='type',
                        action='store',
                        help='Type of the performance tests.',
                        choices=['fio', 'uperf'],
                        default='UnknownType',
                        required=True)
ARG_PARSER.add_argument('--platform',
                        dest='platform',
                        action='store',
                        help='Which platform the tests are running on.',
                        choices=['ESXi', 'HyperV', 'AWS', 'Azure', 'KVM'],
                        default='UnknownPlatform',
                        required=True)
ARG_PARSER.add_argument('--compose',
                        dest='compose',
                        action='store',
                        help='The RHEL Compose Name or ID for the tests.',
                        default='UnknownCompose',
                        required=True)
ARG_PARSER.add_argument('--customized-labels',
                        dest='customized_labels',
                        action='store',
                        help='Customized labels used to generate the \
TestRunID, separated by underline (_) between multiple labels.',
                        default='',
                        required=True)
ARG_PARSER.add_argument('--timestamp',
                        dest='timestamp',
                        action='store',
                        help='The timestamp in "D%%y%%m%%dT%%H%%M%%S" format, \
the current timestamp will be used if not speicified.',
                        default=None,
                        required=False)

ARGS = ARG_PARSER.parse_args()

if __name__ == '__main__':

    # Get timestamp or make a new one
    timestamp = ARGS.timestamp if ARGS.timestamp else time.strftime(
        'D%y%m%dT%H%M%S', time.localtime())

    # Make the TestRunID
    testrunid = '_'.join((ARGS.type, ARGS.platform, ARGS.compose,
                          ARGS.customized_labels, timestamp))

    # Send to stdout
    print(testrunid)

    exit(0)
