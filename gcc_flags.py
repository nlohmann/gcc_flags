import argparse
import re
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple

from termcolor import colored


# TODO: Help for -Wstringop-overflow is not properly collected.


def get_help_strings(binary: str) -> Dict[str, str]:
    # collect all warnings from g++
    proc = subprocess.Popen([binary, '--help=warnings'],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    proc.wait()
    output = proc.stdout.read().decode('utf-8')

    result = dict()  # type: Dict[str, str]

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
    tmpdir = tempfile.TemporaryDirectory()
    proc = subprocess.Popen([binary, '-x', 'c++'] + options + ['-'],
                            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, cwd=tmpdir.name)
    proc.stdin.write('int main() {}\n'.encode('utf-8'))
    proc.stdin.close()
    proc.wait()

    error_output = proc.stderr.read().decode('utf-8').strip()
    return proc.returncode, error_output


def get_all_options(binary: str) -> List[str]:
    # collect all warnings from g++
    proc = subprocess.Popen([binary, '-Q', '--help=warnings'],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    proc.wait()
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
        self.option = ''   # type: str
        self.help = ''     # type: str
        self.error = None  # type: Optional[str]

    def __repr__(self):
        result = '{option:50} {help}'.format(option=self.option, help=self.help)

        if self.error:
            result += '\n ' + self.error

        return result


def process(binary: str):
    help_strings = get_help_strings(binary)
    all_options = get_all_options(binary)
    max_option_len = max([len(option) for option in all_options])

    evaluated_options = []  # type: List[EvaluatedOption]
    todo_options = list(sorted(all_options))
    total_options = len(all_options)

    while len(todo_options) > 0:
        option = todo_options.pop(0)

        print('[{progress:3.0f}%] {option:<{max_option_len}} '.format(
            progress=(total_options-len(todo_options))/total_options*100, option=option, max_option_len=max_option_len
        ), end='', flush=True)

        # remove redundant options
        m = re.findall(r"Same as '?(-[^ ']+)", help_strings.get(option, ''))
        if len(m):
            if '=' in m[0]:
                print(colored('✘ duplicate of {option}'.format(option=m[0]), 'blue'))
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
                print(colored('✘ {error_msg}'.format(error_msg=error_msg), 'red'))
                continue

            # check if option requires another option to be given
            m = re.findall(r"ignored without '?(-[^ ']+)", error_output)
            if len(m):
                # add required option to list of options to check
                todo_options.insert(0, m[0] + ' ' + option)
                print(colored('? depends on {option}; trying next'.format(option=m[0]), 'yellow'))
                continue

            # use value ranges and lists
            m = re.findall(r'=[<\[]([^>\]]+)[>\]]', option)
            if len(m):
                base, _ = option.split('=')

                # value range (take upper bound)
                if ',' in m[0]:
                    _, upper = m[0].split(',')
                    todo_options.insert(0, base + '=' + upper)
                    print(colored('? expects argument from <{values}>; trying next'.format(values=m[0]), 'yellow'))
                    continue

                # value list (take last element)
                if '|' in m[0]:
                    todo_options.insert(0, base + '=' + m[0].split('|')[-1])
                    print(colored('? expects argument from [{values}]; trying next'.format(values=m[0]), 'yellow'))
                    continue

            print(colored('✘ error', 'red'))

            # create entry for failed option
            ec = EvaluatedOption()
            ec.option = option
            ec.help = help_strings.get(option, '')
            ec.error = error_output
            evaluated_options.append(ec)

        else:
            print(colored('✔ works', 'green'))

            ec = EvaluatedOption()
            ec.option = option

            # if multiple options are given, use the last one to look up the help string
            option_list = option.split()
            if len(option_list) > 1:
                ec.help = help_strings.get(option_list[-1])
            else:
                ec.help = help_strings.get(option)

            # if the option contains a =, we need to put more effort into looking up the help string
            if '=' in option:
                for help_option, help_string in help_strings.items():
                    if help_option.startswith(option.split('=')[0] + '='):
                        ec.help = help_string
                        break

            evaluated_options.append(ec)

    print()

    for o in sorted([x for x in evaluated_options if x.error is None], key=lambda x: x.option):
        print(o)

    print()

    for o in sorted([x for x in evaluated_options if x.error is not None], key=lambda x: x.option):
        print(o)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect GCC C++ warning options.')
    parser.add_argument('BINARY', help='path to the g++ binary (default: g++)', default='g++', type=str, nargs='?')

    args = parser.parse_args()

    process(args.BINARY)
