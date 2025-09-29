# Task Pattern: Budget Management

## Context
- **Purpose**: Monitor and manage campaign budgets automatically
- **Prerequisites**: Active campaigns, budget thresholds defined
- **Expected Outcome**: Optimized budget allocation and spend control

## Execution Flow

### 1. Budget Monitoring

```python
def monitor_budget_health(client):
    """Monitor overall account and campaign budgets"""
    
    # Check account balance
    balance = client.get_balance()
    account_balance = float(balance['data'])
    
    # Get active campaigns
    campaigns = client.get_campaigns(status='active')
    
    budget_analysis = {
        'account_balance': account_balance,
        'total_daily_budget': 0,
        'campaigns_at_risk': [],
        'recommendations': []
    }
    
    for campaign in campaigns['data']['result']:
        daily_budget = campaign.get('daily_budget', 0)
        budget_analysis['total_daily_budget'] += daily_budget
        
        # Check if campaign is at risk
        if daily_budget > account_balance * 0.1:  # More than 10% of balance
            budget_analysis['campaigns_at_risk'].append({
                'id': campaign['campaign_id'],
                'name': campaign['name'],
                'daily_budget': daily_budget,
                'risk_level': 'HIGH'
            })
    
    # Generate recommendations
    if account_balance < budget_analysis['total_daily_budget'] * 3:
        budget_analysis['recommendations'].append(
            "LOW_BALANCE: Account balance low for current daily spend"
        )
    
    return budget_analysis
```

### 2. Automatic Budget Adjustment

```python
def adjust_campaign_budgets(client, adjustment_rules):
    """Automatically adjust campaign budgets based on performance"""
    
    for rule in adjustment_rules:
        campaigns = client.get_campaigns(
            status='active',
            campaign_id=rule.get('campaign_id')
        )
        
        for campaign in campaigns['data']['result']:
            # Get recent performance
            stats = client.get_statistics(
                campaign_id=campaign['campaign_id'],
                day_from=rule['analysis_period']['start'],
                day_to=rule['analysis_period']['end']
            )
            
            # Calculate adjustment
            adjustment = calculate_budget_adjustment(
                stats['data'], 
                rule['performance_targets']
            )
            
            if adjustment['action'] != 'NONE':
                # Apply budget change
                result = client.update_campaign(
                    campaign_id=campaign['campaign_id'],
                    daily_budget=adjustment['new_budget']
                )
                
                print(f"Budget adjusted for {campaign['name']}: {adjustment}")
```

## Error Recovery
- Budget update failures: Retry with validation
- Insufficient permissions: Log and alert
- API errors: Fallback to manual review

## Related Patterns
- [Performance Optimization](performance_optimization.md)
- [Alert Management](alert_management.md)
