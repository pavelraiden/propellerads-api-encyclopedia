"""
Creative schemas based on official PropellerAds API documentation
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, HttpUrl
from decimal import Decimal

from .base import PropellerBaseSchema, IDMixin, TimestampMixin
from .enums import CreativeType, CreativeStatus


class CampaignCreative(PropellerBaseSchema, IDMixin):
    """Campaign creative configuration"""
    
    # Template settings
    template_id: Optional[int] = Field(
        default=None, description="Template ID (supported for Interstitial)"
    )
    
    # Skin settings
    skin: Optional[str] = Field(default=None, description="Creative skin")
    
    # Creative content
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Media
    image_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    
    # Advanced settings
    custom_fields: Optional[Dict[str, Any]] = None


class Creative(PropellerBaseSchema, IDMixin, TimestampMixin):
    """Standalone creative model"""
    
    # Basic info
    name: str = Field(max_length=255, description="Creative name")
    type: CreativeType = Field(description="Creative type")
    status: CreativeStatus = Field(default=CreativeStatus.ACTIVE)
    
    # Content
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Media URLs
    image_url: Optional[HttpUrl] = None
    icon_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    
    # Dimensions
    width: Optional[int] = Field(default=None, ge=1)
    height: Optional[int] = Field(default=None, ge=1)
    
    # File info
    file_size: Optional[int] = Field(default=None, ge=0, description="File size in bytes")
    file_format: Optional[str] = None
    
    # Performance metrics
    impressions: Optional[int] = Field(default=0, ge=0)
    clicks: Optional[int] = Field(default=0, ge=0)
    conversions: Optional[int] = Field(default=0, ge=0)
    ctr: Optional[Decimal] = Field(default=None, ge=0, description="Click-through rate")
    
    # Campaign association
    campaign_id: Optional[int] = None
    
    # Additional settings
    custom_fields: Optional[Dict[str, Any]] = None


class CreativeFilters(PropellerBaseSchema):
    """Filters for creative listing"""
    status: Optional[List[CreativeStatus]] = None
    type: Optional[List[CreativeType]] = None
    campaign_id: Optional[int] = None
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)


class CreativeResponse(PropellerBaseSchema):
    """Creative API response wrapper"""
    data: List[Creative]
    total: int
    limit: int
    offset: int


class CreativePerformance(PropellerBaseSchema):
    """Creative performance statistics"""
    creative_id: int
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: Decimal = Field(default=Decimal('0'))
    revenue: Decimal = Field(default=Decimal('0'))
    ctr: Decimal = Field(default=Decimal('0'), description="Click-through rate")
    cvr: Decimal = Field(default=Decimal('0'), description="Conversion rate")
    roi: Decimal = Field(default=Decimal('0'), description="Return on investment")
    
    # Time period
    date_from: Optional[str] = None
    date_to: Optional[str] = None
