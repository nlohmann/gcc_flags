#!/usr/bin/env python

import argparse
from typing import List
from gcc_flags import process, __version__, EvaluatedOption
import json


def console_output(evaluated_options: List[EvaluatedOption]):
    print()

    for option in sorted([x for x in evaluated_options if not x.error], key=lambda x: x.option):
        print(option)

    print()

    for option in sorted([x for x in evaluated_options if x.error], key=lambda x: x.option):
        print(option)

def json_output(evaluated_options: List[EvaluatedOption]):
    result = []
    for option in sorted([x for x in evaluated_options], key=lambda x: x.option):
        result.append(dict(option))

    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(prog='gcc_flags', description='Collect GCC C++ warning options.')
    parser.add_argument('BINARY', help='path to the g++ binary (default: g++)',
                        default='g++', type=str, nargs='?')
    parser.add_argument('--json', help='create JSON output for flags', action='store_true')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    options = process(binary=args.BINARY)
    if args.json:
        json_output(options)
    else:
        console_output(options)


if __name__ == "__main__":
    main()
