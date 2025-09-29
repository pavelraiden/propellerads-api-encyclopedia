# Task Pattern: Campaign Monitoring

## Context
- **Purpose**: Monitor campaign performance and detect issues
- **Prerequisites**: Active campaigns, monitoring permissions
- **Expected Outcome**: Performance insights and optimization recommendations

## Execution Flow

### 1. Initial State
**Required:**
- Active campaigns exist
- API access to statistics endpoint
- Monitoring time range defined

### 2. Operation Steps

```python
# Step 1: Get campaign list
campaigns = client.get_campaigns(status='active')

# Step 2: Collect performance data
for campaign in campaigns['data']['result']:
    campaign_id = campaign['campaign_id']
    
    # Get statistics
    stats = client.get_statistics(
        campaign_id=campaign_id,
        day_from="2025-09-01 00:00:00",
        day_to="2025-09-30 23:59:59",
        tz="+0000"
    )
    
    # Analyze performance
    if stats['success']:
        performance = analyze_campaign_performance(stats['data'])
        
        # Generate recommendations
        recommendations = generate_recommendations(performance)
        
        print(f"Campaign {campaign_id}: {performance['status']}")
        for rec in recommendations:
            print(f"  💡 {rec}")
```

### 3. Performance Analysis

```python
def analyze_campaign_performance(stats_data):
    """Analyze campaign performance metrics"""
    
    metrics = {
        'impressions': stats_data.get('impressions', 0),
        'clicks': stats_data.get('clicks', 0),
        'conversions': stats_data.get('conversions', 0),
        'spend': stats_data.get('spend', 0),
        'ctr': 0,
        'cpc': 0,
        'roi': 0
    }
    
    # Calculate derived metrics
    if metrics['impressions'] > 0:
        metrics['ctr'] = metrics['clicks'] / metrics['impressions'] * 100
    
    if metrics['clicks'] > 0:
        metrics['cpc'] = metrics['spend'] / metrics['clicks']
    
    if metrics['spend'] > 0:
        metrics['roi'] = (metrics['conversions'] * 10 - metrics['spend']) / metrics['spend'] * 100
    
    # Determine status
    if metrics['ctr'] < 0.5:
        status = 'LOW_CTR'
    elif metrics['cpc'] > 1.0:
        status = 'HIGH_CPC'
    elif metrics['roi'] < 10:
        status = 'LOW_ROI'
    else:
        status = 'HEALTHY'
    
    return {
        'metrics': metrics,
        'status': status
    }
```

## Error Recovery
- API timeout: Retry with exponential backoff
- Missing data: Use default values or skip analysis
- Rate limits: Queue monitoring tasks

## Related Patterns
- [Campaign Optimization](campaign_optimization.md)
- [Budget Adjustment](budget_adjustment.md)
- [Alert Management](alert_management.md)
