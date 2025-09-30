"""
Enums for PropellerAds API based on official Swagger documentation
"""

from enum import Enum


class Direction(str, Enum):
    """Campaign direction types"""
    ONCLICK = "onclick"
    NATIVEADS = "nativeads" 
    NATIVE = "native"


class RateModel(str, Enum):
    """Campaign rate models"""
    CPM = "cpm"          # Cost per mile
    SCPM = "scpm"        # Smart cost per mile
    CPC = "cpc"          # Cost per click
    SCPC = "scpc"        # Smart cost per click
    SCPA = "scpa"        # CPA Goal 2.0 (by impressions for OnClick)
    CPAG = "cpag"        # CPA Goal 2.0 (by clicks for Push)


class CampaignStatus(int, Enum):
    """Campaign status values"""
    DRAFT = 1
    MODERATION = 2


class AudienceTopics(int, Enum):
    """Audience topic types"""
    CLICKS = 1
    ENGAGED_USERS = 2
    CONVERSIONS = 3


class Connection(str, Enum):
    """Connection types"""
    MOBILE = "mobile"
    OTHER = "other"


class UserActivity(int, Enum):
    """User activity levels"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class UVC(str, Enum):
    """UVC types for Telegram Ads"""
    HIGH_INTENT = "high_intent"
    WIDE_REACH = "wide_reach"


class ZoneType(int, Enum):
    """Zone types"""
    IN_PAGE_PUSH_1 = 42   # In-Page Push (used together)
    IN_PAGE_PUSH_2 = 78   # In-Page Push (used together)
    IN_PAGE_PUSH_3 = 119  # In-Page Push (used together)
    INTERSTITIAL = 135    # Interstitial


class TrafficCategory(str, Enum):
    """Traffic categories"""
    PROPELLER = "propeller"
    BROKER = "broker"
    PREMIUM = "premium"
    SOCIAL_TRAFFIC = "social_traffic"
    ALL_SURVEY = "all_survey"
    FINANCE_SURVEY = "finance_survey"
    SWEEPS_SURVEY = "sweeps_survey"
    SOCIAL_NETWORKS_SURVEY = "social_networks_survey"


class Timezone(int, Enum):
    """Timezone values"""
    UTC_MINUS_12 = -12
    UTC_MINUS_11 = -11
    UTC_MINUS_10 = -10
    UTC_MINUS_9 = -9
    UTC_MINUS_8 = -8
    UTC_MINUS_7 = -7
    UTC_MINUS_6 = -6
    UTC_MINUS_5 = -5
    UTC_MINUS_4 = -4
    UTC_MINUS_3 = -3
    UTC_MINUS_2 = -2
    UTC_MINUS_1 = -1
    UTC = 0
    UTC_PLUS_1 = 1
    UTC_PLUS_2 = 2
    UTC_PLUS_3 = 3
    UTC_PLUS_4 = 4
    UTC_PLUS_5 = 5
    UTC_PLUS_6 = 6
    UTC_PLUS_7 = 7
    UTC_PLUS_8 = 8
    UTC_PLUS_9 = 9
    UTC_PLUS_10 = 10
    UTC_PLUS_11 = 11
    UTC_PLUS_12 = 12


class CreativeType(str, Enum):
    """Creative types"""
    BANNER = "banner"
    NATIVE = "native"
    PUSH = "push"
    INTERSTITIAL = "interstitial"


class CreativeStatus(int, Enum):
    """Creative status values"""
    ACTIVE = 1
    PAUSED = 2
    REJECTED = 3
