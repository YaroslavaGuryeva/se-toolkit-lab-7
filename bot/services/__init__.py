"""Services for the LMS bot.

Services handle external dependencies (APIs, databases, etc.).
"""

from .lms_api import get_lms_client, LMSAPIClient
from .llm_client import get_llm_client, LLMClient

__all__ = [
    'get_lms_client',
    'LMSAPIClient',
    'get_llm_client',
    'LLMClient',
]
