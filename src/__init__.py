"""PropellerAds API Encyclopedia Package"""

from .client.async_client import PropellerAdsAsyncClient
from .models.campaign import CampaignCreate, CampaignUpdate, Campaign
from .models.statistics import StatisticsRequest, PerformanceSummary
from .exceptions import PropellerAdsError, AuthenticationError, ValidationError

__version__ = "2.0.0"
__all__ = [
    "PropellerAdsAsyncClient",
    "CampaignCreate", 
    "CampaignUpdate", 
    "Campaign",
    "StatisticsRequest", 
    "PerformanceSummary",
    "PropellerAdsError", 
    "AuthenticationError", 
    "ValidationError"
]
