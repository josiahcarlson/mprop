
import mprop

@property
def test_read(mod):
    return "got read"

value = None

@test_read.setter
def test_read(mod, value):
    mod.value = value


def test_no_mod():
    return "I work too"

mprop.init()
