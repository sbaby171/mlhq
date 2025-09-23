from mlhq.core import get_version
from mlhq import __version__, hello

def test_version_roundtrip():
    assert get_version() == __version__

def test_hello_default():
    assert hello() == "hello, world"

def test_hello_custom():
    assert hello("Max") == "hello, Max"

