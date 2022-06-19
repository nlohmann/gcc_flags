import subprocess

def call(args):
    try:
        result = subprocess.run(['gcc_flags'] + args, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as error:
        print(error.stdout)
        print(error.stderr)
        raise error


def test_help():
    result = call(['--help'])
    assert result.stdout == '''usage: gcc_flags [-h] [--json] [--version] [BINARY]

Collect GCC C++ warning options.

positional arguments:
  BINARY      path to the g++ binary (default: g++)

optional arguments:
  -h, --help  show this help message and exit
  --json      create JSON output for flags
  --version   show program's version number and exit
'''

def test_version():
    result = call(['--version'])
    assert result.stdout == '''gcc_flags 0.1.1
'''
