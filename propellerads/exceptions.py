"""
PropellerAds API Exceptions

Custom exception classes for comprehensive error handling.
"""

from typing import Optional, Dict, Any


class PropellerAdsError(Exception):
    """
    Base exception for all PropellerAds API errors.
    
    Attributes:
        message: Error message
        status_code: HTTP status code (if applicable)
        response_data: Raw response data (if available)
        request_id: Request ID for tracking
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.request_id = request_id
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation with context."""
        parts = [self.message]
        
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        
        return " | ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'status_code': self.status_code,
            'request_id': self.request_id,
            'response_data': self.response_data
        }


class AuthenticationError(PropellerAdsError):
    """
    Authentication/authorization errors.
    
    Raised when:
    - Invalid API key
    - Expired token
    - Insufficient permissions
    """
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class ValidationError(PropellerAdsError):
    """
    Request validation errors.
    
    Raised when:
    - Invalid parameters
    - Missing required fields
    - Data format errors
    """
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        self.field = field
        
        if field:
            message = f"Validation error for '{field}': {message}"
        
        super().__init__(message, status_code=400, **kwargs)


class RateLimitError(PropellerAdsError):
    """
    Rate limiting errors.
    
    Raised when API rate limits are exceeded.
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        
        if retry_after:
            message = f"{message}. Retry after {retry_after} seconds."
        
        super().__init__(message, status_code=429, **kwargs)


class ServerError(PropellerAdsError):
    """
    Server-side errors.
    
    Raised when:
    - Internal server errors (5xx)
    - Service unavailable
    - Timeout errors
    """
    
    def __init__(self, message: str = "Server error", **kwargs):
        if 'status_code' not in kwargs:
            kwargs['status_code'] = 500
        
        super().__init__(message, **kwargs)


class NotFoundError(PropellerAdsError):
    """
    Resource not found errors.
    
    Raised when:
    - Campaign not found
    - Endpoint not found
    - Resource doesn't exist
    """
    
    def __init__(self, message: str = "Resource not found", resource_type: Optional[str] = None, **kwargs):
        self.resource_type = resource_type
        
        if resource_type:
            message = f"{resource_type} not found: {message}"
        
        super().__init__(message, status_code=404, **kwargs)


class ConflictError(PropellerAdsError):
    """
    Conflict errors.
    
    Raised when:
    - Resource already exists
    - Conflicting operations
    - State conflicts
    """
    
    def __init__(self, message: str = "Conflict error", **kwargs):
        super().__init__(message, status_code=409, **kwargs)


class CircuitBreakerError(PropellerAdsError):
    """
    Circuit breaker errors.
    
    Raised when circuit breaker is open due to too many failures.
    """
    
    def __init__(
        self,
        message: str = "Circuit breaker is open",
        failure_count: Optional[int] = None,
        reset_time: Optional[float] = None,
        **kwargs
    ):
        self.failure_count = failure_count
        self.reset_time = reset_time
        
        if failure_count:
            message = f"{message} (failures: {failure_count})"
        
        super().__init__(message, status_code=503, **kwargs)


class TimeoutError(PropellerAdsError):
    """
    Request timeout errors.
    
    Raised when requests exceed configured timeout.
    """
    
    def __init__(
        self,
        message: str = "Request timeout",
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        self.timeout_seconds = timeout_seconds
        
        if timeout_seconds:
            message = f"{message} after {timeout_seconds} seconds"
        
        super().__init__(message, status_code=408, **kwargs)


class ConnectionError(PropellerAdsError):
    """
    Connection errors.
    
    Raised when:
    - Network connectivity issues
    - DNS resolution failures
    - Connection refused
    """
    
    def __init__(self, message: str = "Connection error", **kwargs):
        super().__init__(message, status_code=503, **kwargs)


class ConfigurationError(PropellerAdsError):
    """
    Configuration errors.
    
    Raised when:
    - Invalid client configuration
    - Missing required settings
    - Incompatible options
    """
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        # Configuration errors don't have HTTP status codes
        super().__init__(message, **kwargs)


class DataError(PropellerAdsError):
    """
    Data processing errors.
    
    Raised when:
    - Response parsing fails
    - Data format is unexpected
    - Serialization errors
    """
    
    def __init__(self, message: str = "Data processing error", **kwargs):
        super().__init__(message, **kwargs)


# Exception mapping for HTTP status codes
STATUS_CODE_EXCEPTIONS = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}


def create_exception_from_response(
    status_code: int,
    message: str,
    response_data: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> PropellerAdsError:
    """
    Create appropriate exception based on HTTP status code.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response_data: Raw response data
        request_id: Request ID for tracking
        
    Returns:
        PropellerAdsError: Appropriate exception instance
    """
    exception_class = STATUS_CODE_EXCEPTIONS.get(status_code, PropellerAdsError)
    
    return exception_class(
        message=message,
        status_code=status_code,
        response_data=response_data,
        request_id=request_id
    )


def handle_api_error(
    response,
    request_id: Optional[str] = None
) -> None:
    """
    Handle API error response and raise appropriate exception.
    
    Args:
        response: HTTP response object
        request_id: Request ID for tracking
        
    Raises:
        PropellerAdsError: Appropriate exception based on response
    """
    try:
        error_data = response.json()
        message = error_data.get('message', 'Unknown API error')
        
        # Extract additional error details
        if 'errors' in error_data:
            if isinstance(error_data['errors'], list):
                message = '; '.join(error_data['errors'])
            elif isinstance(error_data['errors'], dict):
                error_details = []
                for field, errors in error_data['errors'].items():
                    if isinstance(errors, list):
                        error_details.append(f"{field}: {'; '.join(errors)}")
                    else:
                        error_details.append(f"{field}: {errors}")
                message = '; '.join(error_details)
        
    except (ValueError, KeyError):
        message = response.text or f"HTTP {response.status_code} error"
        error_data = None
    
    # Create and raise appropriate exception
    exception = create_exception_from_response(
        status_code=response.status_code,
        message=message,
        response_data=error_data,
        request_id=request_id
    )
    
    raise exception
