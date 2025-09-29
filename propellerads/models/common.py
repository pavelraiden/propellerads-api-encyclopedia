"""
PropellerAds Common Models

Shared Pydantic models for common API responses and requests.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class BalanceResponse(BaseModel):
    """Account balance response model."""
    
    amount: Decimal = Field(..., description="Balance amount")
    currency: str = Field(default="USD", description="Currency code")
    formatted: str = Field(..., description="Formatted balance string")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    }


class StatisticsRequest(BaseModel):
    """Statistics request model."""
    
    day_from: str = Field(..., description="Start date (YYYY-MM-DD HH:MM:SS)")
    day_to: str = Field(..., description="End date (YYYY-MM-DD HH:MM:SS)")
    tz: str = Field(default="+0000", description="Timezone offset")
    group_by: List[str] = Field(default=["campaign_id"], description="Grouping fields")
    campaign_ids: Optional[List[int]] = Field(None, description="Filter by campaign IDs")
    
    @field_validator('group_by')
    @classmethod
    def validate_group_by(cls, v):
        """Validate grouping fields."""
        allowed_fields = [
            'campaign_id', 'day', 'hour', 'country', 'zone', 'os', 'browser',
            'device_type', 'connection_type', 'carrier'
        ]
        
        for field in v:
            if field not in allowed_fields:
                raise ValueError(f"Invalid group_by field: {field}. Allowed: {allowed_fields}")
        
        return v


class StatisticsRow(BaseModel):
    """Single statistics row."""
    
    # Grouping fields
    campaign_id: Optional[int] = None
    day: Optional[str] = None
    hour: Optional[int] = None
    country: Optional[str] = None
    zone: Optional[int] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    device_type: Optional[str] = None
    connection_type: Optional[str] = None
    carrier: Optional[str] = None
    
    # Metrics
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spent: Decimal = Field(default=0, ge=0)
    revenue: Optional[Decimal] = Field(None, ge=0)
    
    # Calculated fields
    ctr: Optional[float] = None
    conversion_rate: Optional[float] = None
    cpc: Optional[Decimal] = None
    cpa: Optional[Decimal] = None
    
    model_config = {
        "json_encoders": {
            Decimal: lambda v: float(v) if v else None
        }
    }


class ApiError(BaseModel):
    """API error response model."""
    
    error: str
    message: str
    code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., pattern=r'^(healthy|unhealthy|degraded)$')
    timestamp: datetime
    api_version: str = Field(default="v5")
    response_time: Optional[float] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
