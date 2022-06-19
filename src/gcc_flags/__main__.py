#!/usr/bin/env python

import argparse
from gcc_flags import process

def main():
    parser = argparse.ArgumentParser(description='Collect GCC C++ warning options.')
    parser.add_argument('BINARY', help='path to the g++ binary (default: g++)',
                        default='g++', type=str, nargs='?')

    args = parser.parse_args()

    process(args.BINARY)


if __name__ == "__main__":
    main()
