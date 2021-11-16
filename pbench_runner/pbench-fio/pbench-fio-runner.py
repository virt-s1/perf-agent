#!/usr/bin/env python3

# Description:
#   The runner for scheduling pbench-fio runs.
#
# Maintainers:
#   Charles Shih <schrht@gmail.com>
#

"""pbench-fio runner.

The runner for scheduling pbench-fio runs.
"""

import argparse
import logging
import toml
import json
import subprocess

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

ARG_PARSER = argparse.ArgumentParser(
    description="The runner for scheduling pbench-fio runs.")

ARG_PARSER.add_argument('--testrun-id',
                        dest='testrun_id',
                        action='store',
                        help='The TestRun ID associated with this run.',
                        default=None,
                        required=True)
ARG_PARSER.add_argument('--targets',
                        dest='targets',
                        action='store',
                        help='The pbench-fio targets argument.',
                        default=None,
                        required=True)
ARG_PARSER.add_argument('--mode',
                        dest='mode',
                        action='store',
                        help='The pre-defined testing mode.',
                        choices=['quick', 'standard', 'extended',
                                 'customized', 'reproducing'],
                        required=True)
ARG_PARSER.add_argument('--profile',
                        dest='profile',
                        action='store',
                        help='The profile of the pre-defined modes.',
                        default='./profiles.toml',
                        required=False)
ARG_PARSER.add_argument('--report-id',
                        dest='report_id',
                        action='store',
                        help='The benchmark report ID to be analized. '
                        '(a picli request will be triggered to query '
                        'information)',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--test-types',
                        dest='test_types',
                        action='store',
                        help='The pbench-fio test-types argument.',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--block-sizes',
                        dest='block_sizes',
                        action='store',
                        help='The pbench-fio block-sizes argument.',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--iodepth',
                        dest='iodepth',
                        action='store',
                        help='The pbench-fio iodepth argument.',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--numjobs',
                        dest='numjobs',
                        action='store',
                        help='The pbench-fio numjobs argument.',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--samples',
                        dest='samples',
                        action='store',
                        help='The pbench-fio samples argument.',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--runtime',
                        dest='runtime',
                        action='store',
                        help='The pbench-fio runtime argument.',
                        default=None,
                        required=False)
ARG_PARSER.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='Parse the arguments only without running '
                        'any test cases.',
                        default=None,
                        required=False)


if __name__ == '__main__':

    # Parse parameters
    ARGS = ARG_PARSER.parse_args()

    testrun_id = str(ARGS.testrun_id)
    if not testrun_id.startswith('fio_'):
        LOG.error('TestRun ID is invalid. It must start with "fio_".')
        exit(1)

    if ARGS.mode in ('quick', 'standard', 'extended'):
        # No pbench-fio arguments should be specified
        if (ARGS.test_types is not None
                or ARGS.block_sizes is not None
                or ARGS.iodepth is not None
                or ARGS.numjobs is not None
                or ARGS.samples is not None
                or ARGS.runtime is not None):
            LOG.error('Cannot overwrite "test_types", "block_sizes", '
                      '"iodepth", "numjobs", "samples", "runtime" arguments '
                      'in specified mode.')
            exit(1)

    if ARGS.mode == 'reproducing':
        if ARGS.report_id is None:
            LOG.error(
                'The "report-id" must be specified in "reproducing" mode.')
            exit(1)

        if (ARGS.test_types is not None
                or ARGS.block_sizes is not None
                or ARGS.iodepth is not None
                or ARGS.numjobs is not None):
            LOG.error('Cannot overwrite "test_types", "block_sizes", '
                      '"iodepth", "numjobs" arguments in "reproducing" mode.')
            exit(1)

    # Read profile
    LOG.info('Loading profiles...')
    try:
        with open(ARGS.profile, 'r') as f:
            profile = toml.load(f)
    except Exception as err:
        LOG.error('Failed to load the profile: {}'.format(err))
        exit(1)

    # Update pbench-fio arguments
    arguments = profile.get('DEFAULT', {})
    arguments.update(profile.get(ARGS.mode, {}))

    arguments.update({'config': testrun_id.removeprefix('fio_')})
    arguments.update({'targets': ARGS.targets})

    LOG.debug('pbench-fio arguments:\n{}'.format(
        json.dumps(arguments, indent=3)))

    pbench_fio_runs = []
    if ARGS.mode == 'reproducing':
        # TODO: generate reproducing runs.
        pass
    else:
        if ARGS.mode == 'customized':
            # TODO: overwrite for customized runs.
            pass

        # Expend the iodepth and numjobs iterations
        LOG.info('Expending the iodepth and numjobs iterations...')
        iodepth_list = arguments.pop('iodepth', '1')
        numjobs_list = arguments.pop('numjobs', '1')
        for iodepth in iodepth_list.split(','):
            for numjobs in numjobs_list.split(','):
                LOG.debug('Expending to (iodepth={}, numjobs={})'.format(
                    iodepth, numjobs))
                _pbench_fio_args = arguments.copy()
                _pbench_fio_args.update(
                    {'iodepth': iodepth, 'numjobs': numjobs})
                pbench_fio_runs.append(_pbench_fio_args)

    LOG.debug('pbench-fio arguments list:\n{}'.format(
        json.dumps(pbench_fio_runs, indent=3)))

    # Verify pbench-fio runs
    LOG.info('Verifing the pbench-fio runs...')

    essential_args = (
        'job-file', 'pre-iteration-script', 'job-mode', 'config',
        'targets', 'test-types', 'block-sizes', 'iodepth', 'numjobs',
        'samples', 'runtime'
    )

    for pbench_fio_run in pbench_fio_runs:
        for args in essential_args:
            if args not in pbench_fio_run:
                LOG.error('Missing "{}" from pbench-fio run: {}'.format(
                    args, pbench_fio_run))
                exit(1)

    # Execute pbench-fio runs
    LOG.info('Executing the pbench-fio runs...')
    for pbench_fio_run in pbench_fio_runs:
        cmd = 'pbench-fio'
        for k, v in pbench_fio_run.items():
            cmd += ' --{}={}'.format(k, v)

        LOG.info('Run command: {}'.format(cmd))
        if not ARGS.dry_run:
            subprocess.run(cmd, shell=True, encoding='utf-8')

    exit(0)
