"""
PropellerAds API Schemas
Complete schema definitions based on official Swagger documentation
"""

from .base import PropellerBaseSchema
from .campaign import Campaign, CampaignTargeting, CampaignRates, CampaignAudience
from .creative import Creative, CampaignCreative
from .balance import Balance
from .statistics import Statistics, StatisticsFilters
from .collections import Country, OS, OSVersion, Browser, UserActivity
from .enums import *

__all__ = [
    'PropellerBaseSchema',
    'Campaign',
    'CampaignTargeting', 
    'CampaignRates',
    'CampaignAudience',
    'Creative',
    'CampaignCreative',
    'Balance',
    'Statistics',
    'StatisticsFilters',
    'Country',
    'OS',
    'OSVersion',
    'Browser',
    'UserActivity',
]
