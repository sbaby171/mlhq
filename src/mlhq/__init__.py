from .client import Client

__all__ = ["Client", "__version__", "hello"]

__version__ = "0.1.0"

def hello(name: str = "world") -> str:
    return f"hello, {name}"


