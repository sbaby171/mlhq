from .client import Client, ClientConfig
from .types import MLHQResponse
from .logging_config import setup_logging, get_logger

__all__ = ["Client", "ClientConfig", "MLHQResponse", "__version__", "hello", 'setup_logging', 'get_logger']

__version__ = "0.1.0"

def hello(name: str = "world") -> str:
    return f"hello, {name}"


