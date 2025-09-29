"""
Collections API implementation for targeting data
"""

from typing import List, Optional, Dict, Any
import logging

from .base import BaseAPI
from ..schemas.collections import (
    Country, OS, OSVersion, Browser, Device, Carrier, 
    Zone, Language, UserActivityLevel, TargetingOptions
)

logger = logging.getLogger(__name__)


class CollectionsAPI(BaseAPI):
    """Collections API for targeting and reference data"""
    
    def get_targeting_options(self):
        """
        Get all targeting options (synchronous)
        
        Returns:
            Dictionary with all targeting options
        """
        logger.debug("Getting targeting options")
        
        try:
            # Try to get countries
            countries_response = self.client._make_request('GET', '/adv/collections/countries')
            countries = countries_response.json()
        except:
            countries = []
        
        try:
            # Try to get OS
            os_response = self.client._make_request('GET', '/adv/collections/os')
            operating_systems = os_response.json()
        except:
            operating_systems = []
        
        try:
            # Try to get browsers
            browsers_response = self.client._make_request('GET', '/adv/collections/browsers')
            browsers = browsers_response.json()
        except:
            browsers = []
        
        return {
            'countries': countries,
            'operating_systems': operating_systems,
            'browsers': browsers,
            'devices': ['desktop', 'mobile', 'tablet'],
            'connections': ['wifi', 'mobile', 'all']
        }
    
    async def get_countries(self) -> List[Country]:
        """
        Get available countries for targeting
        
        Returns:
            List of countries
        """
        logger.debug("Getting countries collection")
        
        response = await self._get('/adv/collections/countries')
        
        countries = []
        if 'data' in response:
            for country_data in response['data']:
                countries.append(Country(
                    code=country_data.get('code', ''),
                    name=country_data.get('name', ''),
                    region=country_data.get('region'),
                    continent=country_data.get('continent'),
                    population=country_data.get('population'),
                    gdp_per_capita=country_data.get('gdp_per_capita'),
                    internet_penetration=country_data.get('internet_penetration'),
                    mobile_penetration=country_data.get('mobile_penetration'),
                    avg_cpc=country_data.get('avg_cpc'),
                    avg_cpm=country_data.get('avg_cpm'),
                    competition_level=country_data.get('competition_level')
                ))
        
        return countries
    
    async def get_operating_systems(self) -> List[OS]:
        """
        Get available operating systems for targeting
        
        Returns:
            List of operating systems
        """
        logger.debug("Getting operating systems collection")
        
        response = await self._get('/adv/collections/operating-systems')
        
        operating_systems = []
        if 'data' in response:
            for os_data in response['data']:
                operating_systems.append(OS(
                    code=os_data.get('code', ''),
                    name=os_data.get('name', ''),
                    type=os_data.get('type', ''),
                    vendor=os_data.get('vendor'),
                    market_share=os_data.get('market_share'),
                    versions=os_data.get('versions', []),
                    latest_version=os_data.get('latest_version')
                ))
        
        return operating_systems
    
    async def get_os_versions(self, os_code: Optional[str] = None) -> List[OSVersion]:
        """
        Get available OS versions for targeting
        
        Args:
            os_code: Optional OS code filter
            
        Returns:
            List of OS versions
        """
        logger.debug(f"Getting OS versions collection (os_code: {os_code})")
        
        params = {}
        if os_code:
            params['os_code'] = os_code
        
        response = await self._get('/adv/collections/os-versions', params=params)
        
        os_versions = []
        if 'data' in response:
            for version_data in response['data']:
                os_versions.append(OSVersion(
                    code=version_data.get('code', ''),
                    name=version_data.get('name', ''),
                    os_code=version_data.get('os_code', ''),
                    release_date=version_data.get('release_date'),
                    market_share=version_data.get('market_share'),
                    is_supported=version_data.get('is_supported', True)
                ))
        
        return os_versions
    
    async def get_browsers(self) -> List[Browser]:
        """
        Get available browsers for targeting
        
        Returns:
            List of browsers
        """
        logger.debug("Getting browsers collection")
        
        response = await self._get('/adv/collections/browsers')
        
        browsers = []
        if 'data' in response:
            for browser_data in response['data']:
                browsers.append(Browser(
                    code=browser_data.get('code', ''),
                    name=browser_data.get('name', ''),
                    vendor=browser_data.get('vendor'),
                    market_share=browser_data.get('market_share'),
                    versions=browser_data.get('versions', []),
                    latest_version=browser_data.get('latest_version'),
                    supports_push=browser_data.get('supports_push', True),
                    supports_native=browser_data.get('supports_native', True),
                    supports_javascript=browser_data.get('supports_javascript', True)
                ))
        
        return browsers
    
    async def get_devices(self) -> List[Device]:
        """
        Get available devices for targeting
        
        Returns:
            List of devices
        """
        logger.debug("Getting devices collection")
        
        response = await self._get('/adv/collections/devices')
        
        devices = []
        if 'data' in response:
            for device_data in response['data']:
                devices.append(Device(
                    code=device_data.get('code', ''),
                    name=device_data.get('name', ''),
                    type=device_data.get('type', ''),
                    brand=device_data.get('brand'),
                    model=device_data.get('model'),
                    screen_width=device_data.get('screen_width'),
                    screen_height=device_data.get('screen_height'),
                    screen_density=device_data.get('screen_density'),
                    market_share=device_data.get('market_share'),
                    price_range=device_data.get('price_range')
                ))
        
        return devices
    
    async def get_carriers(self, country_code: Optional[str] = None) -> List[Carrier]:
        """
        Get available carriers for targeting
        
        Args:
            country_code: Optional country code filter
            
        Returns:
            List of carriers
        """
        logger.debug(f"Getting carriers collection (country: {country_code})")
        
        params = {}
        if country_code:
            params['country_code'] = country_code
        
        response = await self._get('/adv/collections/carriers', params=params)
        
        carriers = []
        if 'data' in response:
            for carrier_data in response['data']:
                carriers.append(Carrier(
                    code=carrier_data.get('code', ''),
                    name=carrier_data.get('name', ''),
                    country_code=carrier_data.get('country_code', ''),
                    type=carrier_data.get('type', ''),
                    market_share=carrier_data.get('market_share')
                ))
        
        return carriers
    
    async def get_zones(self, zone_type: Optional[str] = None) -> List[Zone]:
        """
        Get available zones for targeting
        
        Args:
            zone_type: Optional zone type filter
            
        Returns:
            List of zones
        """
        logger.debug(f"Getting zones collection (type: {zone_type})")
        
        params = {}
        if zone_type:
            params['type'] = zone_type
        
        response = await self._get('/adv/collections/zones', params=params)
        
        zones = []
        if 'data' in response:
            for zone_data in response['data']:
                zones.append(Zone(
                    id=zone_data.get('id', 0),
                    name=zone_data.get('name', ''),
                    type=zone_data.get('type', ''),
                    category=zone_data.get('category'),
                    avg_cpc=zone_data.get('avg_cpc'),
                    avg_cpm=zone_data.get('avg_cpm'),
                    quality_score=zone_data.get('quality_score'),
                    countries=zone_data.get('countries', []),
                    languages=zone_data.get('languages', []),
                    categories=zone_data.get('categories', []),
                    is_active=zone_data.get('is_active', True),
                    is_premium=zone_data.get('is_premium', False)
                ))
        
        return zones
    
    async def get_languages(self) -> List[Language]:
        """
        Get available languages for targeting
        
        Returns:
            List of languages
        """
        logger.debug("Getting languages collection")
        
        response = await self._get('/adv/collections/languages')
        
        languages = []
        if 'data' in response:
            for lang_data in response['data']:
                languages.append(Language(
                    code=lang_data.get('code', ''),
                    name=lang_data.get('name', ''),
                    native_name=lang_data.get('native_name'),
                    countries=lang_data.get('countries', []),
                    speakers=lang_data.get('speakers'),
                    market_size=lang_data.get('market_size'),
                    competition=lang_data.get('competition')
                ))
        
        return languages
    
    async def get_user_activity_levels(self) -> List[UserActivityLevel]:
        """
        Get available user activity levels for targeting
        
        Returns:
            List of user activity levels
        """
        logger.debug("Getting user activity levels collection")
        
        response = await self._get('/adv/collections/user-activity-levels')
        
        activity_levels = []
        if 'data' in response:
            for level_data in response['data']:
                activity_levels.append(UserActivityLevel(
                    level=level_data.get('level', 1),
                    name=level_data.get('name', ''),
                    description=level_data.get('description'),
                    avg_session_duration=level_data.get('avg_session_duration'),
                    avg_pages_per_session=level_data.get('avg_pages_per_session'),
                    bounce_rate=level_data.get('bounce_rate'),
                    conversion_rate=level_data.get('conversion_rate')
                ))
        
        return activity_levels
    
    async def get_all_targeting_options(self) -> TargetingOptions:
        """
        Get all targeting options in one request
        
        Returns:
            Complete targeting options
        """
        logger.info("Getting all targeting options")
        
        # Make parallel requests for all collections
        import asyncio
        
        countries_task = self.get_countries()
        os_task = self.get_operating_systems()
        browsers_task = self.get_browsers()
        devices_task = self.get_devices()
        languages_task = self.get_languages()
        activity_levels_task = self.get_user_activity_levels()
        
        # Wait for all requests to complete
        countries, operating_systems, browsers, devices, languages, user_activity_levels = await asyncio.gather(
            countries_task,
            os_task,
            browsers_task,
            devices_task,
            languages_task,
            activity_levels_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(countries, Exception):
            logger.warning(f"Failed to get countries: {countries}")
            countries = []
        
        if isinstance(operating_systems, Exception):
            logger.warning(f"Failed to get operating systems: {operating_systems}")
            operating_systems = []
        
        if isinstance(browsers, Exception):
            logger.warning(f"Failed to get browsers: {browsers}")
            browsers = []
        
        if isinstance(devices, Exception):
            logger.warning(f"Failed to get devices: {devices}")
            devices = []
        
        if isinstance(languages, Exception):
            logger.warning(f"Failed to get languages: {languages}")
            languages = []
        
        if isinstance(user_activity_levels, Exception):
            logger.warning(f"Failed to get user activity levels: {user_activity_levels}")
            user_activity_levels = []
        
        return TargetingOptions(
            countries=countries,
            operating_systems=operating_systems,
            browsers=browsers,
            devices=devices,
            languages=languages,
            user_activity_levels=user_activity_levels,
            last_updated=datetime.now().isoformat(),
            version="2.0.0"
        )
