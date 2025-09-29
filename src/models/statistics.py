"""Statistics data models with validation"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, date


class StatisticsRequest(BaseModel):
    """Model for statistics API requests"""
    day_from: str = Field(..., description="Start date in YYYY-MM-DD HH:MM:SS format")
    day_to: str = Field(..., description="End date in YYYY-MM-DD HH:MM:SS format")
    tz: str = Field(default="+0000", description="Timezone offset")
    group_by: List[str] = Field(default=["campaign_id"], description="Grouping fields")
    campaign_id: Optional[List[int]] = Field(None, description="Filter by campaign IDs")
    zone_id: Optional[List[int]] = Field(None, description="Filter by zone IDs")
    geo: Optional[List[str]] = Field(None, description="Filter by countries")
    order_by: str = Field(default="spent", description="Sort field")
    order_dest: str = Field(default="desc", description="Sort direction")

    @validator('day_from', 'day_to')
    def validate_datetime_format(cls, v):
        """Validate datetime format"""
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD HH:MM:SS format')

    @validator('tz')
    def validate_timezone(cls, v):
        """Validate timezone format"""
        if not v.startswith(('+', '-')) or len(v) != 5:
            raise ValueError('Timezone must be in format +HHMM or -HHMM')
        return v

    @validator('group_by')
    def validate_group_by(cls, v):
        """Validate grouping fields"""
        valid_fields = [
            'campaign_id', 'zone_id', 'country_id', 'date_time', 'hour',
            'banner_id', 'os_id', 'browser_id', 'connection_type_id'
        ]
        for field in v:
            if field not in valid_fields:
                raise ValueError(f'Invalid group_by field: {field}. Valid fields: {valid_fields}')
        return v

    @validator('order_by')
    def validate_order_by(cls, v):
        """Validate sort field"""
        valid_fields = ['impressions', 'clicks', 'conversions', 'spent', 'payout', 'ctr', 'cr', 'cpa']
        if v not in valid_fields:
            raise ValueError(f'Invalid order_by field: {v}. Valid fields: {valid_fields}')
        return v

    @validator('order_dest')
    def validate_order_direction(cls, v):
        """Validate sort direction"""
        if v not in ['asc', 'desc']:
            raise ValueError('order_dest must be "asc" or "desc"')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "day_from": "2025-09-22 00:00:00",
                "day_to": "2025-09-29 23:59:59",
                "tz": "+0000",
                "group_by": ["campaign_id"],
                "campaign_id": [12345, 12346],
                "order_by": "spent",
                "order_dest": "desc"
            }
        }


class StatisticsRecord(BaseModel):
    """Single statistics record"""
    campaign_id: Optional[int] = None
    zone_id: Optional[int] = None
    country_id: Optional[int] = None
    date_time: Optional[str] = None
    hour: Optional[int] = None
    banner_id: Optional[int] = None
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spent: float = Field(default=0.0, ge=0)
    payout: float = Field(default=0.0, ge=0)
    ctr: Optional[float] = Field(None, ge=0, le=100, description="Click-through rate %")
    cr: Optional[float] = Field(None, ge=0, le=100, description="Conversion rate %")
    cpa: Optional[float] = Field(None, ge=0, description="Cost per acquisition")
    roi: Optional[float] = Field(None, description="Return on investment %")

    @validator('ctr', 'cr', 'roi', pre=True)
    def round_percentages(cls, v):
        """Round percentage values"""
        if v is not None:
            return round(float(v), 2)
        return v

    @validator('spent', 'payout', 'cpa', pre=True)
    def round_money(cls, v):
        """Round monetary values"""
        if v is not None:
            return round(float(v), 3)
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 12345,
                "impressions": 10000,
                "clicks": 150,
                "conversions": 5,
                "spent": 15.75,
                "payout": 25.00,
                "ctr": 1.5,
                "cr": 3.33,
                "cpa": 3.15,
                "roi": 58.73
            }
        }


class PerformanceSummary(BaseModel):
    """Campaign performance summary"""
    campaign_id: int
    period: str = Field(..., description="Date range analyzed")
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spent: float = Field(default=0.0, ge=0)
    revenue: float = Field(default=0.0, ge=0)
    profit: float = Field(default=0.0)
    roi: float = Field(default=0.0, description="Return on investment %")
    avg_ctr: float = Field(default=0.0, ge=0, le=100, description="Average CTR %")
    avg_cr: float = Field(default=0.0, ge=0, le=100, description="Average CR %")
    avg_cpc: float = Field(default=0.0, ge=0, description="Average cost per click")
    avg_cpa: float = Field(default=0.0, ge=0, description="Average cost per acquisition")

    @validator('roi', 'avg_ctr', 'avg_cr', pre=True)
    def round_percentages(cls, v):
        """Round percentage values"""
        return round(float(v), 2)

    @validator('spent', 'revenue', 'profit', 'avg_cpc', 'avg_cpa', pre=True)
    def round_money(cls, v):
        """Round monetary values"""
        return round(float(v), 3)

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": 12345,
                "period": "2025-09-22 to 2025-09-29",
                "impressions": 50000,
                "clicks": 750,
                "conversions": 25,
                "spent": 78.50,
                "revenue": 125.00,
                "profit": 46.50,
                "roi": 59.24,
                "avg_ctr": 1.5,
                "avg_cr": 3.33,
                "avg_cpc": 0.105,
                "avg_cpa": 3.14
            }
        }


class ZonePerformance(BaseModel):
    """Zone performance analysis"""
    zone_id: int
    zone_name: Optional[str] = None
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spent: float = Field(default=0.0, ge=0)
    revenue: float = Field(default=0.0, ge=0)
    ctr: float = Field(default=0.0, ge=0, le=100)
    cr: float = Field(default=0.0, ge=0, le=100)
    cpa: float = Field(default=0.0, ge=0)
    roi: float = Field(default=0.0)
    efficiency_score: float = Field(default=0.0, ge=0, le=100, description="Zone efficiency score")
    recommendation: str = Field(default="MONITOR", description="Optimization recommendation")

    @validator('ctr', 'cr', 'roi', 'efficiency_score', pre=True)
    def round_percentages(cls, v):
        """Round percentage values"""
        return round(float(v), 2)

    @validator('spent', 'revenue', 'cpa', pre=True)
    def round_money(cls, v):
        """Round monetary values"""
        return round(float(v), 3)

    @validator('recommendation')
    def validate_recommendation(cls, v):
        """Validate recommendation values"""
        valid_recommendations = [
            'WHITELIST', 'BLACKLIST', 'OPTIMIZE', 'MONITOR', 'TESTING'
        ]
        if v not in valid_recommendations:
            raise ValueError(f'Invalid recommendation: {v}. Valid values: {valid_recommendations}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "zone_id": 12345,
                "zone_name": "Premium Mobile Zone",
                "impressions": 5000,
                "clicks": 75,
                "conversions": 3,
                "spent": 7.50,
                "revenue": 15.00,
                "ctr": 1.5,
                "cr": 4.0,
                "cpa": 2.50,
                "roi": 100.0,
                "efficiency_score": 85.5,
                "recommendation": "WHITELIST"
            }
        }


class HourlyPerformance(BaseModel):
    """Hourly performance data for dayparting"""
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spent: float = Field(default=0.0, ge=0)
    ctr: float = Field(default=0.0, ge=0, le=100)
    cr: float = Field(default=0.0, ge=0, le=100)
    efficiency_score: float = Field(default=0.0, ge=0, le=100)
    recommendation: str = Field(default="NORMAL")

    @validator('ctr', 'cr', 'efficiency_score', pre=True)
    def round_percentages(cls, v):
        """Round percentage values"""
        return round(float(v), 2)

    @validator('spent', pre=True)
    def round_money(cls, v):
        """Round monetary values"""
        return round(float(v), 3)

    class Config:
        json_schema_extra = {
            "example": {
                "hour": 14,
                "impressions": 2000,
                "clicks": 30,
                "conversions": 1,
                "spent": 3.00,
                "ctr": 1.5,
                "cr": 3.33,
                "efficiency_score": 75.0,
                "recommendation": "OPTIMIZE"
            }
        }


class ComparisonPeriod(BaseModel):
    """Period comparison data"""
    period_name: str = Field(..., description="Period identifier")
    dates: str = Field(..., description="Date range")
    metrics: Dict[str, float] = Field(..., description="Period metrics")
    changes: Optional[Dict[str, Dict[str, Union[float, str]]]] = Field(None, description="Changes from previous period")

    class Config:
        json_schema_extra = {
            "example": {
                "period_name": "Current Week",
                "dates": "2025-09-22 to 2025-09-29",
                "metrics": {
                    "impressions": 50000,
                    "clicks": 750,
                    "conversions": 25,
                    "spent": 78.50,
                    "roi": 59.24
                },
                "changes": {
                    "impressions": {"absolute": 5000, "percentage": 11.11},
                    "roi": {"absolute": -5.5, "percentage": -8.5}
                }
            }
        }
