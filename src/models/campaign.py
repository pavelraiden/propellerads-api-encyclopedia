"""Campaign data models with enhanced validation"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class Rate(BaseModel):
    """Rate model for campaign pricing"""
    countries: List[str] = Field(..., min_items=1, description="List of country codes")
    amount: float = Field(..., gt=0, description="Rate amount in USD")

    @validator('countries')
    def validate_countries(cls, v):
        """Validate country codes"""
        if not v:
            raise ValueError("At least one country is required")
        # Convert to uppercase
        return [country.upper() for country in v]


class Targeting(BaseModel):
    """Targeting configuration model"""
    country: Dict[str, Any] = Field(..., description="Country targeting")
    traffic_categories: Optional[Dict[str, Any]] = None
    operating_systems: Optional[Dict[str, Any]] = None
    browsers: Optional[Dict[str, Any]] = None
    connection_type: Optional[Dict[str, Any]] = None
    device_type: Optional[Dict[str, Any]] = None

    @validator('country')
    def validate_country_targeting(cls, v):
        """Validate country targeting structure"""
        if not isinstance(v, dict):
            raise ValueError("Country targeting must be a dictionary")
        if 'list' not in v or 'is_excluded' not in v:
            raise ValueError("Country targeting must have 'list' and 'is_excluded' fields")
        return v


class CampaignCreate(BaseModel):
    """Model for creating a new campaign"""
    name: str = Field(..., max_length=255, min_length=1, description="Campaign name")
    direction: str = Field(
        ..., 
        pattern="^(onclick|ipp|classic_push|survey|display_interstitial|telegram)$",
        description="Ad format"
    )
    rate_model: str = Field(
        ..., 
        pattern="^(cpm|scpm|cpc|scpc|scpa|cpag)$",
        description="Pricing model"
    )
    target_url: str = Field(..., description="Landing page URL")
    status: int = Field(default=1, ge=1, le=2, description="1=draft, 2=moderation")
    started_at: str = Field(..., description="Start date in dd/MM/YYYY format")
    expired_at: Optional[str] = Field(None, description="End date in dd/MM/YYYY format")
    frequency: Optional[int] = Field(default=0, ge=0, le=100, description="Frequency cap")
    capping: Optional[int] = Field(default=0, ge=0, le=1209600, description="Time-based capping in seconds")
    is_adblock_buy: Optional[int] = Field(default=0, ge=0, le=1, description="Adblock traffic")
    limit_daily_amount: Optional[float] = Field(None, gt=0, description="Daily budget limit")
    limit_total_amount: Optional[float] = Field(None, gt=0, description="Total budget limit")
    targeting: Targeting = Field(..., description="Targeting configuration")
    timezone: int = Field(default=-5, ge=-12, le=12, description="Timezone offset")
    allow_zone_update: bool = Field(default=True, description="Allow automatic zone updates")
    rates: List[Rate] = Field(..., min_items=1, description="Country-specific rates")
    creatives: Optional[List[Dict[str, Any]]] = Field(None, description="Initial creatives")

    @validator('target_url')
    def validate_cpa_url(cls, v, values):
        """Validate URL for CPA campaigns"""
        rate_model = values.get('rate_model', '')
        if rate_model in ['cpa', 'scpa', 'cpag'] and '${SUBID}' not in v:
            raise ValueError(f'{rate_model} campaigns must include ${{SUBID}} macro in target URL')
        return v

    @validator('started_at', 'expired_at')
    def validate_date_format(cls, v):
        """Validate date format"""
        if v is None:
            return v
        try:
            datetime.strptime(v, '%d/%m/%Y')
            return v
        except ValueError:
            raise ValueError('Date must be in dd/MM/YYYY format')

    @validator('rates')
    def validate_rates_countries_match_targeting(cls, v, values):
        """Validate that rates countries match targeting"""
        targeting = values.get('targeting')
        if targeting and hasattr(targeting, 'country'):
            target_countries = set(targeting.country.get('list', []))
            rate_countries = set()
            for rate in v:
                rate_countries.update(rate.countries)
            
            if not target_countries.issubset(rate_countries):
                missing = target_countries - rate_countries
                raise ValueError(f'Missing rates for countries: {missing}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Summer Gaming Push Campaign",
                "direction": "classic_push",
                "rate_model": "cpc",
                "target_url": "https://example.com?clickid=${SUBID}",
                "started_at": "01/08/2024",
                "targeting": {
                    "country": {"list": ["US", "GB", "CA"], "is_excluded": False},
                    "traffic_categories": {"list": ["propeller"], "is_excluded": False}
                },
                "rates": [
                    {"countries": ["US"], "amount": 0.05},
                    {"countries": ["GB", "CA"], "amount": 0.04}
                ],
                "limit_daily_amount": 100.0
            }
        }


class CampaignUpdate(BaseModel):
    """Model for updating campaign settings"""
    name: Optional[str] = Field(None, max_length=255, min_length=1)
    frequency: Optional[int] = Field(None, ge=0, le=100)
    capping: Optional[int] = Field(None, ge=0, le=1209600)
    limit_total_amount: Optional[float] = Field(None, gt=0)
    limit_daily_amount: Optional[float] = Field(None, gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Campaign Name",
                "limit_daily_amount": 150.0,
                "frequency": 3
            }
        }


class Campaign(BaseModel):
    """Full campaign model for API responses"""
    id: int
    direction_id: int
    name: str
    rate_model: str
    status: int
    is_archived: int
    frequency: Optional[int] = None
    capping: Optional[int] = None
    target_url: str
    started_at: str
    expired_at: Optional[str] = None
    limit_total_amount: Optional[float] = None
    limit_daily_amount: Optional[float] = None
    allow_zone_update: bool
    targeting: Optional[Dict[str, Any]] = None
    rates: Optional[List[Dict[str, Any]]] = None
    creatives: Optional[List[Dict[str, Any]]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "direction_id": 1,
                "name": "Test Campaign",
                "rate_model": "cpc",
                "status": 6,
                "is_archived": 0,
                "target_url": "https://example.com",
                "started_at": "01/08/2024",
                "limit_daily_amount": 100.0,
                "allow_zone_update": True
            }
        }


class CampaignBulkAction(BaseModel):
    """Model for bulk campaign actions"""
    campaign_ids: List[int] = Field(..., min_items=1, description="List of campaign IDs")
    
    @validator('campaign_ids')
    def validate_campaign_ids(cls, v):
        """Validate campaign IDs"""
        if not v:
            raise ValueError("At least one campaign ID is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 campaigns per bulk action")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_ids": [12345, 12346, 12347]
            }
        }
