"""LMS API client.

Handles all HTTP calls to the LMS backend with proper error handling.
"""
import httpx
from config import get_settings


class LMSAPIClient:
    """Client for the LMS backend API.
    
    All methods return either:
    - A successful result (dict, list, etc.)
    - An error tuple: (False, error_message)
    """
    
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key
        self._client: httpx.Client | None = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create the HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client
    
    def get_items(self) -> dict | tuple[bool, str]:
        """GET /items/ — returns labs and tasks.
        
        Returns:
            dict with items on success, or (False, error_message) on failure.
        """
        try:
            client = self._get_client()
            response = client.get("/items/")
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            return (False, f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPStatusError as e:
            return (False, f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.HTTPError as e:
            return (False, f"HTTP error: {str(e)}")
    
    def get_pass_rates(self, lab: str) -> dict | tuple[bool, str]:
        """GET /analytics/pass-rates?lab=<lab> — returns per-task pass rates.
        
        Args:
            lab: The lab identifier (e.g., 'lab-04')
            
        Returns:
            dict with pass rates on success, or (False, error_message) on failure.
        """
        try:
            client = self._get_client()
            response = client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            return (False, f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPStatusError as e:
            return (False, f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.HTTPError as e:
            return (False, f"HTTP error: {str(e)}")


# Global client instance
_client: LMSAPIClient | None = None


def get_lms_client() -> LMSAPIClient:
    """Get the global LMS API client, creating it if necessary."""
    global _client
    if _client is None:
        _client = LMSAPIClient()
    return _client
