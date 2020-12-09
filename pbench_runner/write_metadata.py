#!/usr/bin/env python
"""Write metadata to a json file.

Write user provided metadata entries to a specified json file.
"""

import argparse
import os
import json

ARG_PARSER = argparse.ArgumentParser(description="Write user provided \
metadata entries to a specified json file.")

ARG_PARSER.add_argument('--file',
                        dest='file',
                        action='store',
                        help='The file stores the metadata, will create a \
new one if not found.',
                        default='./testrun_metadata.json',
                        required=False)
ARG_PARSER.add_argument('--keypair',
                        dest='keypair',
                        action='append',
                        help='The metadata in KEY=VALUE format to be added \
or updated. This argument can be provided multiple times.',
                        required=True)

ARGS = ARG_PARSER.parse_args()

if __name__ == '__main__':

    # Read the metadata entries or init from scratch
    if os.path.isfile(ARGS.file):
        with open(ARGS.file, 'r') as f:
            metadata = json.load(f)
    else:
        dirname = os.path.dirname(ARGS.file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        metadata = {}

    # Update the metadata entries
    for keypair in ARGS.keypair:
        key, value = keypair.split('=')
        metadata[key] = value

    # Write the metadata entries
    with open(ARGS.file, 'w') as f:
        json.dump(metadata, f, indent=3, sort_keys=True)

    exit(0)
