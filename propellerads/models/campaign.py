"""
PropellerAds Campaign Models

Pydantic models for campaign data validation and serialization.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    PENDING = "pending"
    REJECTED = "rejected"


class CampaignType(str, Enum):
    """Campaign type enumeration."""
    CPA = "cpa"
    CPM = "cpm"
    CPC = "cpc"


class TrafficSource(BaseModel):
    """Traffic source model."""
    id: int
    name: str
    type: str


class Campaign(BaseModel):
    """Campaign model with comprehensive validation."""
    
    id: int = Field(..., description="Unique campaign identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    status: CampaignStatus = Field(..., description="Campaign status")
    
    # Financial fields
    budget: Optional[Decimal] = Field(None, ge=0, description="Campaign budget")
    cost: Optional[Decimal] = Field(None, ge=0, description="Cost per action/click/impression")
    currency: str = Field(default="USD", description="Currency code")
    
    # Campaign type and targeting
    campaign_type: Optional[CampaignType] = Field(None, alias="type")
    traffic_source_id: Optional[int] = Field(None, description="Traffic source ID")
    traffic_source: Optional[TrafficSource] = Field(None, description="Traffic source details")
    
    # URLs and tracking
    target_url: Optional[str] = Field(None, description="Target URL")
    tracking_url: Optional[str] = Field(None, description="Tracking URL")
    
    # Dates
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Campaign start time")
    expires_at: Optional[datetime] = Field(None, description="Campaign expiration time")
    
    # Targeting
    countries: Optional[List[str]] = Field(None, description="Target countries")
    zones: Optional[List[int]] = Field(None, description="Target zones")
    
    # Statistics (read-only)
    impressions: Optional[int] = Field(None, ge=0, description="Total impressions")
    clicks: Optional[int] = Field(None, ge=0, description="Total clicks")
    conversions: Optional[int] = Field(None, ge=0, description="Total conversions")
    spent: Optional[Decimal] = Field(None, ge=0, description="Total spent amount")
    
    # Additional metadata
    user_id: Optional[int] = Field(None, description="Owner user ID")
    group_id: Optional[int] = Field(None, description="Campaign group ID")
    
    model_config = {
        "populate_by_name": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }
    }
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate campaign name."""
        if not v or not v.strip():
            raise ValueError('Campaign name cannot be empty')
        return v.strip()
    
    @field_validator('target_url', 'tracking_url')
    @classmethod
    def validate_urls(cls, v):
        """Validate URLs."""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @field_validator('countries')
    @classmethod
    def validate_countries(cls, v):
        """Validate country codes."""
        if v:
            for country in v:
                if not isinstance(country, str) or len(country) != 2:
                    raise ValueError('Country codes must be 2-letter ISO codes')
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate date relationships."""
        if self.started_at and self.expires_at and self.started_at >= self.expires_at:
            raise ValueError('Campaign start time must be before expiration time')
        return self
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Campaign':
        """Create Campaign instance from API response."""
        # Handle different date formats
        date_fields = ['created_at', 'updated_at', 'started_at', 'expires_at']
        for field in date_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    try:
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                            try:
                                data[field] = datetime.strptime(data[field], fmt)
                                break
                            except ValueError:
                                continue
                    except:
                        data[field] = None
        
        # Handle nested traffic source
        if 'traffic_source' in data and isinstance(data['traffic_source'], dict):
            data['traffic_source'] = TrafficSource(**data['traffic_source'])
        
        return cls(**data)
    
    @property
    def ctr(self) -> Optional[float]:
        """Calculate click-through rate."""
        if self.impressions and self.clicks:
            return (self.clicks / self.impressions) * 100
        return None
    
    @property
    def conversion_rate(self) -> Optional[float]:
        """Calculate conversion rate."""
        if self.clicks and self.conversions:
            return (self.conversions / self.clicks) * 100
        return None
    
    def is_active(self) -> bool:
        """Check if campaign is currently active."""
        return self.status == CampaignStatus.ACTIVE


class CampaignCreate(BaseModel):
    """Model for creating new campaigns."""
    
    name: str = Field(..., min_length=1, max_length=255)
    traffic_source_id: int = Field(..., gt=0)
    cost: Decimal = Field(..., ge=0)
    currency: str = Field(default="USD")
    
    # Optional fields
    budget: Optional[Decimal] = Field(None, ge=0)
    target_url: Optional[str] = None
    tracking_url: Optional[str] = None
    countries: Optional[List[str]] = None
    zones: Optional[List[int]] = None
    
    # Scheduling
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None,
            Decimal: lambda v: float(v)
        }
    }
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Campaign name is required')
        return v.strip()


class CampaignUpdate(BaseModel):
    """Model for updating existing campaigns."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[CampaignStatus] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    
    target_url: Optional[str] = None
    tracking_url: Optional[str] = None
    countries: Optional[List[str]] = None
    zones: Optional[List[int]] = None
    
    expires_at: Optional[datetime] = None
    
    model_config = {
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None,
            Decimal: lambda v: float(v) if v else None
        }
    }
