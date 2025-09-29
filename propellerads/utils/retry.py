"""Retry utilities."""
from dataclasses import dataclass

@dataclass
class RetryConfig:
    max_retries: int = 3
    backoff_factor: float = 2.0

def create_retry_session():
    """Create session with retry logic."""
    import requests
    return requests.Session()
