from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict

@dataclass
class ClientConfig:
    api_key: Optional[str] = None
    endpoint: str = "https://api.example.com"
    timeout: float = 30.0

class Client:
    """
    Core MLHQ client.

    Example:
        from mlhq import Client
        client = Client(api_key="secret")
        data = client.ping()
    """

    def __init__(self, api_key: Optional[str] = None, *, endpoint: str | None = None, timeout: float | None = None):
        cfg = ClientConfig(api_key=api_key)
        if endpoint is not None:
            cfg.endpoint = endpoint
        if timeout is not None:
            cfg.timeout = timeout
        self._cfg = cfg
        # set up any session/resources here, e.g. requests.Session()

    @property
    def config(self) -> ClientConfig:
        return self._cfg

    def ping(self) -> Dict[str, Any]:
        # Replace with real health-check / version call later
        return {
            "ok": True,
            "endpoint": self._cfg.endpoint,
            "timeout": self._cfg.timeout,
            "using_key": bool(self._cfg.api_key),
        }

    def close(self) -> None:
        # clean up sessions/resources
        pass

    # Convenience: allow `with Client(...) as c: ...`
    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Client(endpoint={self._cfg.endpoint!r}, timeout={self._cfg.timeout!r}, api_key={'***' if self._cfg.api_key else None})"

