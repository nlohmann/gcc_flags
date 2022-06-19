import gcc_flags

def test_process():
    res = gcc_flags.process('g++')
    assert len(res) > 0

    s = str(res[0])
    assert len(s) > 0

    j = dict(res[0])
    assert 'flag' in j.keys()
    assert 'help' in j.keys()
    assert 'error' in j.keys()
