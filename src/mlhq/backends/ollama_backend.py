from __future__ import annotations
from typing import Any, Optional, Dict
import ollama
from .base import Backend, ResponsesAPI, ChatAPI, ChatCompletionsAPI
from ..types import MLHQResponse

# ---------- helpers to normalize Ollama payloads ----------

def _extract_ollama_chat_text(obj: Any) -> str:
    """
    Ollama chat response structure:
      response['message']['content']
    """
    # Dict-like access (most common)
    if isinstance(obj, dict):
        # Standard chat response
        if "message" in obj:
            msg = obj["message"]
            if isinstance(msg, dict) and "content" in msg:
                return msg["content"] or ""
        # Direct content field (some responses)
        if "content" in obj:
            return obj["content"] or ""
        # Response field (generate API)
        if "response" in obj:
            return obj["response"] or ""
    
    # Object attribute access
    msg = getattr(obj, "message", None)
    if msg is not None:
        content = getattr(msg, "content", None)
        if isinstance(content, str):
            return content
    
    # Direct content attribute
    content = getattr(obj, "content", None)
    if isinstance(content, str):
        return content
    
    # Response attribute (for generate)
    response = getattr(obj, "response", None)
    if isinstance(response, str):
        return response
    
    return ""

def _extract_ollama_generate_text(obj: Any) -> str:
    """
    Ollama generate response structure:
      response['response']
    """
    # Dict-like access
    if isinstance(obj, dict):
        if "response" in obj:
            return obj["response"] or ""
    
    # Object attribute access
    response = getattr(obj, "response", None)
    if isinstance(response, str):
        return response
    
    return ""

def _extract_ollama_common(obj: Any) -> Dict[str, Any]:
    """
    Extract model, finish_reason (done_reason in Ollama), and usage info.
    """
    model = None
    finish_reason = None
    usage = None
    
    if isinstance(obj, dict):
        model = obj.get("model")
        
        # Ollama uses 'done' boolean and 'done_reason'
        if obj.get("done"):
            finish_reason = obj.get("done_reason", "stop")
        
        # Usage/token info - Ollama provides these at top level
        usage_fields = {}
        for key in ("prompt_eval_count", "eval_count", "total_duration", 
                    "load_duration", "prompt_eval_duration", "eval_duration"):
            if key in obj:
                usage_fields[key] = obj[key]
        
        if usage_fields:
            usage = usage_fields
    else:
        # Object attribute access
        model = getattr(obj, "model", None)
        
        done = getattr(obj, "done", None)
        if done:
            finish_reason = getattr(obj, "done_reason", "stop")
        
        # Collect usage fields
        usage_fields = {}
        for key in ("prompt_eval_count", "eval_count", "total_duration",
                    "load_duration", "prompt_eval_duration", "eval_duration"):
            val = getattr(obj, key, None)
            if val is not None:
                usage_fields[key] = val
        
        if usage_fields:
            usage = usage_fields
    
    return {"model": model, "finish_reason": finish_reason, "usage": usage}

# ---------- adapters ----------

class _OllamaGenerate(ResponsesAPI):
    """
    Maps to Ollama's generate() method (similar to OpenAI's responses API).
    """
    def __init__(self, client: ollama.Client):
        self._client = client
    
    def create(self, **kwargs: Any) -> MLHQResponse:
        # Ollama uses 'prompt' instead of 'input'
        if "input" in kwargs and "prompt" not in kwargs:
            kwargs["prompt"] = kwargs.pop("input")
        
        raw = self._client.generate(**kwargs)
        text = _extract_ollama_generate_text(raw)
        meta = _extract_ollama_common(raw)
        
        return MLHQResponse(
            text=text,
            raw=raw,
            model=meta["model"],
            provider="ollama",
            finish_reason=meta["finish_reason"],
            usage=meta["usage"],
        )

class _OllamaChatCompletions(ChatCompletionsAPI):
    """
    Maps to Ollama's chat() method.
    """
    def __init__(self, client: ollama.Client):
        self._client = client
    
    def create(self, **kwargs: Any) -> MLHQResponse:
        print(f"kwargs = {type(kwargs)}")
        print(f"kwargs = {kwargs}")
        options = {} 
        messages = []
        model = ""
        tools = []
        if "max_new_tokens" in kwargs: 
            options["num_predict"] = kwargs["max_new_tokens"]
        if "messages" in kwargs: 
            messages  = kwargs["messages"]
        if "model" in kwargs: 
            model = kwargs["model"]
        if "tools" in kwargs: 
            tools = kwargs["tools"]
        print(f"DEBUG: model = {model}")
        print(f"DEBUG: messages = {messages}")
        print(f"DEBUG: tools = {tools}")
        print(f"DEBUG: options = {options}")

        try:
            #raw = self._client.chat(**kwargs)
            raw = self._client.chat(model = model, messages=messages, options=options, tools=tools)
            #raw = self._client.chat(options = kwargs)
        except Exception as e: 
            raise RuntimeError(f"{e}")
        text = _extract_ollama_chat_text(raw)
        meta = _extract_ollama_common(raw)
        
        return MLHQResponse(
            text=text,
            raw=raw,
            model=meta["model"],
            provider="ollama",
            finish_reason=meta["finish_reason"],
            usage=meta["usage"],
        )

class _OllamaChat(ChatAPI):
    def __init__(self, client: ollama.Client):
        self._completions = _OllamaChatCompletions(client)
    
    @property
    def completions(self) -> ChatCompletionsAPI:
        return self._completions

class OllamaBackend(Backend):
    """
    Backend implementation for Ollama.
    
    Usage:
        backend = OllamaBackend(host="http://localhost:11434")
        
        # Chat completions
        response = backend.chat.completions.create(
            model="llama2",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        
        # Generate (responses API equivalent)
        response = backend.responses.create(
            model="llama2",
            prompt="Hello!"  # or use 'input' which gets converted to 'prompt'
        )
    """
    def __init__(
        self,
        *,
        host: Optional[str] = None,
        timeout: Optional[float] = None,
        **extra: Any,
    ) -> None:
        """
        Initialize Ollama backend.
        
        Args:
            host: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
            **extra: Additional arguments (currently unused, for future compatibility)
        """
        client_kwargs = {}
        if host is not None:
            client_kwargs["host"] = host
        if timeout is not None:
            client_kwargs["timeout"] = timeout
        
        self._inner = ollama.Client(**client_kwargs)
        self._responses = _OllamaGenerate(self._inner)
        self._chat = _OllamaChat(self._inner)
    
    @property
    def responses(self) -> ResponsesAPI:
        """Access to Ollama's generate API (mapped as responses)."""
        return self._responses
    
    @property
    def chat(self) -> ChatAPI:
        """Access to Ollama's chat API."""
        return self._chat
