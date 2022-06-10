#!/usr/bin/env python3

import argparse
import re
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple

from termcolor import colored


# TODO: Help for -Wstringop-overflow is not properly collected.


def get_help_strings(binary: str) -> Dict[str, str]:
    # collect all warnings from g++
    with subprocess.Popen([binary, '--help=warnings'],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proc:
        output = proc.stdout.read().decode('utf-8')

    result = {}  # type: Dict[str, str]

    # option, followed by help, and possible additional help in second line
    for match in re.findall(r'[ ]+(-[^ ]+)[ ]+([^\n]+)(\n {2}[^-][ ]*([^\n]+))*', output):
        option, help1, _, help2 = match

        # combine help lines
        doc = help1 + ' ' + help2
        doc = doc.strip()

        result[option] = doc

    return result


def test_compile_with_option(binary: str, option: str) -> Tuple[int, str]:
    options = option.split()

    # compile a test program to check if the parameter works
    with tempfile.TemporaryDirectory() as tmpdir:
        with subprocess.Popen([binary, '-x', 'c++'] + options + ['-'],
                              stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE, cwd=tmpdir) as proc:
            proc.stdin.write('int main() {}\n'.encode('utf-8'))
            proc.stdin.close()
            error_output = proc.stderr.read().decode('utf-8').strip()

    return proc.returncode, error_output


def get_all_options(binary: str) -> List[str]:
    # collect all warnings from g++
    with subprocess.Popen([binary, '-Q', '--help=warnings'],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proc:
        output = proc.stdout.read().decode('utf-8')

    result = []  # type: List[str]

    # skip first and last line
    for line in output.splitlines()[1:-1]:
        line = line.strip()
        line = line.replace('\t', ' ')

        # option is everything before the first whitespace
        option = line.split(' ', 1)[0].strip()
        result.append(option)

    return result


class EvaluatedOption:
    def __init__(self):
        self.option = ''  # type: str
        self.help = ''  # type: str
        self.error = None  # type: Optional[str]

    def __repr__(self):
        result = f'{self.option:50} {self.help}'

        if self.error:
            result += '\n ' + self.error

        return result


def process(binary: str):
    help_strings = get_help_strings(binary)
    all_options = get_all_options(binary)
    max_option_len = max(len(option) for option in all_options)

    evaluated_options = []  # type: List[EvaluatedOption]
    todo_options = list(sorted(all_options))
    total_options = len(all_options)

    while len(todo_options) > 0:
        option = todo_options.pop(0)

        progress = (total_options - len(todo_options)) / total_options * 100
        print(f'[{progress:3.0f}%] {option:<{max_option_len}} ', end='', flush=True)

        # remove redundant options
        match = re.findall(r"Same as '?(-[^ ']+)", help_strings.get(option, ''))
        if len(match) and '=' in match[0]:
            print(colored(f'✘ duplicate of {match[0]}', 'blue'))
            continue

        # remove options that just disable other options
        if help_strings.get(option, '').startswith('Disable'):
            print(colored('✘ disables a warning', 'blue'))
            continue

        return_code, error_output = test_compile_with_option(binary, option)

        if return_code != 0 or len(error_output) > 0:
            # ignore options that do not work with C++
            if 'not for C++' in error_output:
                error_msg = error_output[error_output.index('is valid') + 3:]
                print(colored(f'✘ {error_msg}', 'red'))
                continue

            # check if option requires another option to be given
            match = re.findall(r"ignored without '?(-[^ ']+)", error_output)
            if len(match):
                # add required option to list of options to check
                todo_options.insert(0, match[0] + ' ' + option)
                print(colored(f'? depends on {match[0]}; trying next', 'yellow'))
                continue

            # use value ranges and lists
            match = re.findall(r'=[<\[]([^>\]]+)[>\]]', option)
            if len(match):
                base, _ = option.split('=')

                # value range (take upper bound)
                if ',' in match[0]:
                    _, upper = match[0].split(',')
                    todo_options.insert(0, base + '=' + upper)
                    print(colored(f'? expects argument from <{match[0]}>; trying next', 'yellow'))
                    continue

                # value list (take last element)
                if '|' in match[0]:
                    todo_options.insert(0, base + '=' + match[0].split('|')[-1])
                    print(colored(f'? expects argument from [{match[0]}]; trying next', 'yellow'))
                    continue

            print(colored('✘ error', 'red'))

            # create entry for failed option
            evaluated_option = EvaluatedOption()
            evaluated_option.option = option
            evaluated_option.help = help_strings.get(option, '')
            evaluated_option.error = error_output
            evaluated_options.append(evaluated_option)

        else:
            print(colored('✔ works', 'green'))

            evaluated_option = EvaluatedOption()
            evaluated_option.option = option

            # if multiple options are given, use the last one to look up the help string
            option_list = option.split()
            if len(option_list) > 1:
                evaluated_option.help = help_strings.get(option_list[-1])
            else:
                evaluated_option.help = help_strings.get(option)

            # if the option contains a =, we need to put more effort into looking up the help string
            if '=' in option:
                for help_option, help_string in help_strings.items():
                    if help_option.startswith(option.split('=')[0] + '='):
                        evaluated_option.help = help_string
                        break

            evaluated_options.append(evaluated_option)

    print()

    for option in sorted([x for x in evaluated_options if not x.error], key=lambda x: x.option):
        print(option)

    print()

    for option in sorted([x for x in evaluated_options if x.error], key=lambda x: x.option):
        print(option)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect GCC C++ warning options.')
    parser.add_argument('BINARY', help='path to the g++ binary (default: g++)',
                        default='g++', type=str, nargs='?')

    args = parser.parse_args()

    process(args.BINARY)
