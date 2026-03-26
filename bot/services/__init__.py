"""Services for the LMS bot.

Services handle external dependencies (APIs, databases, etc.).
"""

from .lms_api import get_lms_client, LMSAPIClient

__all__ = [
    'get_lms_client',
    'LMSAPIClient',
]
