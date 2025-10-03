"""
Base schema classes for PropellerAds API
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class PropellerBaseSchema(BaseModel):
    """Base schema class for all PropellerAds API models"""
    
    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,
        str_strip_whitespace=True
    )
    
    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for API requests"""
        return self.model_dump(exclude_none=True, by_alias=True)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]):
        """Create instance from API response data"""
        return cls.model_validate(data)


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields"""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDMixin(BaseModel):
    """Mixin for models with ID fields"""
    
    id: Optional[int] = None



class BaseResponse(PropellerBaseSchema):
    """Base response class for API responses"""
    
    success: bool = True
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Any] = None
    
    @property
    def is_success(self) -> bool:
        """Check if response is successful"""
        return self.success and not self.error
    
    @property
    def error_message(self) -> Optional[str]:
        """Get error message if any"""
        return self.error or (self.message if not self.success else None)
