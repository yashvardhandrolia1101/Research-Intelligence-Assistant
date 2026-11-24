import json
import requests
from typing import Optional, Dict, Any, Tuple

try:
    from settings import (
        DEFAULT_AI_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL,
        OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
    )
except ImportError:
    from settings import (
        DEFAULT_AI_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL,
        OPENAI_API_KEY, OPENAI_MODEL
    )
    OPENAI_BASE_URL = "https://api.groq.com/openai/v1"

from exceptions import AIProviderError


class AIProvider:
    _runtime_config: Dict[str, Any] = {
        "provider": DEFAULT_AI_PROVIDER,
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "openai_key": OPENAI_API_KEY,
        "openai_base_url": OPENAI_BASE_URL or "https://api.groq.com/openai/v1",
        "openai_model": OPENAI_MODEL,
        "temperature": 0.2,
    }

    @classmethod
    def configure(
        cls,
        provider: Optional[str] = None,
        ollama_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        openai_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        openai_model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        if provider is not None:
            cls._runtime_config["provider"] = provider
        if ollama_url is not None:
            cls._runtime_config["ollama_url"] = ollama_url.rstrip("/")
        if ollama_model is not None:
            cls._runtime_config["ollama_model"] = ollama_model
        if openai_key is not None:
            cls._runtime_config["openai_key"] = openai_key
        if openai_base_url is not None:
            cls._runtime_config["openai_base_url"] = openai_base_url.rstrip("/")
        if openai_model is not None:
            cls._runtime_config["openai_model"] = openai_model
        if temperature is not None:
            cls._runtime_config["temperature"] = temperature

    @classmethod
    def get_status(cls) -> Tuple[bool, str]:
        provider = cls._runtime_config["provider"]
        if provider == "ollama":
            try:
                resp = requests.get(f"{cls._runtime_config['ollama_url']}/api/tags", timeout=3)
                if resp.status_code == 200:
                    models = [m.get("name", "") for m in resp.json().get("models", [])]
                    return True, f"Ollama Connected ({len(models)} local models available)"
                return False, f"Ollama returned HTTP {resp.status_code}"
            except Exception:
                return False, "Ollama offline (start with 'ollama serve' or switch to OpenAI in Settings)"
        elif provider == "openai":
            if cls._runtime_config["openai_key"]:
                return True, f"OpenAI Configured ({cls._runtime_config['openai_model']})"
            return False, "OpenAI API Key missing"
        return False, "Unknown provider"

    @classmethod
    def generate(cls, prompt: str, system_prompt: str = "You are a scientific research intelligence assistant.") -> str:
        provider = cls._runtime_config["provider"]
        if provider == "ollama":
            return cls._call_ollama(prompt, system_prompt)
        elif provider == "openai":
            return cls._call_openai(prompt, system_prompt)
        raise AIProviderError(f"Unsupported AI provider: {provider}")

    @classmethod
    def _call_ollama(cls, prompt: str, system_prompt: str) -> str:
        url = f"{cls._runtime_config['ollama_url']}/api/generate"
        payload = {
            "model": cls._runtime_config["ollama_model"],
            "system": system_prompt,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": cls._runtime_config["temperature"]}
        }
        try:
            response = requests.post(url, json=payload, timeout=90)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
            raise AIProviderError(
                f"Local Ollama model '{cls._runtime_config['ollama_model']}' is unavailable at "
                f"{cls._runtime_config['ollama_url']}. Ensure Ollama is running or configure a cloud provider in Settings. ({str(e)})"
            )

    @classmethod
    def _call_openai(cls, prompt: str, system_prompt: str) -> str:
        api_key = cls._runtime_config["openai_key"]
        if not api_key:
            raise AIProviderError("OpenAI API key is not configured. Add it in Settings or .env.")
        base_url = (cls._runtime_config.get("openai_base_url") or "https://api.groq.com/openai/v1").rstrip("/")
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": cls._runtime_config["openai_model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": cls._runtime_config["temperature"]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            raise AIProviderError(f"OpenAI API request failed: {str(e)}")
