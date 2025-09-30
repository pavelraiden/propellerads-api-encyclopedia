"""
Collection schemas for targeting data
"""

from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import PropellerBaseSchema


class Country(PropellerBaseSchema):
    """Country targeting option"""
    
    code: str = Field(description="Alpha-2 country code (ISO 3166)")
    name: str = Field(description="Country name")
    region: Optional[str] = None
    continent: Optional[str] = None
    population: Optional[int] = None
    gdp_per_capita: Optional[float] = None
    internet_penetration: Optional[float] = None
    mobile_penetration: Optional[float] = None
    
    # Advertising metrics
    avg_cpc: Optional[float] = None
    avg_cpm: Optional[float] = None
    competition_level: Optional[str] = None  # low, medium, high
    
    # Supported ad formats
    supports_onclick: bool = True
    supports_push: bool = True
    supports_native: bool = True
    supports_interstitial: bool = True


class OS(PropellerBaseSchema):
    """Operating system targeting option"""
    
    code: str = Field(description="OS code")
    name: str = Field(description="OS name")
    type: str = Field(description="OS type: mobile, desktop, tablet")
    vendor: Optional[str] = None
    market_share: Optional[float] = None
    
    # Version support
    versions: Optional[List[str]] = None
    latest_version: Optional[str] = None


class OSVersion(PropellerBaseSchema):
    """OS version targeting option"""
    
    code: str = Field(description="OS version code")
    name: str = Field(description="OS version name")
    os_code: str = Field(description="Parent OS code")
    release_date: Optional[str] = None
    market_share: Optional[float] = None
    is_supported: bool = True


class Browser(PropellerBaseSchema):
    """Browser targeting option"""
    
    code: str = Field(description="Browser code")
    name: str = Field(description="Browser name")
    vendor: Optional[str] = None
    market_share: Optional[float] = None
    
    # Version support
    versions: Optional[List[str]] = None
    latest_version: Optional[str] = None
    
    # Capabilities
    supports_push: bool = True
    supports_native: bool = True
    supports_javascript: bool = True


class Device(PropellerBaseSchema):
    """Device targeting option"""
    
    code: str = Field(description="Device code")
    name: str = Field(description="Device name")
    type: str = Field(description="Device type: mobile, tablet, desktop")
    brand: Optional[str] = None
    model: Optional[str] = None
    
    # Specifications
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    screen_density: Optional[str] = None
    
    # Market data
    market_share: Optional[float] = None
    price_range: Optional[str] = None  # budget, mid-range, premium


class Carrier(PropellerBaseSchema):
    """Mobile carrier targeting option"""
    
    code: str = Field(description="Carrier code")
    name: str = Field(description="Carrier name")
    country_code: str = Field(description="Country code")
    type: str = Field(description="Carrier type: mobile, wifi")
    market_share: Optional[float] = None


class Zone(PropellerBaseSchema):
    """Zone targeting option"""
    
    id: int = Field(description="Zone ID")
    name: str = Field(description="Zone name")
    type: str = Field(description="Zone type")
    category: Optional[str] = None
    
    # Performance metrics
    avg_cpc: Optional[float] = None
    avg_cpm: Optional[float] = None
    quality_score: Optional[float] = Field(ge=0, le=10)
    
    # Targeting info
    countries: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    
    # Status
    is_active: bool = True
    is_premium: bool = False


class Language(PropellerBaseSchema):
    """Language targeting option"""
    
    code: str = Field(description="Language code (ISO 639-1)")
    name: str = Field(description="Language name")
    native_name: Optional[str] = None
    
    # Geographic data
    countries: Optional[List[str]] = None
    speakers: Optional[int] = None
    
    # Advertising data
    market_size: Optional[str] = None  # small, medium, large
    competition: Optional[str] = None  # low, medium, high


class UserActivityLevel(PropellerBaseSchema):
    """User activity level targeting option"""
    
    level: int = Field(description="Activity level: 1=High, 2=Medium, 3=Low")
    name: str = Field(description="Activity level name")
    description: Optional[str] = None
    
    # Characteristics
    avg_session_duration: Optional[int] = None  # in seconds
    avg_pages_per_session: Optional[float] = None
    bounce_rate: Optional[float] = None
    conversion_rate: Optional[float] = None


class CollectionResponse(PropellerBaseSchema):
    """Generic collection response wrapper"""
    
    data: List[Dict[str, Any]]
    total: int
    collection_type: str
    last_updated: Optional[str] = None


class TargetingOptions(PropellerBaseSchema):
    """Complete targeting options"""
    
    countries: List[Country] = Field(default_factory=list)
    operating_systems: List[OS] = Field(default_factory=list)
    os_versions: List[OSVersion] = Field(default_factory=list)
    browsers: List[Browser] = Field(default_factory=list)
    devices: List[Device] = Field(default_factory=list)
    carriers: List[Carrier] = Field(default_factory=list)
    zones: List[Zone] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    user_activity_levels: List[UserActivityLevel] = Field(default_factory=list)
    
    # Metadata
    last_updated: Optional[str] = None
    version: Optional[str] = None
