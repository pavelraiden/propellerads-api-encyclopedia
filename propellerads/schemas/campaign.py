"""
Campaign schemas based on official PropellerAds API documentation
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from decimal import Decimal

from .base import PropellerBaseSchema, IDMixin, TimestampMixin
from .enums import (
    Direction, RateModel, CampaignStatus, AudienceTopics, 
    Connection, UserActivity, UVC, ZoneType, TrafficCategory, Timezone
)


class TargetingList(PropellerBaseSchema):
    """Base targeting list structure"""
    list: List[str] = Field(default_factory=list)
    is_excluded: bool = False


class IntegerTargetingList(PropellerBaseSchema):
    """Integer-based targeting list structure"""
    list: List[int] = Field(default_factory=list)
    is_excluded: bool = False


class CampaignTargeting(PropellerBaseSchema):
    """Campaign targeting configuration"""
    
    # Country targeting (required)
    country: TargetingList = Field(
        description="Alpha-2 country codes in lowercase (ISO 3166)"
    )
    
    # Time table targeting (required)
    time_table: TargetingList = Field(
        description="Day of week and hour for scheduling (e.g., Mon00, Tue03)"
    )
    
    # Connection type
    connection: Optional[Connection] = None
    
    # OS targeting
    os_type: Optional[TargetingList] = None
    os: Optional[TargetingList] = None
    os_version: Optional[TargetingList] = None
    
    # User activity targeting
    user_activity: Optional[IntegerTargetingList] = None
    
    # UVC targeting (Telegram Ads only)
    uvc: Optional[TargetingList] = None
    
    # Zone targeting
    zone: Optional[IntegerTargetingList] = None
    sub_zone: Optional[IntegerTargetingList] = None
    zone_type: Optional[IntegerTargetingList] = None
    
    # Traffic categories
    traffic_categories: Optional[List[TrafficCategory]] = None


class CampaignRates(PropellerBaseSchema):
    """Campaign rate configuration"""
    amount: Decimal = Field(description="Rate amount")
    countries: List[str] = Field(description="Country codes for this rate")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class CampaignAudience(PropellerBaseSchema):
    """Campaign audience configuration"""
    topics: Optional[List[AudienceTopics]] = None
    audience_id: Optional[int] = None


class CampaignCPATest(PropellerBaseSchema):
    """CPA test configuration for OnClick CPA"""
    test_limit_amount: Optional[Decimal] = None


class Campaign(PropellerBaseSchema, IDMixin, TimestampMixin):
    """Complete campaign model based on official API"""
    
    # Basic campaign info
    name: str = Field(max_length=255, description="Campaign name")
    direction: Direction = Field(description="Campaign direction")
    rate_model: RateModel = Field(description="Rate model")
    target_url: str = Field(description="Target URL with ${SUBID} macro for CPA/SCPA")
    
    # Campaign settings
    frequency: Optional[int] = Field(
        default=None, ge=0, le=100,
        description="Frequency cap, 0 for unlimited"
    )
    capping: Optional[int] = Field(
        default=None, ge=0, le=1209600,
        description="Capping in seconds, 0 for unlimited"
    )
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    
    # Dates
    started_at: str = Field(description="Start date in dd/MM/YYYY format")
    expired_at: Optional[str] = Field(
        default=None, description="End date in dd/MM/YYYY format"
    )
    
    # Audience
    audience: Optional[CampaignAudience] = None
    
    # Advanced settings
    evenly_limits_usage: Optional[int] = Field(default=None, ge=0, le=1)
    is_adblock_buy: Optional[int] = Field(default=None, ge=0, le=1)
    
    # Budget
    daily_amount: Optional[Decimal] = Field(
        default=None, description="Daily budget (min $10, $5 for OnClick CPA)"
    )
    total_amount: Optional[Decimal] = Field(
        default=None, description="Total budget (min $10, $100 for OnClick CPA)"
    )
    
    # Targeting (required)
    targeting: CampaignTargeting
    
    # Timezone (required)
    timezone: Timezone = Field(default=Timezone.UTC_MINUS_5)
    
    # CPA Goal settings
    cpa_goal_status: Optional[bool] = None
    cpa_goal_bid: Optional[Decimal] = None
    cpa_goal_slice_budget: Optional[Decimal] = None
    
    # Auto bidding
    is_auto_bidding: Optional[int] = Field(default=None, ge=0, le=1)
    
    # Zone updates
    allow_zone_update: Optional[bool] = None
    
    # CPA test (OnClick CPA only)
    campaign_cpa_test: Optional[CampaignCPATest] = None
    
    # Rates (required)
    rates: List[CampaignRates] = Field(description="Rate configuration by countries")
    
    # Creatives
    creatives: Optional[List[Dict[str, Any]]] = None
    
    @field_validator('target_url')
    @classmethod
    def validate_target_url(cls, v, info):
        """Validate target URL contains ${SUBID} for CPA/SCPA models"""
        if info.data and info.data.get('rate_model') in [RateModel.SCPA, RateModel.CPAG]:
            if '${SUBID}' not in v:
                raise ValueError('CPA & SCPA rate models must have ${SUBID} macro')
        return v
    
    @field_validator('daily_amount', 'total_amount', 'cpa_goal_bid', 'cpa_goal_slice_budget')
    @classmethod
    def validate_decimal_fields(cls, v):
        if v is not None and isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class CampaignFilters(PropellerBaseSchema):
    """Filters for campaign listing"""
    status: Optional[List[CampaignStatus]] = None
    direction: Optional[List[Direction]] = None
    rate_model: Optional[List[RateModel]] = None
    limit: Optional[int] = Field(default=100, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)


class CampaignResponse(PropellerBaseSchema):
    """Campaign API response wrapper"""
    data: List[Campaign]
    total: int
    limit: int
    offset: int
