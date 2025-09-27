from __future__ import annotations
from typing import Optional, Any
from dataclasses import dataclass
import json 

from .backends.base import Backend
from .backends.openai_backend import OpenAIBackend
from .backends.hf_backend import HFLocalBackend

from mlhq.logging_config import get_logger
logger = get_logger(__name__)

@dataclass
class ClientConfig:

    def __init__(self, config=None,
            backend: str = "openai",
            api_key: Optional[str] = None, 
            base_url: Optional[str] = None,
            organization: Optional[str] = None,
            project: Optional[str] = None,
            model: Optional[str] = None # NOTE needed for HFLocal HFClient 
        ): 
        config_data = {} 
        if config: 
            with open(config, 'r') as f:
                config_data = json.load(f)
            logger.debug(f"Config fields: {config_data}")

        for k,v in config_data.items(): 
            self.__dict__[k] = v 
       
        if "api_key" not in self.__dict__: 
            self.api_key = "abc123"

class Client:
    """
    Provider-agnostic façade exposing:
      - client.responses.create(...)
      - client.chat.completions.create(...)
    """

    # populated after backend selection
    responses: Any
    chat: Any

    def __init__(self, **kwargs):
        logger.info(f"Initializing MLHQ Client : {kwargs}")

        cfg = ClientConfig(**kwargs)

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

