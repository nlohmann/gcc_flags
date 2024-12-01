import subprocess


def call(args):
    return subprocess.run(["gcc_flags"] + args, check=True, capture_output=True, text=True)


def test_help():
    result = call(["--help"])
    assert "Collect GCC C++ warning options." in result.stdout


def test_version():
    result = call(["--version"])
    assert "gcc_flags" in result.stdout
