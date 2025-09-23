from __future__ import annotations
from typing import Optional, Any
from dataclasses import dataclass

from .backends.base import Backend
from .backends.openai_backend import OpenAIBackend
from .backends.hf_backend import HFLocalBackend

@dataclass
class ClientConfig:
    backend: str = "openai"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    organization: Optional[str] = None
    project: Optional[str] = None
    model: Optional[str] = None # NOTE needed for HFLocal HFClient 

class Client:
    """
    Provider-agnostic façade exposing:
      - client.responses.create(...)
      - client.chat.completions.create(...)
    """

    # populated after backend selection
    responses: Any
    chat: Any

    def __init__(self, *, backend: str = "openai", **kwargs: Any) -> None:
        cfg = ClientConfig(backend=backend, **kwargs)
        self._cfg = cfg

        if cfg.backend == "openai":
            self._backend: Backend = OpenAIBackend(
                api_key=cfg.api_key,
                base_url=cfg.base_url,
                organization=cfg.organization,
                project=cfg.project,
            )
            self.responses = self._backend.responses
            self.chat = self._backend.chat
        elif cfg.backend == "hflocal": 
            self._backend = HFLocalBackend(
                model = cfg.model,
            )
        else:
            raise ValueError(f"Unsupported backend: {cfg.backend!r}")
        # TODO: note that witin each backend we are remapping the method
        # access up from the backend to the self. we need to normalize 
        # these other simply get the HFFace Local and Infereclient up 
        # to the OpenAI standard. 


        self.text_generation = self._backend.text_generation

    @property
    def config(self) -> ClientConfig:
        return self._cfg

    def __repr__(self) -> str:
        redacted = "***" if self._cfg.api_key else None
        return f"Client(backend={self._cfg.backend!r}, base_url={self._cfg.base_url!r}, api_key={redacted})"

