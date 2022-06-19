#!/usr/bin/env python

import argparse
from gcc_flags import process, __version__

def main():
    parser = argparse.ArgumentParser(prog='gcc_flags', description='Collect GCC C++ warning options.')
    parser.add_argument('BINARY', help='path to the g++ binary (default: g++)',
                        default='g++', type=str, nargs='?')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    process(args.BINARY)


if __name__ == "__main__":
    main()
