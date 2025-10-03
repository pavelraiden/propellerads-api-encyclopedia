#!/usr/bin/env python3
"""
Comprehensive PropellerAds API Service

This module provides complete access to all PropellerAds API endpoints
with proper error handling, validation, and context management.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import aiohttp
import asyncio
from propellerads.client import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError


class CampaignDirection(Enum):
    """Campaign direction types"""
    ONCLICK = "onclick"
    PUSH = "nativeads"
    IN_PAGE_PUSH = "nativeads"


class RateModel(Enum):
    """Rate model types"""
    CPM = "cpm"
    CPC = "cpc"
    CPA = "cpa"
    SCPA = "scpa"  # Smart CPA Goal
    SCPM = "scpm"  # Smart CPM
    CPAG = "cpag"  # CPA Goal


class CampaignStatus(Enum):
    """Campaign status types"""
    DRAFT = 1
    MODERATION_PENDING = 2
    REJECTED = 3
    ACTIVE = 4
    PAUSED = 5
    ARCHIVED = 6


@dataclass
class CampaignContext:
    """Context for campaign-specific operations"""
    campaign_id: int
    campaign_name: str
    current_status: int
    rate_model: str
    direction: str
    user_session_id: str
    last_action: str
    timestamp: datetime


class PropellerAdsAPIService:
    """
    Comprehensive PropellerAds API Service
    
    Provides access to all PropellerAds API endpoints with:
    - Complete CRUD operations for campaigns
    - Statistics and analytics
    - Targeting management
    - Creative management
    - Context-aware operations
    - Real-time updates
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the PropellerAds API service"""
        self.api_key = api_key or os.environ.get("MainAPI")
        if not self.api_key:
            raise ValueError("PropellerAds API key not found")
        
        self.client = PropellerAdsClient(
            api_key=self.api_key,
            timeout=30,
            max_retries=3,
            rate_limit=60
        )
        
        # Context management
        self.campaign_contexts: Dict[str, CampaignContext] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    # ==================== CAMPAIGN OPERATIONS ====================
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign with comprehensive validation
        
        Supports all campaign types:
        - Onclick CPM/CPC/CPA/SmartCPM
        - Push Notification CPA Goal/CPC
        - In-Page Push CPA Goal
        """
        try:
            # Validate required fields
            required_fields = ['name', 'direction', 'rate_model', 'target_url']
            missing_fields = [field for field in required_fields if not campaign_data.get(field)]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            # Prepare campaign data according to PropellerAds schema
            prepared_data = self._prepare_campaign_data(campaign_data)
            
            # Create campaign via API
            result = self.client.create_campaign(prepared_data)
            
            if result:
                campaign_id = result.get('id')
                
                # Store context for future operations
                context = CampaignContext(
                    campaign_id=campaign_id,
                    campaign_name=prepared_data['name'],
                    current_status=prepared_data.get('status', 1),
                    rate_model=prepared_data['rate_model'],
                    direction=prepared_data['direction'],
                    user_session_id=campaign_data.get('session_id', 'default'),
                    last_action='created',
                    timestamp=datetime.now()
                )
                self.campaign_contexts[str(campaign_id)] = context
                
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'campaign': result,
                    'message': f'Campaign "{prepared_data["name"]}" created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create campaign'
                }
                
        except PropellerAdsError as e:
            self.logger.error(f"PropellerAds API error: {str(e)}")
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    async def get_campaigns(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get campaigns list with optional filters"""
        try:
            params = {}
            
            if filters:
                if 'ids' in filters:
                    params['id[]'] = filters['ids']
                if 'statuses' in filters:
                    params['status[]'] = filters['statuses']
                if 'limit' in filters:
                    params['limit'] = filters['limit']
                if 'offset' in filters:
                    params['offset'] = filters['offset']
            
            campaigns = self.client.get_campaigns(**params)
            
            return {
                'success': True,
                'campaigns': campaigns,
                'count': len(campaigns) if campaigns else 0
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def get_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Get specific campaign details"""
        try:
            campaign = self.client.get_campaign(campaign_id)
            
            return {
                'success': True,
                'campaign': campaign
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def update_campaign(self, campaign_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign with context awareness"""
        try:
            # Get current context
            context = self.campaign_contexts.get(str(campaign_id))
            
            # Prepare update data
            prepared_data = self._prepare_campaign_update(update_data, context)
            
            # Update campaign via API
            result = self.client.update_campaign(campaign_id, prepared_data)
            
            # Update context
            if context:
                context.last_action = 'updated'
                context.timestamp = datetime.now()
            
            return {
                'success': True,
                'campaign': result,
                'message': f'Campaign {campaign_id} updated successfully'
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def delete_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Delete campaign"""
        try:
            result = self.client.delete_campaign(campaign_id)
            
            # Remove context
            if str(campaign_id) in self.campaign_contexts:
                del self.campaign_contexts[str(campaign_id)]
            
            return {
                'success': True,
                'message': f'Campaign {campaign_id} deleted successfully'
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    # ==================== CAMPAIGN STATUS OPERATIONS ====================
    
    async def start_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Start/activate campaign"""
        return await self._change_campaign_status(campaign_id, CampaignStatus.ACTIVE.value)
    
    async def pause_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Pause campaign"""
        return await self._change_campaign_status(campaign_id, CampaignStatus.PAUSED.value)
    
    async def archive_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Archive campaign"""
        return await self._change_campaign_status(campaign_id, CampaignStatus.ARCHIVED.value)
    
    async def _change_campaign_status(self, campaign_id: int, status: int) -> Dict[str, Any]:
        """Change campaign status"""
        try:
            result = self.client.update_campaign_status(campaign_id, status)
            
            # Update context
            context = self.campaign_contexts.get(str(campaign_id))
            if context:
                context.current_status = status
                context.last_action = f'status_changed_to_{status}'
                context.timestamp = datetime.now()
            
            status_names = {
                1: 'Draft',
                2: 'Moderation Pending',
                3: 'Rejected',
                4: 'Active',
                5: 'Paused',
                6: 'Archived'
            }
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'new_status': status,
                'status_name': status_names.get(status, 'Unknown'),
                'message': f'Campaign {campaign_id} status changed to {status_names.get(status, "Unknown")}'
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    # ==================== STATISTICS OPERATIONS ====================
    
    async def get_campaign_statistics(self, campaign_id: int, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Get campaign statistics"""
        try:
            params = {
                'campaign_id': campaign_id
            }
            
            if date_from:
                params['date_from'] = date_from
            if date_to:
                params['date_to'] = date_to
            
            stats = self.client.get_campaign_statistics(**params)
            
            return {
                'success': True,
                'statistics': stats,
                'campaign_id': campaign_id
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def get_account_statistics(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Get account-wide statistics"""
        try:
            params = {}
            
            if date_from:
                params['date_from'] = date_from
            if date_to:
                params['date_to'] = date_to
            
            stats = self.client.get_account_statistics(**params)
            
            return {
                'success': True,
                'statistics': stats
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    # ==================== TARGETING OPERATIONS ====================
    
    async def get_targeting_options(self, targeting_type: str) -> Dict[str, Any]:
        """Get targeting options (countries, devices, OS, etc.)"""
        try:
            if targeting_type == 'countries':
                options = self.client.get_countries()
            elif targeting_type == 'devices':
                options = self.client.get_devices()
            elif targeting_type == 'os':
                options = self.client.get_operating_systems()
            elif targeting_type == 'browsers':
                options = self.client.get_browsers()
            elif targeting_type == 'languages':
                options = self.client.get_languages()
            else:
                return {
                    'success': False,
                    'error': f'Unknown targeting type: {targeting_type}'
                }
            
            return {
                'success': True,
                'targeting_type': targeting_type,
                'options': options
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    # ==================== ZONE MANAGEMENT OPERATIONS ====================
    
    async def get_campaign_zones(self, campaign_id: int) -> Dict[str, Any]:
        """Get zones for specific campaign with performance data"""
        try:
            zones = self.client.get_campaign_zones(campaign_id)
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'zones': zones,
                'count': len(zones) if zones else 0
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def block_zones(self, campaign_id: int, zone_ids: List[int], reason: str = None) -> Dict[str, Any]:
        """Block zones in campaign (add to blacklist)"""
        try:
            # Get current campaign targeting
            campaign_result = await self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return campaign_result
            
            campaign = campaign_result['campaign']
            targeting = campaign.get('targeting', {})
            
            # Add zones to blacklist
            blocked_zones = targeting.get('blocked_zones', [])
            new_blocked_zones = list(set(blocked_zones + zone_ids))
            
            targeting['blocked_zones'] = new_blocked_zones
            
            # Update campaign
            update_result = await self.update_campaign(campaign_id, {'targeting': targeting})
            
            if update_result['success']:
                # Log the action
                self.logger.info(f"Blocked zones {zone_ids} in campaign {campaign_id}. Reason: {reason}")
                
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'blocked_zones': zone_ids,
                    'total_blocked': len(new_blocked_zones),
                    'reason': reason,
                    'message': f'Successfully blocked {len(zone_ids)} zones in campaign {campaign_id}'
                }
            else:
                return update_result
                
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def unblock_zones(self, campaign_id: int, zone_ids: List[int]) -> Dict[str, Any]:
        """Unblock zones in campaign (remove from blacklist)"""
        try:
            # Get current campaign targeting
            campaign_result = await self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return campaign_result
            
            campaign = campaign_result['campaign']
            targeting = campaign.get('targeting', {})
            
            # Remove zones from blacklist
            blocked_zones = targeting.get('blocked_zones', [])
            new_blocked_zones = [zone_id for zone_id in blocked_zones if zone_id not in zone_ids]
            
            targeting['blocked_zones'] = new_blocked_zones
            
            # Update campaign
            update_result = await self.update_campaign(campaign_id, {'targeting': targeting})
            
            if update_result['success']:
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'unblocked_zones': zone_ids,
                    'total_blocked': len(new_blocked_zones),
                    'message': f'Successfully unblocked {len(zone_ids)} zones in campaign {campaign_id}'
                }
            else:
                return update_result
                
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def set_zone_rates(self, campaign_id: int, zone_rates: Dict[int, float]) -> Dict[str, Any]:
        """Set individual rates for specific zones (for CPM/CPC campaigns)"""
        try:
            # Get current campaign
            campaign_result = await self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return campaign_result
            
            campaign = campaign_result['campaign']
            rate_model = campaign.get('rate_model', '')
            
            # Check if rate model supports zone-specific rates
            if rate_model not in ['cpm', 'cpc']:
                return {
                    'success': False,
                    'error': f'Zone-specific rates not supported for {rate_model} campaigns'
                }
            
            # Get current zone rates
            current_zone_rates = campaign.get('zone_rates', {})
            
            # Update zone rates
            for zone_id, rate in zone_rates.items():
                current_zone_rates[str(zone_id)] = rate
            
            # Update campaign
            update_result = await self.update_campaign(campaign_id, {'zone_rates': current_zone_rates})
            
            if update_result['success']:
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'updated_zones': list(zone_rates.keys()),
                    'zone_rates': zone_rates,
                    'message': f'Successfully updated rates for {len(zone_rates)} zones'
                }
            else:
                return update_result
                
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def get_zone_statistics(self, campaign_id: int, zone_id: int = None, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Get zone-specific statistics"""
        try:
            params = {
                'campaign_id': campaign_id,
                'group_by': 'zone'
            }
            
            if zone_id:
                params['zone_id'] = zone_id
            if date_from:
                params['date_from'] = date_from
            if date_to:
                params['date_to'] = date_to
            
            stats = self.client.get_statistics(**params)
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'zone_id': zone_id,
                'statistics': stats
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    async def analyze_zone_performance(self, campaign_id: int, min_impressions: int = 1000) -> Dict[str, Any]:
        """Analyze zone performance and provide optimization recommendations"""
        try:
            # Get zone statistics
            stats_result = await self.get_zone_statistics(campaign_id)
            if not stats_result['success']:
                return stats_result
            
            zone_stats = stats_result['statistics']
            
            recommendations = {
                'zones_to_block': [],
                'zones_to_increase_rates': [],
                'zones_to_decrease_rates': [],
                'high_performing_zones': []
            }
            
            for zone_data in zone_stats:
                zone_id = zone_data.get('zone_id')
                impressions = zone_data.get('impressions', 0)
                ctr = zone_data.get('ctr', 0)
                cr = zone_data.get('cr', 0)
                cpa = zone_data.get('cpa', 0)
                
                # Skip zones with insufficient data
                if impressions < min_impressions:
                    continue
                
                # Analyze performance
                if ctr < 0.005:  # CTR < 0.5%
                    recommendations['zones_to_block'].append({
                        'zone_id': zone_id,
                        'reason': f'Low CTR: {ctr:.3%}',
                        'impressions': impressions
                    })
                elif cr > 0.02:  # CR > 2%
                    recommendations['high_performing_zones'].append({
                        'zone_id': zone_id,
                        'ctr': ctr,
                        'cr': cr,
                        'impressions': impressions
                    })
                    recommendations['zones_to_increase_rates'].append({
                        'zone_id': zone_id,
                        'reason': f'High performance: CTR {ctr:.3%}, CR {cr:.3%}',
                        'suggested_increase': '20%'
                    })
                elif cpa > 50:  # High CPA
                    recommendations['zones_to_decrease_rates'].append({
                        'zone_id': zone_id,
                        'reason': f'High CPA: ${cpa:.2f}',
                        'suggested_decrease': '15%'
                    })
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'recommendations': recommendations,
                'total_zones_analyzed': len(zone_stats),
                'min_impressions_threshold': min_impressions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }
    
    async def auto_optimize_zones(self, campaign_id: int, apply_changes: bool = False) -> Dict[str, Any]:
        """Automatically optimize zones based on performance analysis"""
        try:
            # Get performance analysis
            analysis_result = await self.analyze_zone_performance(campaign_id)
            if not analysis_result['success']:
                return analysis_result
            
            recommendations = analysis_result['recommendations']
            actions_taken = []
            
            if apply_changes:
                # Block poor performing zones
                zones_to_block = [zone['zone_id'] for zone in recommendations['zones_to_block']]
                if zones_to_block:
                    block_result = await self.block_zones(
                        campaign_id, 
                        zones_to_block, 
                        "Auto-optimization: Poor performance"
                    )
                    if block_result['success']:
                        actions_taken.append(f"Blocked {len(zones_to_block)} poor performing zones")
                
                # Update rates for high-performing zones (if supported)
                campaign_result = await self.get_campaign(campaign_id)
                if campaign_result['success']:
                    rate_model = campaign_result['campaign'].get('rate_model', '')
                    
                    if rate_model in ['cpm', 'cpc']:
                        # Increase rates for high-performing zones
                        zone_rate_updates = {}
                        for zone in recommendations['zones_to_increase_rates']:
                            zone_id = zone['zone_id']
                            # Get current rate and increase by 20%
                            current_rate = 1.0  # Default rate, should get from campaign
                            new_rate = current_rate * 1.2
                            zone_rate_updates[zone_id] = new_rate
                        
                        if zone_rate_updates:
                            rate_result = await self.set_zone_rates(campaign_id, zone_rate_updates)
                            if rate_result['success']:
                                actions_taken.append(f"Increased rates for {len(zone_rate_updates)} high-performing zones")
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'recommendations': recommendations,
                'actions_taken': actions_taken,
                'applied_changes': apply_changes,
                'message': 'Zone optimization analysis completed' + (
                    f'. Applied {len(actions_taken)} optimizations.' if apply_changes else '. Use apply_changes=True to apply recommendations.'
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Auto-optimization error: {str(e)}'
            }

    # ==================== ACCOUNT OPERATIONS ====================
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            balance = self.client.get_balance()
            
            return {
                'success': True,
                'balance': balance
            }
            
        except PropellerAdsError as e:
            return {
                'success': False,
                'error': f'API error: {str(e)}'
            }
    
    # ==================== CONTEXT MANAGEMENT ====================
    
    def set_campaign_context(self, campaign_id: int, session_id: str) -> CampaignContext:
        """Set context for campaign-specific operations"""
        try:
            # Get campaign details
            campaign_result = asyncio.run(self.get_campaign(campaign_id))
            
            if campaign_result['success']:
                campaign = campaign_result['campaign']
                
                context = CampaignContext(
                    campaign_id=campaign_id,
                    campaign_name=campaign.get('name', f'Campaign {campaign_id}'),
                    current_status=campaign.get('status', 1),
                    rate_model=campaign.get('rate_model', 'unknown'),
                    direction=campaign.get('direction', 'unknown'),
                    user_session_id=session_id,
                    last_action='context_set',
                    timestamp=datetime.now()
                )
                
                self.campaign_contexts[str(campaign_id)] = context
                return context
            else:
                raise Exception(f"Failed to get campaign details: {campaign_result['error']}")
                
        except Exception as e:
            self.logger.error(f"Failed to set campaign context: {str(e)}")
            raise
    
    def get_campaign_context(self, campaign_id: int) -> Optional[CampaignContext]:
        """Get campaign context"""
        return self.campaign_contexts.get(str(campaign_id))
    
    def clear_campaign_context(self, campaign_id: int):
        """Clear campaign context"""
        if str(campaign_id) in self.campaign_contexts:
            del self.campaign_contexts[str(campaign_id)]
    
    # ==================== HELPER METHODS ====================
    
    def _prepare_campaign_data(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare campaign data according to PropellerAds API schema"""
        # Set default values and format according to API requirements
        start_date = datetime.now().strftime('%d/%m/%Y')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
        
        prepared_data = {
            'name': campaign_data.get('name'),
            'direction': campaign_data.get('direction', 'onclick'),
            'rate_model': campaign_data.get('rate_model', 'cpm'),
            'target_url': campaign_data.get('target_url'),
            'status': campaign_data.get('status', 1),  # Draft by default
            'started_at': campaign_data.get('started_at', start_date),
            'expired_at': campaign_data.get('expired_at', end_date),
            'timezone': campaign_data.get('timezone', 0),  # UTC
            'allow_zone_update': campaign_data.get('allow_zone_update', True)
        }
        
        # Add optional fields based on campaign type
        if campaign_data.get('frequency'):
            prepared_data['frequency'] = campaign_data['frequency']
        if campaign_data.get('capping'):
            prepared_data['capping'] = campaign_data['capping']
        if campaign_data.get('daily_amount'):
            prepared_data['daily_amount'] = campaign_data['daily_amount']
        if campaign_data.get('total_amount'):
            prepared_data['total_amount'] = campaign_data['total_amount']
        if campaign_data.get('is_adblock_buy') is not None:
            prepared_data['is_adblock_buy'] = campaign_data['is_adblock_buy']
        
        # Add targeting
        if campaign_data.get('targeting'):
            prepared_data['targeting'] = campaign_data['targeting']
        
        # Add rates
        if campaign_data.get('rates'):
            prepared_data['rates'] = campaign_data['rates']
        
        # Add creatives for push campaigns
        if campaign_data.get('creatives'):
            prepared_data['creatives'] = campaign_data['creatives']
        
        return prepared_data
    
    def _prepare_campaign_update(self, update_data: Dict[str, Any], context: CampaignContext = None) -> Dict[str, Any]:
        """Prepare campaign update data with context awareness"""
        prepared_data = {}
        
        # Only include fields that are being updated
        updatable_fields = [
            'name', 'target_url', 'status', 'frequency', 'capping',
            'daily_amount', 'total_amount', 'targeting', 'rates', 'creatives'
        ]
        
        for field in updatable_fields:
            if field in update_data:
                prepared_data[field] = update_data[field]
        
        return prepared_data
    
    # ==================== VALIDATION METHODS ====================
    
    def validate_campaign_data(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate campaign data before API call"""
        errors = []
        
        # Required fields validation
        required_fields = ['name', 'direction', 'rate_model', 'target_url']
        for field in required_fields:
            if not campaign_data.get(field):
                errors.append(f'Missing required field: {field}')
        
        # Direction validation
        if campaign_data.get('direction') not in [d.value for d in CampaignDirection]:
            errors.append(f'Invalid direction: {campaign_data.get("direction")}')
        
        # Rate model validation
        if campaign_data.get('rate_model') not in [r.value for r in RateModel]:
            errors.append(f'Invalid rate model: {campaign_data.get("rate_model")}')
        
        # URL validation
        target_url = campaign_data.get('target_url', '')
        if target_url and not target_url.startswith(('http://', 'https://')):
            errors.append('Target URL must start with http:// or https://')
        
        # Budget validation
        if campaign_data.get('daily_amount') and campaign_data['daily_amount'] <= 0:
            errors.append('Daily amount must be greater than 0')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
