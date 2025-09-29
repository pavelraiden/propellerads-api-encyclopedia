"""
PropellerAds Python SDK

Professional PropellerAds SSP API v5 client with enterprise features.
"""

__version__ = "2.0.0"
__author__ = "PropellerAds Team"
__email__ = "support@propellerads.com"

# Import main client classes
from .client import PropellerAdsClient as LegacyPropellerAdsClient, BalanceResponse

# Try to import enhanced client, fallback to legacy if not available
try:
    from .client_enhanced import EnhancedPropellerAdsClient
    PropellerAdsClient = EnhancedPropellerAdsClient
except ImportError:
    PropellerAdsClient = LegacyPropellerAdsClient

# Import exceptions
from .exceptions import (
    PropellerAdsError,
    AuthenticationError,
    RateLimitError,
    ServerError
)

# Try to import API modules and schemas
try:
    from .api.campaigns import CampaignAPI
    from .api.statistics import StatisticsAPI
    from .api.balance import BalanceAPI
    from .api.collections import CollectionsAPI
    
    from .schemas.campaign import Campaign, CampaignTargeting
    from .schemas.statistics import StatisticsResponse
    from .schemas.balance import BalanceResponse as EnhancedBalanceResponse
    from .schemas.enums import Direction, RateModel, CampaignStatus
    
    _enhanced_available = True
except ImportError:
    _enhanced_available = False

__all__ = [
    # Main client
    'PropellerAdsClient',
    'LegacyPropellerAdsClient',
    'BalanceResponse',
    
    # Exceptions
    'PropellerAdsError',
    'AuthenticationError',
    'RateLimitError',
    'ServerError',
]

# Add enhanced features to __all__ if available
if _enhanced_available:
    __all__.extend([
        'EnhancedPropellerAdsClient',
        'CampaignAPI',
        'StatisticsAPI', 
        'BalanceAPI',
        'CollectionsAPI',
        'Campaign',
        'CampaignTargeting',
        'StatisticsResponse',
        'EnhancedBalanceResponse',
        'Direction',
        'RateModel',
        'CampaignStatus',
    ])
