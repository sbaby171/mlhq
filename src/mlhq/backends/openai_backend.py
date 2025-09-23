from __future__ import annotations
from typing import Any, Optional, Dict
from openai import OpenAI
from .base import Backend, ResponsesAPI, ChatAPI, ChatCompletionsAPI
from ..types import MLHQResponse

# ---------- helpers to normalize OpenAI payloads ----------

def _extract_openai_responses_text(obj: Any) -> str:
    """
    OpenAI Responses API typically exposes `response.output_text`.
    Fallbacks included if structure differs.
    """
    # 1) official property
    text = getattr(obj, "output_text", None)
    if isinstance(text, str) and text:
        return text

    # 2) common fallbacks
    # Some SDK objects have .output or .data
    for attr in ("output", "data", "content", "text"):
        val = getattr(obj, attr, None)
        if isinstance(val, str) and val:
            return val

    # 3) try dict-like
    if isinstance(obj, dict):
        for key in ("output_text", "output", "text"):
            if key in obj and isinstance(obj[key], str):
                return obj[key]

    # last resort
    return ""

def _extract_openai_chat_text(obj: Any) -> str:
    """
    OpenAI Chat Completions shape (python client):
      completion.choices[0].message.content  (or .message for legacy)
    """
    # SDK object with attributes
    choices = getattr(obj, "choices", None)
    if choices and len(choices) > 0:
        msg = getattr(choices[0], "message", None) or getattr(choices[0], "delta", None)
        if msg is not None:
            # message.content can be str or a structured content list; keep the simple case
            content = getattr(msg, "content", None) or getattr(msg, "text", None)
            if isinstance(content, str):
                return content
            # dict fallback
            if isinstance(content, dict) and "content" in content and isinstance(content["content"], str):
                return content["content"]

    # dict-like fallback
    if isinstance(obj, dict):
        try:
            return obj["choices"][0]["message"].get("content") or ""
        except Exception:
            return ""

    return ""

def _extract_openai_common(obj: Any) -> Dict[str, Any]:
    """
    Pull out model, finish_reason, usage if available.
    """
    model = getattr(obj, "model", None)
    finish_reason = None
    usage = None

    # finish_reason via choices[0].finish_reason
    choices = getattr(obj, "choices", None)
    if choices and len(choices) > 0:
        finish_reason = getattr(choices[0], "finish_reason", None) or (
            isinstance(choices[0], dict) and choices[0].get("finish_reason")
        )

    # usage (tokens)
    usage_attr = getattr(obj, "usage", None)
    if usage_attr is not None:
        # Convert SDK model to plain dict if needed
        if hasattr(usage_attr, "dict"):
            try:
                usage = usage_attr.dict()
            except Exception:
                usage = dict(usage_attr)  # type: ignore
        else:
            try:
                usage = dict(usage_attr)  # may work if it's Mapping
            except Exception:
                usage = getattr(usage_attr, "__dict__", None)

    # dict-like fallbacks
    if model is None and isinstance(obj, dict):
        model = obj.get("model")
        if finish_reason is None:
            try:
                finish_reason = obj["choices"][0].get("finish_reason")
            except Exception:
                pass
        if usage is None and "usage" in obj:
            usage = obj["usage"]

    return {"model": model, "finish_reason": finish_reason, "usage": usage}

# ---------- adapters ----------

class _OpenAIResponses(ResponsesAPI):
    def __init__(self, client: OpenAI): self._client = client
    def create(self, **kwargs: Any) -> MLHQResponse:
        raw = self._client.responses.create(**kwargs)
        text = _extract_openai_responses_text(raw)
        meta = _extract_openai_common(raw)
        return MLHQResponse(
            text=text,
            raw=raw,
            model=meta["model"],
            provider="openai",
            finish_reason=meta["finish_reason"],
            usage=meta["usage"],
        )

class _OpenAIChatCompletions(ChatCompletionsAPI):
    def __init__(self, client: OpenAI): self._client = client
    def create(self, **kwargs: Any) -> MLHQResponse:
        raw = self._client.chat.completions.create(**kwargs)
        text = _extract_openai_chat_text(raw)
        meta = _extract_openai_common(raw)
        return MLHQResponse(
            text=text,
            raw=raw,
            model=meta["model"],
            provider="openai",
            finish_reason=meta["finish_reason"],
            usage=meta["usage"],
        )

class _OpenAIChat(ChatAPI):
    def __init__(self, client: OpenAI):
        self._completions = _OpenAIChatCompletions(client)
    @property
    def completions(self) -> ChatCompletionsAPI:
        return self._completions

class OpenAIBackend(Backend):
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        **extra: Any,
    ) -> None:
        self._inner = OpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            project=project,
        )
        self._responses = _OpenAIResponses(self._inner)
        self._chat = _OpenAIChat(self._inner)

    @property
    def responses(self) -> ResponsesAPI:
        return self._responses

    @property
    def chat(self) -> ChatAPI:
        return self._chat

