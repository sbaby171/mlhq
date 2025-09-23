from __future__ import annotations
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Optional, List

@dataclass
class MLHQResponse:
    text: str
    raw: Any
    model: Optional[str] = None
    provider: Optional[str] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None

    # --- OpenAI-ish aliases (so old code keeps working) ---
    @property
    def output_text(self) -> str:
        """Alias used by OpenAI Responses API examples."""
        return self.text

    @property
    def content(self) -> str:
        """Handy alias; some libs expose .content as string."""
        return self.text

    @property
    def message(self) -> Dict[str, str]:
        """
        Minimal chat-like message object.
        OpenAI examples often do: completion.choices[0].message
        """
        return {"role": "assistant", "content": self.text}

    @property
    def choices(self) -> List[Any]:
        """
        Provide a minimal .choices[0].message shim to match
        OpenAI chat/completions examples.
        """
        msg = SimpleNamespace(role="assistant", content=self.text)
        choice = SimpleNamespace(message=msg, finish_reason=self.finish_reason)
        return [choice]

    # --- niceties ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "raw": self.raw,
            "model": self.model,
            "provider": self.provider,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
        }

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        prov = f"{self.provider}:" if self.provider else ""
        mdl = f" model={self.model!r}" if self.model else ""
        return f"<MLHQResponse {prov}{self.text[:60]!r}{'…' if len(self.text)>60 else ''}{mdl}>"

    # --- graceful passthrough for uncommon attrs ---
    def __getattr__(self, name: str) -> Any:
        """
        If a caller requests an attribute that exists on the raw provider
        object (e.g., id, created), fall back to it. This keeps us flexible
        without polluting the primary surface.
        """
        raw = object.__getattribute__(self, "raw")
        if hasattr(raw, name):
            return getattr(raw, name)
        raise AttributeError(f"{type(self).__name__!s} object has no attribute {name!r}")

