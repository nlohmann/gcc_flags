import gcc_flags

def test_process():
    res = gcc_flags.process('g++')
    assert len(res) > 0
