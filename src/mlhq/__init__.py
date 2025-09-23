from .client import Client, ClientConfig
from .types import MLHQResponse

__all__ = ["Client", "ClientConfig", "MLHQResponse", "__version__", "hello"]

__version__ = "0.1.0"

def hello(name: str = "world") -> str:
    return f"hello, {name}"


