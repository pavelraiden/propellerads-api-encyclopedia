# 📚 API Reference

This document provides a complete reference for the PropellerAds API Encyclopedia.

## `EnhancedPropellerAdsClient`

Enhanced PropellerAds SSP API v5 Client with complete endpoint coverage.

Features:
- Complete API endpoint coverage
- Modular API classes
- Intelligent retry with exponential backoff
- Rate limiting with token bucket algorithm
- Circuit breaker pattern
- Comprehensive error handling
- Request/response logging
- Metrics collection
- Connection pooling
- Pydantic schema validation

### `Balance` API

#### `close`

```python
close()
```
Close HTTP session

#### `delete_budget_alert`

```python
delete_budget_alert(alert_id: int) -> bool
```
Delete budget alert

Args:
    alert_id: Alert ID to delete
    
Returns:
    True if deleted successfully

#### `get_balance`

```python
get_balance()
```
Get current account balance

Returns:
    Current balance information

#### `get_budget_alerts`

```python
get_budget_alerts() -> List[Dict[str, Any]]
```
Get configured budget alerts

Returns:
    List of budget alerts

#### `get_financial_summary`

```python
get_financial_summary(date_from: str, date_to: str) -> propellerads.schemas.balance.FinancialSummary
```
Get financial summary for date range

Args:
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    
Returns:
    Financial summary

#### `get_spending_forecast`

```python
get_spending_forecast(days: int = 30) -> Dict[str, Any]
```
Get spending forecast based on current campaigns

Args:
    days: Number of days to forecast
    
Returns:
    Spending forecast data

#### `get_stats`

```python
get_stats() -> Dict[str, Any]
```
Get API usage statistics

#### `get_transactions`

```python
get_transactions(date_from: Optional[str] = None, date_to: Optional[str] = None, transaction_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[propellerads.schemas.balance.Transaction]
```
Get transaction history

Args:
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    transaction_type: Filter by type (deposit, withdrawal, spend, refund)
    limit: Maximum number of transactions
    offset: Offset for pagination
    
Returns:
    List of transactions

#### `set_budget_alert`

```python
set_budget_alert(threshold: float, alert_type: str = 'email') -> Dict[str, Any]
```
Set budget alert threshold

Args:
    threshold: Budget threshold amount
    alert_type: Alert type (email, webhook)
    
Returns:
    Alert configuration

### `Campaigns` API

#### `clone_campaign`

```python
clone_campaign(campaign_id: int, new_name: Optional[str] = None) -> propellerads.schemas.campaign.Campaign
```
Clone existing campaign

Args:
    campaign_id: Campaign ID to clone
    new_name: Optional new name for cloned campaign
    
Returns:
    Cloned campaign

#### `close`

```python
close()
```
Close HTTP session

#### `create_campaign`

```python
create_campaign(campaign_data: propellerads.schemas.campaign.Campaign) -> propellerads.schemas.campaign.Campaign
```
Create a new campaign

Args:
    campaign_data: Campaign configuration
    
Returns:
    Created campaign with ID
    
Raises:
    PropellerAdsValidationError: If campaign data is invalid
    PropellerAdsAPIError: If API request fails

#### `delete_campaign`

```python
delete_campaign(campaign_id: int) -> bool
```
Delete campaign

Args:
    campaign_id: Campaign ID to delete
    
Returns:
    True if deleted successfully

#### `get_campaign`

```python
get_campaign(campaign_id: int) -> propellerads.schemas.campaign.Campaign
```
Get campaign by ID

Args:
    campaign_id: Campaign ID
    
Returns:
    Campaign data

#### `get_campaign_insights`

```python
get_campaign_insights(campaign_id: int) -> Dict[str, Any]
```
Get AI-powered insights for campaign

Args:
    campaign_id: Campaign ID
    
Returns:
    Campaign insights and recommendations

#### `get_campaign_performance`

```python
get_campaign_performance(campaign_id: int, date_from: str, date_to: str) -> Dict[str, Any]
```
Get campaign performance statistics

Args:
    campaign_id: Campaign ID
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    
Returns:
    Performance statistics

#### `get_campaigns`

```python
get_campaigns(limit: int = 100, offset: int = 0)
```
Get campaigns list (synchronous)

Args:
    limit: Maximum number of campaigns to return
    offset: Offset for pagination
    
Returns:
    List of campaigns

#### `get_stats`

```python
get_stats() -> Dict[str, Any]
```
Get API usage statistics

#### `list_campaigns`

```python
list_campaigns(filters: Optional[propellerads.schemas.campaign.CampaignFilters] = None) -> propellerads.schemas.campaign.CampaignResponse
```
List campaigns with optional filters

Args:
    filters: Optional filters for campaign listing
    
Returns:
    Campaign list response

#### `optimize_campaign`

```python
optimize_campaign(campaign_id: int, optimization_type: str = 'auto') -> Dict[str, Any]
```
Optimize campaign using AI recommendations

Args:
    campaign_id: Campaign ID to optimize
    optimization_type: Type of optimization (auto, bid, targeting, creative)
    
Returns:
    Optimization results and recommendations

#### `pause_campaign`

```python
pause_campaign(campaign_id: int) -> propellerads.schemas.campaign.Campaign
```
Pause campaign

Args:
    campaign_id: Campaign ID to pause
    
Returns:
    Updated campaign

#### `resume_campaign`

