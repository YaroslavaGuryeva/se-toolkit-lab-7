"""LLM client with tool calling support.

Handles communication with the LLM API for intent recognition.
"""
import json
import sys
from typing import Any

import httpx
from config import get_settings


class LLMClient:
    """Client for LLM API with tool calling support.
    
    Uses OpenAI-compatible API format (works with Qwen Code proxy).
    """
    
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.llm_api_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model
        self._client: httpx.Client | None = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create the HTTP client with auth headers."""
        if self._client is None:
            # Ensure URL has scheme
            url = self.base_url
            if not url.startswith('http://') and not url.startswith('https://'):
                url = f'http://{url}'
            self._client = httpx.Client(
                base_url=url.rstrip('/'),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client
    
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat request to the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            
        Returns:
            Response dict with 'content' and/or 'tool_calls'
        """
        try:
            client = self._get_client()
            
            payload: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
            }
            
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"
            
            response = client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            choice = data["choices"][0]["message"]
            
            result = {
                "content": choice.get("content", ""),
                "tool_calls": [],
            }
            
            # Parse tool calls if present
            if "tool_calls" in choice and choice["tool_calls"]:
                for tc in choice["tool_calls"]:
                    if tc["type"] == "function":
                        result["tool_calls"].append({
                            "id": tc["id"],
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                        })
            
            return result
            
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except httpx.HTTPError as e:
            return {"error": f"HTTP error: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode error: {str(e)}"}
        except Exception as e:
            return {"error": f"LLM error: {str(e)}"}


# Global client instance
_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client, creating it if necessary."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
