from __future__ import annotations
from typing import Protocol, Any
from ..types import MLHQResponse

# ----- responses -----
class ResponsesAPI(Protocol):
    def create(self, **kwargs: Any) -> MLHQResponse: ...

# ----- chat.completions -----
class ChatCompletionsAPI(Protocol):
    def create(self, **kwargs: Any) -> MLHQResponse: ...

class ChatAPI(Protocol):
    @property
    def completions(self) -> ChatCompletionsAPI: ...

# ----- backend -----
class Backend(Protocol):
    @property
    def responses(self) -> ResponsesAPI: ...
    @property
    def chat(self) -> ChatAPI: ...