```python
resume_campaign(campaign_id: int) -> propellerads.schemas.campaign.Campaign
```
Resume paused campaign

Args:
    campaign_id: Campaign ID to resume
    
Returns:
    Updated campaign

#### `update_campaign`

```python
update_campaign(campaign_id: int, campaign_data: propellerads.schemas.campaign.Campaign) -> propellerads.schemas.campaign.Campaign
```
Update existing campaign

Args:
    campaign_id: Campaign ID to update
    campaign_data: Updated campaign data
    
Returns:
    Updated campaign

### `Statistics` API

#### `close`

```python
close()
```
Close HTTP session

#### `get_campaign_statistics`

```python
get_campaign_statistics(campaign_id: int, date_from: str, date_to: str, group_by: Optional[List[str]] = None) -> propellerads.schemas.statistics.Statistics
```
Get statistics for specific campaign

Args:
    campaign_id: Campaign ID
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    group_by: Optional grouping dimensions
    
Returns:
    Campaign statistics

#### `get_creative_statistics`

```python
get_creative_statistics(creative_id: int, date_from: str, date_to: str) -> propellerads.schemas.statistics.Statistics
```
Get statistics for specific creative

Args:
    creative_id: Creative ID
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    
Returns:
    Creative statistics

#### `get_performance_report`

```python
get_performance_report(date_from: str, date_to: str, campaign_ids: Optional[List[int]] = None) -> propellerads.schemas.statistics.PerformanceReport
```
Get comprehensive performance report

Args:
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    campaign_ids: Optional campaign IDs filter
    
Returns:
    Performance report with insights

#### `get_real_time_stats`

```python
get_real_time_stats(campaign_ids: Optional[List[int]] = None) -> Dict[str, Any]
```
Get real-time statistics (last 24 hours)

Args:
    campaign_ids: Optional campaign IDs filter
    
Returns:
    Real-time statistics

#### `get_statistics`

```python
get_statistics(date_from: str, date_to: str, group_by: Optional[List[str]] = None, campaign_ids: Optional[List[int]] = None)
```
Get statistics (synchronous)

Args:
    date_from: Start date (YYYY-MM-DD format)
    date_to: End date (YYYY-MM-DD format)
    group_by: Group by fields
    campaign_ids: Filter by campaign IDs
    
Returns:
    Statistics data

#### `get_statistics_async`

```python
get_statistics_async(filters: propellerads.schemas.statistics.StatisticsFilters) -> propellerads.schemas.statistics.Statistics
```
Get statistics data with filters

Args:
    filters: Statistics filters
    
Returns:
    Statistics response

#### `get_stats`

```python
get_stats() -> Dict[str, Any]
```
Get API usage statistics

#### `get_trend_analysis`

```python
get_trend_analysis(metric: str, date_from: str, date_to: str, campaign_id: Optional[int] = None) -> propellerads.schemas.statistics.TrendAnalysis
```
Get trend analysis for specific metric

Args:
    metric: Metric to analyze (impressions, clicks, conversions, spend, etc.)
    date_from: Start date (YYYY-MM-DD)
    date_to: End date (YYYY-MM-DD)
    campaign_id: Optional campaign ID filter
    
Returns:
    Trend analysis

### `Collections` API

#### `close`

```python
close()
```
Close HTTP session

#### `get_all_targeting_options`

```python
get_all_targeting_options() -> propellerads.schemas.collections.TargetingOptions
```
Get all targeting options in one request

Returns:
    Complete targeting options

#### `get_browsers`

```python
get_browsers() -> List[propellerads.schemas.collections.Browser]
```
Get available browsers for targeting

Returns:
    List of browsers

#### `get_carriers`

```python
get_carriers(country_code: Optional[str] = None) -> List[propellerads.schemas.collections.Carrier]
```
Get available carriers for targeting

Args:
    country_code: Optional country code filter
    
Returns:
    List of carriers

#### `get_countries`

```python
get_countries() -> List[propellerads.schemas.collections.Country]
```
Get available countries for targeting

Returns:
    List of countries

#### `get_devices`

```python
get_devices() -> List[propellerads.schemas.collections.Device]
```
Get available devices for targeting

Returns:
    List of devices

#### `get_languages`

```python
get_languages() -> List[propellerads.schemas.collections.Language]
```
Get available languages for targeting

Returns:
    List of languages

#### `get_operating_systems`

```python
get_operating_systems() -> List[propellerads.schemas.collections.OS]
```
Get available operating systems for targeting

Returns:
    List of operating systems

#### `get_os_versions`

```python
get_os_versions(os_code: Optional[str] = None) -> List[propellerads.schemas.collections.OSVersion]
```
Get available OS versions for targeting

Args:
    os_code: Optional OS code filter
    
Returns:
    List of OS versions

#### `get_stats`

```python
get_stats() -> Dict[str, Any]
```
Get API usage statistics

#### `get_targeting_options`

```python
get_targeting_options()
```
Get all targeting options (synchronous)

Returns:
    Dictionary with all targeting options

#### `get_user_activity_levels`

```python
get_user_activity_levels() -> List[propellerads.schemas.collections.UserActivityLevel]
```
Get available user activity levels for targeting

Returns:
    List of user activity levels

#### `get_zones`

```python
get_zones(zone_type: Optional[str] = None) -> List[propellerads.schemas.collections.Zone]
```
Get available zones for targeting

Args:
    zone_type: Optional zone type filter
    
Returns:
    List of zones

