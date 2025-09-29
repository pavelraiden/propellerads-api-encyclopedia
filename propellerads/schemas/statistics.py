"""
Statistics schemas for PropellerAds API
"""

from typing import List, Optional, Dict, Any
from pydantic import Field
from decimal import Decimal
from datetime import datetime, date

from .base import PropellerBaseSchema


class StatisticsFilters(PropellerBaseSchema):
    """Filters for statistics queries"""
    
    # Time range
    date_from: str = Field(description="Start date in YYYY-MM-DD format")
    date_to: str = Field(description="End date in YYYY-MM-DD format")
    
    # Campaign filters
    campaign_ids: Optional[List[int]] = None
    creative_ids: Optional[List[int]] = None
    
    # Grouping
    group_by: Optional[List[str]] = Field(
        default=None,
        description="Group by: campaign, creative, country, os, browser, etc."
    )
    
    # Pagination
    limit: Optional[int] = Field(default=1000, ge=1, le=10000)
    offset: Optional[int] = Field(default=0, ge=0)
    
    # Sorting
    order_by: Optional[str] = Field(default="date", description="Sort field")
    order_direction: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class StatisticsRow(PropellerBaseSchema):
    """Single statistics row"""
    
    # Identifiers
    campaign_id: Optional[int] = None
    campaign_name: Optional[str] = None
    creative_id: Optional[int] = None
    creative_name: Optional[str] = None
    
    # Dimensions
    date: Optional[date] = None
    country: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    device_type: Optional[str] = None
    
    # Metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: Decimal = Field(default=Decimal('0'))
    revenue: Decimal = Field(default=Decimal('0'))
    
    # Calculated metrics
    ctr: Decimal = Field(default=Decimal('0'), description="Click-through rate (%)")
    cvr: Decimal = Field(default=Decimal('0'), description="Conversion rate (%)")
    cpc: Decimal = Field(default=Decimal('0'), description="Cost per click")
    cpm: Decimal = Field(default=Decimal('0'), description="Cost per mille")
    cpa: Decimal = Field(default=Decimal('0'), description="Cost per acquisition")
    roi: Decimal = Field(default=Decimal('0'), description="Return on investment (%)")
    profit: Decimal = Field(default=Decimal('0'), description="Profit (revenue - spend)")
    
    # Additional metrics
    unique_clicks: Optional[int] = None
    bounce_rate: Optional[Decimal] = None
    session_duration: Optional[int] = None  # in seconds


class Statistics(PropellerBaseSchema):
    """Statistics response"""
    
    data: List[StatisticsRow]
    total_rows: int
    summary: Optional[StatisticsRow] = None  # Aggregated totals
    
    # Metadata
    date_from: str
    date_to: str
    generated_at: datetime = Field(default_factory=datetime.now)


class PerformanceInsight(PropellerBaseSchema):
    """AI-generated performance insight"""
    
    type: str  # trend, anomaly, recommendation, alert
    title: str
    description: str
    severity: str = "info"  # info, warning, critical
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    
    # Related data
    campaign_id: Optional[int] = None
    creative_id: Optional[int] = None
    metric: Optional[str] = None
    value: Optional[Decimal] = None
    
    # Recommendations
    recommended_action: Optional[str] = None
    expected_impact: Optional[str] = None


class PerformanceReport(PropellerBaseSchema):
    """Comprehensive performance report"""
    
    # Summary metrics
    total_campaigns: int = 0
    active_campaigns: int = 0
    total_spend: Decimal = Field(default=Decimal('0'))
    total_revenue: Decimal = Field(default=Decimal('0'))
    overall_roi: Decimal = Field(default=Decimal('0'))
    
    # Top performers
    top_campaigns: List[StatisticsRow] = Field(default_factory=list)
    top_creatives: List[StatisticsRow] = Field(default_factory=list)
    top_countries: List[StatisticsRow] = Field(default_factory=list)
    
    # Insights
    insights: List[PerformanceInsight] = Field(default_factory=list)
    
    # Time period
    date_from: str
    date_to: str
    generated_at: datetime = Field(default_factory=datetime.now)


class TrendAnalysis(PropellerBaseSchema):
    """Trend analysis for metrics over time"""
    
    metric: str  # impressions, clicks, conversions, spend, etc.
    trend_direction: str  # up, down, stable
    trend_strength: float = Field(ge=0, le=1, description="Trend strength 0-1")
    
    # Data points
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Statistics
    average_value: Decimal = Field(default=Decimal('0'))
    min_value: Decimal = Field(default=Decimal('0'))
    max_value: Decimal = Field(default=Decimal('0'))
    variance: Decimal = Field(default=Decimal('0'))
    
    # Predictions
    predicted_next_value: Optional[Decimal] = None
    confidence_interval: Optional[Dict[str, Decimal]] = None
