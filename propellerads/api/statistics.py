"""
Statistics API implementation
"""

from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from .base import BaseAPI
from ..schemas.statistics import (
    Statistics, StatisticsFilters, StatisticsRow, 
    PerformanceReport, PerformanceInsight, TrendAnalysis
)

logger = logging.getLogger(__name__)


class StatisticsAPI(BaseAPI):
    """Statistics and analytics API"""
    
    def get_statistics(
        self,
        date_from: str,
        date_to: str,
        group_by: Optional[List[str]] = None,
        campaign_ids: Optional[List[int]] = None
    ):
        """
        Get statistics (synchronous)
        
        Args:
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            group_by: Group by fields
            campaign_ids: Filter by campaign IDs
            
        Returns:
            Statistics data
        """
        logger.debug(f"Getting statistics: {date_from} to {date_to}")
        
        params = {
            'day_from': date_from,
            'day_to': date_to,
            'tz': '+0000',
            'group_by[]': group_by or ['campaign_id']
        }
        
        if campaign_ids:
            params['campaign_id[]'] = campaign_ids
        
        response = self.client._make_request('GET', '/adv/statistics', params=params)
        return response.json()
    
    async def get_statistics_async(self, filters: StatisticsFilters) -> Statistics:
        """
        Get statistics data with filters
        
        Args:
            filters: Statistics filters
            
        Returns:
            Statistics response
        """
        logger.debug(f"Getting statistics: {filters.date_from} to {filters.date_to}")
        
        params = filters.to_api_dict()
        response = await self._get('/adv/statistics', params=params)
        
        # Parse statistics rows
        rows = []
        if 'data' in response:
            rows = [StatisticsRow.from_api_response(row) for row in response['data']]
        
        # Calculate summary if not provided
        summary = None
        if 'summary' in response:
            summary = StatisticsRow.from_api_response(response['summary'])
        elif rows:
            summary = self._calculate_summary(rows)
        
        return Statistics(
            data=rows,
            total_rows=response.get('total', len(rows)),
            summary=summary,
            date_from=filters.date_from,
            date_to=filters.date_to
        )
    
    async def get_campaign_statistics(
        self, 
        campaign_id: int, 
        date_from: str, 
        date_to: str,
        group_by: Optional[List[str]] = None
    ) -> Statistics:
        """
        Get statistics for specific campaign
        
        Args:
            campaign_id: Campaign ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            group_by: Optional grouping dimensions
            
        Returns:
            Campaign statistics
        """
        filters = StatisticsFilters(
            date_from=date_from,
            date_to=date_to,
            campaign_ids=[campaign_id],
            group_by=group_by
        )
        
        return await self.get_statistics(filters)
    
    async def get_creative_statistics(
        self, 
        creative_id: int, 
        date_from: str, 
        date_to: str
    ) -> Statistics:
        """
        Get statistics for specific creative
        
        Args:
            creative_id: Creative ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Creative statistics
        """
        filters = StatisticsFilters(
            date_from=date_from,
            date_to=date_to,
            creative_ids=[creative_id]
        )
        
        return await self.get_statistics(filters)
    
    async def get_performance_report(
        self, 
        date_from: str, 
        date_to: str,
        campaign_ids: Optional[List[int]] = None
    ) -> PerformanceReport:
        """
        Get comprehensive performance report
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            campaign_ids: Optional campaign IDs filter
            
        Returns:
            Performance report with insights
        """
        logger.info(f"Generating performance report: {date_from} to {date_to}")
        
        # Get overall statistics
        filters = StatisticsFilters(
            date_from=date_from,
            date_to=date_to,
            campaign_ids=campaign_ids,
            group_by=['campaign']
        )
        
        stats = await self.get_statistics(filters)
        
        # Calculate report metrics
        total_campaigns = len(set(row.campaign_id for row in stats.data if row.campaign_id))
        active_campaigns = len([row for row in stats.data if row.impressions > 0])
        
        total_spend = sum(row.spend for row in stats.data)
        total_revenue = sum(row.revenue for row in stats.data)
        overall_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
        
        # Get top performers
        top_campaigns = sorted(stats.data, key=lambda x: x.revenue, reverse=True)[:10]
        
        # Get country performance
        country_filters = StatisticsFilters(
            date_from=date_from,
            date_to=date_to,
            campaign_ids=campaign_ids,
            group_by=['country']
        )
        country_stats = await self.get_statistics(country_filters)
        top_countries = sorted(country_stats.data, key=lambda x: x.revenue, reverse=True)[:10]
        
        # Generate insights
        insights = await self._generate_insights(stats.data, date_from, date_to)
        
        return PerformanceReport(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            total_spend=total_spend,
            total_revenue=total_revenue,
            overall_roi=overall_roi,
            top_campaigns=top_campaigns,
            top_countries=top_countries,
            insights=insights,
            date_from=date_from,
            date_to=date_to
        )
    
    async def get_trend_analysis(
        self, 
        metric: str, 
        date_from: str, 
        date_to: str,
        campaign_id: Optional[int] = None
    ) -> TrendAnalysis:
        """
        Get trend analysis for specific metric
        
        Args:
            metric: Metric to analyze (impressions, clicks, conversions, spend, etc.)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            campaign_id: Optional campaign ID filter
            
        Returns:
            Trend analysis
        """
        logger.debug(f"Analyzing trend for metric: {metric}")
        
        # Get daily statistics
        filters = StatisticsFilters(
            date_from=date_from,
            date_to=date_to,
            campaign_ids=[campaign_id] if campaign_id else None,
            group_by=['date']
        )
        
        stats = await self.get_statistics(filters)
        
        # Extract metric values
        data_points = []
        values = []
        
        for row in sorted(stats.data, key=lambda x: x.date or ''):
            if hasattr(row, metric):
                value = getattr(row, metric, 0)
                data_points.append({
                    'date': str(row.date),
                    'value': float(value)
                })
                values.append(float(value))
        
        # Calculate trend
        trend_direction = 'stable'
        trend_strength = 0.0
        
        if len(values) >= 2:
            # Simple linear trend calculation
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            avg_first = sum(first_half) / len(first_half) if first_half else 0
            avg_second = sum(second_half) / len(second_half) if second_half else 0
            
            if avg_second > avg_first * 1.1:
                trend_direction = 'up'
                trend_strength = min((avg_second - avg_first) / avg_first, 1.0) if avg_first > 0 else 0
            elif avg_second < avg_first * 0.9:
                trend_direction = 'down'
                trend_strength = min((avg_first - avg_second) / avg_first, 1.0) if avg_first > 0 else 0
        
        # Calculate statistics
        avg_value = sum(values) / len(values) if values else 0
        min_value = min(values) if values else 0
        max_value = max(values) if values else 0
        
        # Simple variance calculation
        variance = sum((v - avg_value) ** 2 for v in values) / len(values) if values else 0
        
        return TrendAnalysis(
            metric=metric,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            data_points=data_points,
            average_value=avg_value,
            min_value=min_value,
            max_value=max_value,
            variance=variance
        )
    
    async def get_real_time_stats(self, campaign_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Get real-time statistics (last 24 hours)
        
        Args:
            campaign_ids: Optional campaign IDs filter
            
        Returns:
            Real-time statistics
        """
        logger.debug("Getting real-time statistics")
        
        # Get yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        filters = StatisticsFilters(
            date_from=yesterday,
            date_to=today,
            campaign_ids=campaign_ids
        )
        
        stats = await self.get_statistics(filters)
        
        return {
            'total_impressions': sum(row.impressions for row in stats.data),
            'total_clicks': sum(row.clicks for row in stats.data),
            'total_conversions': sum(row.conversions for row in stats.data),
            'total_spend': sum(row.spend for row in stats.data),
            'average_ctr': sum(row.ctr for row in stats.data) / len(stats.data) if stats.data else 0,
            'active_campaigns': len(set(row.campaign_id for row in stats.data if row.campaign_id and row.impressions > 0)),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_summary(self, rows: List[StatisticsRow]) -> StatisticsRow:
        """Calculate summary statistics from rows"""
        if not rows:
            return StatisticsRow()
        
        total_impressions = sum(row.impressions for row in rows)
        total_clicks = sum(row.clicks for row in rows)
        total_conversions = sum(row.conversions for row in rows)
        total_spend = sum(row.spend for row in rows)
        total_revenue = sum(row.revenue for row in rows)
        
        # Calculate averages
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
        profit = total_revenue - total_spend
        
        return StatisticsRow(
            impressions=total_impressions,
            clicks=total_clicks,
            conversions=total_conversions,
            spend=total_spend,
            revenue=total_revenue,
            ctr=ctr,
            cvr=cvr,
            cpc=cpc,
            cpm=cpm,
            cpa=cpa,
            roi=roi,
            profit=profit
        )
    
    async def _generate_insights(
        self, 
        data: List[StatisticsRow], 
        date_from: str, 
        date_to: str
    ) -> List[PerformanceInsight]:
        """Generate AI-powered insights from statistics data"""
        insights = []
        
        if not data:
            return insights
        
        # Calculate overall metrics
        total_spend = sum(row.spend for row in data)
        total_revenue = sum(row.revenue for row in data)
        total_clicks = sum(row.clicks for row in data)
        total_impressions = sum(row.impressions for row in data)
        
        # ROI Analysis
        if total_spend > 0:
            roi = (total_revenue - total_spend) / total_spend * 100
            
            if roi > 50:
                insights.append(PerformanceInsight(
                    type="trend",
                    title="Excellent ROI Performance",
                    description=f"Your campaigns achieved {roi:.1f}% ROI, significantly above industry average.",
                    severity="info",
                    confidence=0.9,
                    metric="roi",
                    value=roi,
                    recommended_action="Consider increasing budget for high-performing campaigns"
                ))
            elif roi < 0:
                insights.append(PerformanceInsight(
                    type="alert",
                    title="Negative ROI Detected",
                    description=f"Your campaigns have negative ROI ({roi:.1f}%). Immediate optimization needed.",
                    severity="critical",
                    confidence=0.95,
                    metric="roi",
                    value=roi,
                    recommended_action="Pause underperforming campaigns and optimize targeting"
                ))
        
        # CTR Analysis
        if total_impressions > 0:
            ctr = total_clicks / total_impressions * 100
            
            if ctr < 0.5:
                insights.append(PerformanceInsight(
                    type="recommendation",
                    title="Low Click-Through Rate",
                    description=f"Your CTR is {ctr:.2f}%, which is below industry benchmarks.",
                    severity="warning",
                    confidence=0.8,
                    metric="ctr",
                    value=ctr,
                    recommended_action="Test new creative variations and optimize ad copy"
                ))
        
        # Top Performer Analysis
        if len(data) > 1:
            top_campaign = max(data, key=lambda x: x.revenue)
            if top_campaign.revenue > 0:
                insights.append(PerformanceInsight(
                    type="trend",
                    title="Top Performing Campaign Identified",
                    description=f"Campaign {top_campaign.campaign_id} generated ${top_campaign.revenue:.2f} revenue.",
                    severity="info",
                    confidence=0.85,
                    campaign_id=top_campaign.campaign_id,
                    metric="revenue",
                    value=top_campaign.revenue,
                    recommended_action="Scale this campaign by increasing budget and expanding targeting"
                ))
        
        return insights
