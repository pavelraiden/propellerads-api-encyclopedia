"""PropellerAds API exceptions with detailed error handling"""

from typing import Optional, Dict, Any


class PropellerAdsError(Exception):
    """Base exception for PropellerAds API errors"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.endpoint = endpoint
        self.method = method
        super().__init__(self.message)
    
    def __str__(self) -> str:
        error_parts = [self.message]
        
        if self.status_code:
            error_parts.append(f"Status: {self.status_code}")
        
        if self.endpoint:
            error_parts.append(f"Endpoint: {self.endpoint}")
        
        if self.method:
            error_parts.append(f"Method: {self.method}")
        
        return " | ".join(error_parts)


class AuthenticationError(PropellerAdsError):
    """Authentication failed - invalid API token"""
    
    def __init__(self, message: str = "Invalid API token", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(PropellerAdsError):
    """Authorization failed - insufficient permissions"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class ValidationError(PropellerAdsError):
    """Request validation failed"""
    
    def __init__(self, message: str = "Request validation failed", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class NotFoundError(PropellerAdsError):
    """Resource not found"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class RateLimitError(PropellerAdsError):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, status_code=429, **kwargs)


class ServerError(PropellerAdsError):
    """Server-side error"""
    
    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class TimeoutError(PropellerAdsError):
    """Request timeout"""
    
    def __init__(self, message: str = "Request timeout", **kwargs):
        super().__init__(message, status_code=408, **kwargs)


class CampaignError(PropellerAdsError):
    """Campaign-specific errors"""
    pass


class StatisticsError(PropellerAdsError):
    """Statistics-specific errors"""
    pass


class TargetingError(PropellerAdsError):
    """Targeting-specific errors"""
    pass


def create_error_from_response(
    status_code: int,
    response_data: Any,
    endpoint: str = None,
    method: str = None
) -> PropellerAdsError:
    """Create appropriate exception from API response"""
    
    # Extract error message
    if isinstance(response_data, dict):
        if 'errors' in response_data:
            if isinstance(response_data['errors'], list):
                message = '; '.join(str(err) for err in response_data['errors'])
            else:
                message = str(response_data['errors'])
        elif 'error' in response_data:
            message = str(response_data['error'])
        elif 'message' in response_data:
            message = str(response_data['message'])
        else:
            message = str(response_data)
    else:
        message = str(response_data)
    
    # Create specific exception based on status code
    error_kwargs = {
        'details': response_data if isinstance(response_data, dict) else {},
        'endpoint': endpoint,
        'method': method
    }
    
    if status_code == 400:
        return ValidationError(message, **error_kwargs)
    elif status_code == 401:
        return AuthenticationError(message, **error_kwargs)
    elif status_code == 403:
        return AuthorizationError(message, **error_kwargs)
    elif status_code == 404:
        return NotFoundError(message, **error_kwargs)
    elif status_code == 408:
        return TimeoutError(message, **error_kwargs)
    elif status_code == 429:
        return RateLimitError(message, **error_kwargs)
    elif status_code >= 500:
        return ServerError(message, **error_kwargs)
    else:
        return PropellerAdsError(message, status_code=status_code, **error_kwargs)


# Error code mappings for better error messages
ERROR_CODE_MESSAGES = {
    400: "Bad Request - Check your request parameters",
    401: "Unauthorized - Invalid API token",
    403: "Forbidden - Insufficient permissions or token limitations",
    404: "Not Found - Endpoint or resource doesn't exist",
    408: "Request Timeout - Request took too long to complete",
    429: "Too Many Requests - Rate limit exceeded",
    500: "Internal Server Error - PropellerAds server issue",
    502: "Bad Gateway - PropellerAds server temporarily unavailable",
    503: "Service Unavailable - PropellerAds API maintenance",
    504: "Gateway Timeout - PropellerAds server timeout"
}


def get_error_message(status_code: int) -> str:
    """Get user-friendly error message for status code"""
    return ERROR_CODE_MESSAGES.get(status_code, f"HTTP Error {status_code}")


# Common error scenarios and solutions
ERROR_SOLUTIONS = {
    400: [
        "Check required parameters are provided",
        "Validate date formats (YYYY-MM-DD HH:MM:SS)",
        "Ensure numeric values are within valid ranges",
        "Verify enum values match API specification"
    ],
    401: [
        "Verify API token is correct",
        "Check token hasn't expired",
        "Ensure Bearer token format: 'Bearer YOUR_TOKEN'"
    ],
    403: [
        "Check API token permissions",
        "Verify account has access to requested features",
        "Contact PropellerAds support for permission issues"
    ],
    404: [
        "Verify endpoint URL is correct",
        "Check resource ID exists",
        "Ensure API version is supported"
    ],
    429: [
        "Implement exponential backoff retry logic",
        "Reduce request frequency",
        "Contact support for rate limit increase"
    ],
    500: [
        "Retry request after delay",
        "Check PropellerAds status page",
        "Contact PropellerAds support if persistent"
    ]
}


def get_error_solutions(status_code: int) -> list:
    """Get suggested solutions for error"""
    return ERROR_SOLUTIONS.get(status_code, ["Contact PropellerAds support"])
