"""
Campaigns API implementation
"""

from typing import List, Optional, Dict, Any
import logging

from .base import BaseAPI
from ..schemas.campaign import Campaign, CampaignFilters, CampaignResponse
from ..exceptions import PropellerAdsValidationError

logger = logging.getLogger(__name__)


class CampaignAPI(BaseAPI):
    """Campaign management API"""
    
    async def create_campaign(self, campaign_data: Campaign) -> Campaign:
        """
        Create a new campaign
        
        Args:
            campaign_data: Campaign configuration
            
        Returns:
            Created campaign with ID
            
        Raises:
            PropellerAdsValidationError: If campaign data is invalid
            PropellerAdsAPIError: If API request fails
        """
        logger.info(f"Creating campaign: {campaign_data.name}")
        
        # Validate campaign data
        self._validate_campaign_data(campaign_data)
        
        # Convert to API format
        api_data = campaign_data.to_api_dict()
        
        # Make API request
        response = await self._post('/adv/campaigns', data=api_data)
        
        # Parse response
        created_campaign = Campaign.from_api_response(response)
        
        logger.info(f"Campaign created successfully: ID {created_campaign.id}")
        return created_campaign
    
    async def get_campaign(self, campaign_id: int) -> Campaign:
        """
        Get campaign by ID
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign data
        """
        logger.debug(f"Getting campaign: {campaign_id}")
        
        response = await self._get(f'/adv/campaigns/{campaign_id}')
        return Campaign.from_api_response(response)
    
    def get_campaigns(self, limit: int = 100, offset: int = 0):
        """
        Get campaigns list (synchronous)
        
        Args:
            limit: Maximum number of campaigns to return
            offset: Offset for pagination
            
        Returns:
            List of campaigns
        """
        logger.debug(f"Getting campaigns: limit={limit}, offset={offset}")
        
        params = {'limit': limit, 'offset': offset}
        response = self.client._make_request('GET', '/adv/campaigns', params=params)
        return response.json()
    
    async def list_campaigns(self, filters: Optional[CampaignFilters] = None) -> CampaignResponse:
        """
        List campaigns with optional filters
        
        Args:
            filters: Optional filters for campaign listing
            
        Returns:
            Campaign list response
        """
        logger.debug("Listing campaigns")
        
        params = {}
        if filters:
            params = filters.to_api_dict()
        
        response = await self._get('/adv/campaigns', params=params)
        
        # Parse campaigns
        campaigns = []
        if 'data' in response:
            campaigns = [Campaign.from_api_response(camp) for camp in response['data']]
        
        return CampaignResponse(
            data=campaigns,
            total=response.get('total', len(campaigns)),
            limit=response.get('limit', len(campaigns)),
            offset=response.get('offset', 0)
        )
    
    async def update_campaign(self, campaign_id: int, campaign_data: Campaign) -> Campaign:
        """
        Update existing campaign
        
        Args:
            campaign_id: Campaign ID to update
            campaign_data: Updated campaign data
            
        Returns:
            Updated campaign
        """
        logger.info(f"Updating campaign: {campaign_id}")
        
        # Validate campaign data
        self._validate_campaign_data(campaign_data)
        
        # Convert to API format
        api_data = campaign_data.to_api_dict()
        
        # Make API request
        response = await self._put(f'/adv/campaigns/{campaign_id}', data=api_data)
        
        # Parse response
        updated_campaign = Campaign.from_api_response(response)
        
        logger.info(f"Campaign updated successfully: ID {campaign_id}")
        return updated_campaign
    
    async def delete_campaign(self, campaign_id: int) -> bool:
        """
        Delete campaign
        
        Args:
            campaign_id: Campaign ID to delete
            
        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting campaign: {campaign_id}")
        
        await self._delete(f'/adv/campaigns/{campaign_id}')
        
        logger.info(f"Campaign deleted successfully: ID {campaign_id}")
        return True
    
    async def pause_campaign(self, campaign_id: int) -> Campaign:
        """
        Pause campaign
        
        Args:
            campaign_id: Campaign ID to pause
            
        Returns:
            Updated campaign
        """
        logger.info(f"Pausing campaign: {campaign_id}")
        
        response = await self._post(f'/adv/campaigns/{campaign_id}/pause')
        return Campaign.from_api_response(response)
    
    async def resume_campaign(self, campaign_id: int) -> Campaign:
        """
        Resume paused campaign
        
        Args:
            campaign_id: Campaign ID to resume
            
        Returns:
            Updated campaign
        """
        logger.info(f"Resuming campaign: {campaign_id}")
        
        response = await self._post(f'/adv/campaigns/{campaign_id}/resume')
        return Campaign.from_api_response(response)
    
    async def clone_campaign(self, campaign_id: int, new_name: Optional[str] = None) -> Campaign:
        """
        Clone existing campaign
        
        Args:
            campaign_id: Campaign ID to clone
            new_name: Optional new name for cloned campaign
            
        Returns:
            Cloned campaign
        """
        logger.info(f"Cloning campaign: {campaign_id}")
        
        data = {}
        if new_name:
            data['name'] = new_name
        
        response = await self._post(f'/adv/campaigns/{campaign_id}/clone', data=data)
        
        cloned_campaign = Campaign.from_api_response(response)
        logger.info(f"Campaign cloned successfully: ID {cloned_campaign.id}")
        return cloned_campaign
    
    async def get_campaign_performance(self, campaign_id: int, date_from: str, date_to: str) -> Dict[str, Any]:
        """
        Get campaign performance statistics
        
        Args:
            campaign_id: Campaign ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Performance statistics
        """
        logger.debug(f"Getting performance for campaign: {campaign_id}")
        
        params = {
            'date_from': date_from,
            'date_to': date_to
        }
        
        return await self._get(f'/adv/campaigns/{campaign_id}/performance', params=params)
    
    async def optimize_campaign(self, campaign_id: int, optimization_type: str = 'auto') -> Dict[str, Any]:
        """
        Optimize campaign using AI recommendations
        
        Args:
            campaign_id: Campaign ID to optimize
            optimization_type: Type of optimization (auto, bid, targeting, creative)
            
        Returns:
            Optimization results and recommendations
        """
        logger.info(f"Optimizing campaign: {campaign_id} (type: {optimization_type})")
        
        data = {'type': optimization_type}
        response = await self._post(f'/adv/campaigns/{campaign_id}/optimize', data=data)
        
        logger.info(f"Campaign optimization completed: {campaign_id}")
        return response
    
    async def get_campaign_insights(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get AI-powered insights for campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign insights and recommendations
        """
        logger.debug(f"Getting insights for campaign: {campaign_id}")
        
        return await self._get(f'/adv/campaigns/{campaign_id}/insights')
    
    def _validate_campaign_data(self, campaign_data: Campaign):
        """
        Validate campaign data before API request
        
        Args:
            campaign_data: Campaign to validate
            
        Raises:
            PropellerAdsValidationError: If validation fails
        """
        errors = []
        
        # Validate required fields
        if not campaign_data.name or len(campaign_data.name.strip()) == 0:
            errors.append("Campaign name is required")
        
        if not campaign_data.target_url:
            errors.append("Target URL is required")
        
        if not campaign_data.rates or len(campaign_data.rates) == 0:
            errors.append("At least one rate configuration is required")
        
        # Validate targeting
        if not campaign_data.targeting:
            errors.append("Targeting configuration is required")
        elif not campaign_data.targeting.country or len(campaign_data.targeting.country.list) == 0:
            errors.append("At least one target country is required")
        
        # Validate budget constraints
        if campaign_data.daily_amount and campaign_data.total_amount:
            if campaign_data.daily_amount >= campaign_data.total_amount:
                errors.append("Daily amount must be less than total amount")
        
        # Validate CPA/SCPA requirements
        if campaign_data.rate_model in ['scpa', 'cpag']:
            if '${SUBID}' not in campaign_data.target_url:
                errors.append("CPA & SCPA rate models must have ${SUBID} macro in target URL")
        
        if errors:
            raise PropellerAdsValidationError("Campaign validation failed", details={'errors': errors})
