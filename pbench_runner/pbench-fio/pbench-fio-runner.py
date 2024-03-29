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

ARG_PARSER.add_argument(
    '--testrun-id',
    dest='testrun_id',
    action='store',
    help='The TestRun ID associated with this run.',
    default=None,
    required=True)
ARG_PARSER.add_argument(
    '--targets',
    dest='targets',
    action='store',
    help='[pbench-fio] targets argument.',
    default=None,
    required=True)
ARG_PARSER.add_argument(
    '--mode',
    dest='mode',
    action='store',
    help='The pre-defined mode from profile. Such as "quick", "standard", \
"extended", "backlog", etc... When adding your own mode, please make sure \
it is defined in the profile (see "customized" mode as an example).',
    default=None,
    required=True)
ARG_PARSER.add_argument(
    '--profile',
    dest='profile',
    action='store',
    help='The profile of the pre-defined modes.',
    default='./profiles.toml',
    required=False)
ARG_PARSER.add_argument(
    '--backlog-file',
    dest='backlog_file',
    action='store',
    help='The backlog file with the testcases to run.',
    default='backlog.toml',
    required=False)
ARG_PARSER.add_argument(
    '--test-types',
    dest='test_types',
    action='store',
    help='[pbench-fio] test-types argument.',
    default=None,
    required=False)
ARG_PARSER.add_argument(
    '--block-sizes',
    dest='block_sizes',
    action='store',
    help='[pbench-fio] block-sizes argument.',
    default=None,
    required=False)
ARG_PARSER.add_argument(
    '--iodepth',
    dest='iodepth',
    action='store',
    help='[pbench-fio] iodepth argument.',
    default=None,
    required=False)
ARG_PARSER.add_argument(
    '--numjobs',
    dest='numjobs',
    action='store',
    help='[pbench-fio] numjobs argument.',
    default=None,
    required=False)
ARG_PARSER.add_argument(
    '--samples',
    dest='samples',
    action='store',
    help='[pbench-fio] samples argument.',
    default=None,
    required=False)
ARG_PARSER.add_argument(
    '--runtime',
    dest='runtime',
    action='store',
    help='[pbench-fio] runtime argument.',
    default=None,
    required=False)
ARG_PARSER.add_argument(
    '--dry-run',
    dest='dry_run',
    action='store_true',
    help='Only parse the parameters without running any test cases.',
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
        # No pbench-fio arguments should be specified in these modes
        if (ARGS.test_types is not None
                or ARGS.block_sizes is not None
                or ARGS.iodepth is not None
                or ARGS.numjobs is not None
                or ARGS.samples is not None
                or ARGS.runtime is not None):
            LOG.error('"quick", "standard" and "extended" are system \
reserved modes. Therefore "test_types", "block_sizes", "iodepth", "numjobs", \
"samples", and "runtime" arguments cannot be overwritten by CLI.')
            exit(1)

    if ARGS.mode == 'backlog':
        if ARGS.backlog_file is None:
            LOG.error(
                'The "backlog-file" must be specified in "backlog" mode.')
            exit(1)

        if (ARGS.test_types is not None
                or ARGS.block_sizes is not None
                or ARGS.iodepth is not None
                or ARGS.numjobs is not None):
            LOG.error('"backlog" is a system reserved mode. Therefore \
"test_types", "block_sizes", "iodepth", "numjobs", "samples", and "runtime" \
arguments cannot be overwritten by CLI.')
            exit(1)

    # Gather pbench-fio arguments from profile
    LOG.info('Gathering pbench-fio arguments...')

    try:
        with open(ARGS.profile, 'r') as f:
            profiles = toml.load(f)
    except Exception as err:
        LOG.error('Failed to load the profile: {}'.format(err))
        exit(1)

    if ARGS.mode not in profiles:
        LOG.error('The mode "{}" is not defined in profile {}'.format(
            ARGS.mode, ARGS.profile))
        exit(1)

    arguments = profiles.get('DEFAULT', {})
    arguments.update(profiles.get(ARGS.mode, {}))

    # Overwrite with CLI arguments
    arguments.update({'config': testrun_id[4:]})
    arguments.update({'targets': ARGS.targets})

    if ARGS.test_types:
        arguments.update({'test-types': ARGS.test_types})
    if ARGS.block_sizes:
        arguments.update({'block-sizes': ARGS.block_sizes})
    if ARGS.iodepth:
        arguments.update({'iodepth': ARGS.iodepth})
    if ARGS.numjobs:
        arguments.update({'numjobs': ARGS.numjobs})
    if ARGS.samples:
        arguments.update({'samples': ARGS.samples})
    if ARGS.runtime:
        arguments.update({'runtime': ARGS.runtime})

    LOG.debug('pbench-fio arguments:\n{}'.format(
        json.dumps(arguments, indent=3)))

    # Expend to the pbench-fio runs
    pbench_fio_runs = []
    if ARGS.mode == 'backlog':
        # Load the testcases from the backlog file
        LOG.info('Getting the testcases from backlog...')

        with open(ARGS.backlog_file, 'r') as f:
            backlog = toml.load(f)

        testcases = backlog.get('testcases', [])
        if not testcases:
            LOG.info('No testcases have been found in backlog.')
            exit(0)

        for args in testcases:
            args.pop('CASE_ID', None)

            _pbench_fio_args = arguments.copy()
            _pbench_fio_args.update(args)
            pbench_fio_runs.append(_pbench_fio_args)
    else:
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
        
        # Use bs, iodepth, njobs, r/w type as the config tag
        pbench_fio_run['config'] = "bs_{}_iod_{}_njobs_{}_{}".format(
            pbench_fio_run['block-sizes'], pbench_fio_run['iodepth'],
            pbench_fio_run['numjobs'], pbench_fio_run['test-types'])
        
        for k, v in pbench_fio_run.items():
            cmd += ' --{}={}'.format(k, v)

        LOG.info('Run command: {}'.format(cmd))
        if not ARGS.dry_run:
            subprocess.run(cmd, shell=True, encoding='utf-8')

    exit(0)
