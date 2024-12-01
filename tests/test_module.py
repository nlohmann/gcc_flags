import gcc_flags


def test_process():
    res = gcc_flags.process("g++")
    assert len(res) > 0

    s = "\n".join([str(x) for x in res])
    assert len(s) > 0

    array = [dict(x) for x in res]
    for el in array:
        assert "flag" in el.keys()
        assert "help" in el.keys()
        assert "error" in el.keys()
