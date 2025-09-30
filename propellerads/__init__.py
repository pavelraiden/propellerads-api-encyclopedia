"""
PropellerAds Python SDK

Professional PropellerAds SSP API v5 client with enterprise features.
"""

import sys

# Check Python version compatibility
if sys.version_info < (3, 11):
    raise RuntimeError(
        "PropellerAds SDK requires Python 3.11 or higher. "
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

__version__ = "2.0.0"
__author__ = "PropellerAds Team"
__email__ = "support@propellerads.com"

# Import main client classes
from .client import PropellerAdsClient as LegacyPropellerAdsClient, BalanceResponse

# Try to import enhanced client, fallback to legacy if not available
try:
    from .client_enhanced import EnhancedPropellerAdsClient
    from .async_client import AsyncPropellerAdsClient
    PropellerAdsClient = EnhancedPropellerAdsClient
    _async_available = True
except ImportError:
    PropellerAdsClient = LegacyPropellerAdsClient
    _async_available = False

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

# Add async client if available
if _async_available:
    __all__.append('AsyncPropellerAdsClient')
