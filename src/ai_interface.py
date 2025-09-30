"""
PropellerAds AI Interface Layer
High-level interface optimized for AI agents
"""

import yaml
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class PropellerAdsAIInterface:
    """High-level interface for AI agents working with PropellerAds"""
    
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.task_patterns = self._load_task_patterns()
        self.constraints = self._load_constraints()
    
    def process_natural_language_command(self, command: str, confirm_write_operations: bool = True) -> Dict[str, Any]:
        """Process natural language commands"""
        try:
            command_lower = command.lower().strip()
            
            # Balance queries
            if any(word in command_lower for word in ['balance', 'money', 'funds', 'account']):
                balance = self.client.balance.get_balance() if hasattr(self.client, 'balance') else self.client.get_balance()
                return {
                    "action": "get_balance",
                    "result": balance,
                    "message": f"Your current balance is {balance}"
                }
            
            # Campaign queries
            elif any(word in command_lower for word in ['campaigns', 'campaign']):
                if 'list' in command_lower or 'show' in command_lower:
                    campaigns = self.client.campaigns.get_campaigns() if hasattr(self.client, 'campaigns') else self.client.get_campaigns()
                    count = len(campaigns) if isinstance(campaigns, list) else 0
                    return {
                        "action": "list_campaigns",
                        "result": campaigns,
                        "message": f"Found {count} campaigns"
                    }
            
            # Statistics queries
            elif any(word in command_lower for word in ['stats', 'statistics', 'performance']):
                stats = self.client.statistics.get_statistics() if hasattr(self.client, 'statistics') else []
                return {
                    "action": "get_statistics",
                    "result": stats,
                    "message": "Retrieved performance statistics"
                }
            
            # Health check
            elif any(word in command_lower for word in ['health', 'status', 'check']):
                health = self.client.health_check() if hasattr(self.client, 'health_check') else {"status": "unknown"}
                return {
                    "action": "health_check",
                    "result": health,
                    "message": f"API status: {health.get('status', 'unknown')}"
                }
            
            else:
                return {
                    "action": "unknown",
                    "result": None,
                    "message": f"I don't understand the command: '{command}'. Try asking about balance, campaigns, statistics, or health."
                }
                
        except Exception as e:
            return {
                "action": "error",
                "result": None,
                "message": f"Error processing command: {str(e)}"
            }
    
    def _load_task_patterns(self) -> Dict:
        """Load task patterns from metadata"""
        try:
            with open('docs/metadata/tasks.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load task patterns: {e}")
            return {}
    
    def _load_constraints(self) -> Dict:
        """Load system constraints from metadata"""
        try:
            with open('docs/metadata/constraints.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load constraints: {e}")
            return {}
    
    def execute_task_pattern(self, pattern_name: str, params: Dict) -> Dict:
        """Execute a standardized task pattern"""
        
        self.logger.info(f"Executing task pattern: {pattern_name}")
        
        # Validate pattern exists
        if pattern_name not in self.task_patterns.get('tasks', {}):
            raise ValueError(f"Unknown task pattern: {pattern_name}")
        
        pattern = self.task_patterns['tasks'][pattern_name]
        
        # Validate parameters
        validation_result = self.validate_operation(pattern_name, params)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': validation_result['errors']
            }
        
        # Execute based on pattern type
        try:
            if pattern_name == 'campaign_creation':
                return self._execute_campaign_creation(params)
            elif pattern_name == 'campaign_monitoring':
                return self._execute_campaign_monitoring(params)
            elif pattern_name == 'budget_management':
                return self._execute_budget_management(params)
            else:
                raise NotImplementedError(f"Pattern {pattern_name} not implemented")
        
        except Exception as e:
            return self.handle_error(e, {'pattern': pattern_name, 'params': params})
    
    def validate_operation(self, operation_type: str, params: Dict) -> Dict:
        """Validate operations before execution"""
        
        errors = []
        
        if operation_type not in self.task_patterns.get('tasks', {}):
            errors.append(f"Unknown operation type: {operation_type}")
            return {'valid': False, 'errors': errors}
        
        pattern = self.task_patterns['tasks'][operation_type]
        
        # Check required parameters
        required_params = pattern.get('required_params', [])
        for param in required_params:
            if param not in params:
                errors.append(f"Missing required parameter: {param}")
        
        # Validate specific constraints
        if operation_type == 'campaign_creation':
            errors.extend(self._validate_campaign_creation(params))
        elif operation_type == 'budget_management':
            errors.extend(self._validate_budget_management(params))
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_campaign_creation(self, params: Dict) -> List[str]:
        """Validate campaign creation parameters"""
        errors = []
        
        # Budget validation
        if 'budget' in params:
            budget = params['budget']
            min_budget = self.constraints.get('business_constraints', {}).get('minimum_budget', 10)
            max_budget = self.constraints.get('business_constraints', {}).get('maximum_daily_budget', 10000)
            
            if not isinstance(budget, (int, float)):
                errors.append("Budget must be numeric")
            elif budget < min_budget:
                errors.append(f"Budget must be at least ${min_budget}")
            elif budget > max_budget:
                errors.append(f"Budget cannot exceed ${max_budget}")
        
        # Targeting validation
        if 'targeting' in params:
            targeting = params['targeting']
            if 'countries' in targeting:
                if not isinstance(targeting['countries'], list):
                    errors.append("Countries must be a list")
                elif len(targeting['countries']) == 0:
                    errors.append("At least one country must be specified")
        
        return errors
    
    def _validate_budget_management(self, params: Dict) -> List[str]:
        """Validate budget management parameters"""
        errors = []
        
        if 'adjustment_rules' not in params:
            errors.append("Budget management requires adjustment_rules")
        
        return errors
    
    def handle_error(self, error: Exception, context: Dict) -> Dict:
        """Standardized error handling for AI agents"""
        
        error_type = type(error).__name__
        error_message = str(error)
        
        self.logger.error(f"Error in AI interface: {error_type}: {error_message}", 
                         extra={'context': context})
        
        # Determine recovery strategy
        recovery_strategy = self._determine_recovery_strategy(error, context)
        
        return {
            'success': False,
            'error': error_type,
            'message': error_message,
            'context': context,
            'recovery_strategy': recovery_strategy,
            'timestamp': datetime.now().isoformat()
        }
    
    def _determine_recovery_strategy(self, error: Exception, context: Dict) -> Dict:
        """Determine appropriate recovery strategy"""
        
        error_type = type(error).__name__
        
        if 'RateLimit' in error_type:
            return {
                'strategy': 'exponential_backoff',
                'wait_time': 60,
                'max_retries': 3
            }
        elif 'Authentication' in error_type:
            return {
                'strategy': 'check_credentials',
                'action': 'verify_api_key'
            }
        elif 'Validation' in error_type:
            return {
                'strategy': 'fix_parameters',
                'action': 'review_input_data'
            }
        else:
            return {
                'strategy': 'manual_review',
                'action': 'escalate_to_human'
            }
    
    def _execute_campaign_creation(self, params: Dict) -> Dict:
        """Execute campaign creation pattern"""
        
        try:
            # Step 1: Prepare campaign data
            campaign_data = {
                'name': params['name'],
                'budget': params['budget'],
                'targeting': params.get('targeting', {})
            }
            
            # Step 2: Create campaign
            result = self.client.create_campaign(**campaign_data)
            
            # Step 3: Verify creation
            if result.get('success'):
                campaign_id = result.get('data', {}).get('campaign_id')
                return {
                    'success': True,
                    'campaign_id': campaign_id,
                    'status': 'created',
                    'next_steps': ['monitor_moderation', 'check_performance']
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'recovery_suggestions': ['check_balance', 'validate_targeting']
                }
        
        except Exception as e:
            return self.handle_error(e, {'operation': 'campaign_creation', 'params': params})
    
    def _execute_campaign_monitoring(self, params: Dict) -> Dict:
        """Execute campaign monitoring pattern"""
        
        try:
            # Get campaigns to monitor
            campaigns = self.client.get_campaigns(status='active')
            
            if not campaigns.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to retrieve campaigns'
                }
            
            monitoring_results = []
            
            for campaign in campaigns['data']['result']:
                campaign_id = campaign['campaign_id']
                
                # Get performance data
                stats = self.client.get_statistics(
                    campaign_id=campaign_id,
                    day_from=params.get('day_from', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d 00:00:00')),
                    day_to=params.get('day_to', datetime.now().strftime('%Y-%m-%d 23:59:59')),
                    tz="+0000"
                )
                
                if stats.get('success'):
                    analysis = self._analyze_campaign_performance(stats['data'])
                    monitoring_results.append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign['name'],
                        'performance': analysis,
                        'recommendations': self._generate_recommendations(analysis)
                    })
            
            return {
                'success': True,
                'monitored_campaigns': len(monitoring_results),
                'results': monitoring_results,
                'summary': self._create_monitoring_summary(monitoring_results)
            }
        
        except Exception as e:
            return self.handle_error(e, {'operation': 'campaign_monitoring', 'params': params})
    
    def _execute_budget_management(self, params: Dict) -> Dict:
        """Execute budget management pattern"""
        
        try:
            # Get current account balance
            balance = self.client.get_balance()
            account_balance = float(balance['data']) if balance.get('success') else 0
            
            # Get active campaigns
            campaigns = self.client.get_campaigns(status='active')
            
            budget_analysis = {
                'account_balance': account_balance,
                'total_daily_budget': 0,
                'campaigns_analyzed': 0,
                'adjustments_made': 0,
                'recommendations': []
            }
            
            if campaigns.get('success'):
                for campaign in campaigns['data']['result']:
                    daily_budget = campaign.get('daily_budget', 0)
                    budget_analysis['total_daily_budget'] += daily_budget
                    budget_analysis['campaigns_analyzed'] += 1
                    
                    # Apply adjustment rules
                    adjustment_rules = params.get('adjustment_rules', [])
                    for rule in adjustment_rules:
                        if self._should_apply_rule(campaign, rule):
                            adjustment_result = self._apply_budget_adjustment(campaign, rule)
                            if adjustment_result['adjusted']:
                                budget_analysis['adjustments_made'] += 1
            
            # Generate recommendations
            if account_balance < budget_analysis['total_daily_budget'] * 3:
                budget_analysis['recommendations'].append({
                    'type': 'LOW_BALANCE',
                    'message': 'Account balance is low for current daily spend',
                    'action': 'add_funds_or_reduce_budgets'
                })
            
            return {
                'success': True,
                'analysis': budget_analysis
            }
        
        except Exception as e:
            return self.handle_error(e, {'operation': 'budget_management', 'params': params})
    
    def _analyze_campaign_performance(self, stats_data: Dict) -> Dict:
        """Analyze campaign performance metrics"""
        
        metrics = {
            'impressions': stats_data.get('impressions', 0),
            'clicks': stats_data.get('clicks', 0),
            'conversions': stats_data.get('conversions', 0),
            'spend': stats_data.get('spend', 0)
        }
        
        # Calculate derived metrics
        metrics['ctr'] = (metrics['clicks'] / metrics['impressions'] * 100) if metrics['impressions'] > 0 else 0
        metrics['cpc'] = (metrics['spend'] / metrics['clicks']) if metrics['clicks'] > 0 else 0
        metrics['roi'] = ((metrics['conversions'] * 10 - metrics['spend']) / metrics['spend'] * 100) if metrics['spend'] > 0 else 0
        
        # Determine performance status
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
            'status': status,
            'health_score': self._calculate_health_score(metrics)
        }
    
    def _calculate_health_score(self, metrics: Dict) -> float:
        """Calculate overall campaign health score (0-100)"""
        
        score = 50  # Base score
        
        # CTR contribution (0-25 points)
        ctr = metrics.get('ctr', 0)
        if ctr > 2.0:
            score += 25
        elif ctr > 1.0:
            score += 15
        elif ctr > 0.5:
            score += 10
        
        # ROI contribution (0-25 points)
        roi = metrics.get('roi', 0)
        if roi > 50:
            score += 25
        elif roi > 20:
            score += 15
        elif roi > 10:
            score += 10
        
        return min(100, max(0, score))
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate optimization recommendations"""
        
        recommendations = []
        metrics = analysis['metrics']
        status = analysis['status']
        
        if status == 'LOW_CTR':
            recommendations.append({
                'type': 'IMPROVE_CTR',
                'priority': 'HIGH',
                'message': 'Click-through rate is below optimal threshold',
                'actions': ['review_ad_creative', 'adjust_targeting', 'test_new_formats']
            })
        
        if status == 'HIGH_CPC':
            recommendations.append({
                'type': 'REDUCE_CPC',
                'priority': 'MEDIUM',
                'message': 'Cost per click is higher than target',
                'actions': ['optimize_bidding', 'improve_quality_score', 'refine_targeting']
            })
        
        if status == 'LOW_ROI':
            recommendations.append({
                'type': 'IMPROVE_ROI',
                'priority': 'HIGH',
                'message': 'Return on investment is below target',
                'actions': ['pause_poor_performers', 'increase_conversion_tracking', 'optimize_landing_pages']
            })
        
        return recommendations
    
    def _create_monitoring_summary(self, results: List[Dict]) -> Dict:
        """Create summary of monitoring results"""
        
        total_campaigns = len(results)
        healthy_campaigns = len([r for r in results if r['performance']['status'] == 'HEALTHY'])
        
        return {
            'total_campaigns': total_campaigns,
            'healthy_campaigns': healthy_campaigns,
            'health_percentage': (healthy_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0,
            'issues_found': total_campaigns - healthy_campaigns,
            'overall_status': 'HEALTHY' if healthy_campaigns / total_campaigns > 0.8 else 'NEEDS_ATTENTION'
        }
    
    def _should_apply_rule(self, campaign: Dict, rule: Dict) -> bool:
        """Determine if budget adjustment rule should be applied"""
        
        # Simple rule matching logic
        if 'campaign_id' in rule and rule['campaign_id'] != campaign['campaign_id']:
            return False
        
        if 'min_spend' in rule:
            # Would need to get recent spend data
            pass
        
        return True
    
    def _apply_budget_adjustment(self, campaign: Dict, rule: Dict) -> Dict:
        """Apply budget adjustment rule"""
        
        try:
            new_budget = rule.get('new_budget', campaign.get('daily_budget', 0))
            
            result = self.client.update_campaign(
                campaign_id=campaign['campaign_id'],
                daily_budget=new_budget
            )
            
            return {
                'adjusted': result.get('success', False),
                'old_budget': campaign.get('daily_budget', 0),
                'new_budget': new_budget
            }
        
        except Exception as e:
            self.logger.error(f"Failed to adjust budget for campaign {campaign['campaign_id']}: {e}")
            return {'adjusted': False, 'error': str(e)}


class PropellerAdsDecisionSupport:
    """Decision support system for AI agents"""
    
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def evaluate_action_safety(self, action: str, params: Dict) -> Dict:
        """Evaluate if an action is safe to execute"""
        
        safety_score = 100  # Start with maximum safety
        warnings = []
        blockers = []
        
        if action == 'create_campaign':
            # Check budget safety
            budget = params.get('budget', 0)
            balance = self._get_account_balance()
            
            if budget > balance * 0.5:
                safety_score -= 30
                warnings.append("Campaign budget is more than 50% of account balance")
            
            if budget > balance:
                safety_score = 0
                blockers.append("Insufficient account balance")
        
        elif action == 'update_budget':
            # Check for dramatic budget changes
            current_budget = params.get('current_budget', 0)
            new_budget = params.get('new_budget', 0)
            
            if new_budget > current_budget * 5:
                safety_score -= 40
                warnings.append("Budget increase is more than 5x current amount")
        
        return {
            'safe': safety_score >= 70,
            'safety_score': safety_score,
            'warnings': warnings,
            'blockers': blockers,
            'recommendation': 'PROCEED' if safety_score >= 70 else 'REVIEW_REQUIRED'
        }
    
    def suggest_optimization(self, campaign_data: Dict) -> Dict:
        """Suggest optimization opportunities"""
        
        suggestions = []
        
        # Analyze performance metrics
        if 'performance' in campaign_data:
            metrics = campaign_data['performance']['metrics']
            
            if metrics.get('ctr', 0) < 1.0:
                suggestions.append({
                    'type': 'targeting_optimization',
                    'priority': 'HIGH',
                    'description': 'Low CTR suggests targeting could be refined',
                    'specific_actions': [
                        'Analyze top-performing demographics',
                        'Exclude low-performing placements',
                        'Test different ad formats'
                    ]
                })
            
            if metrics.get('cpc', 0) > 0.5:
                suggestions.append({
                    'type': 'bid_optimization',
                    'priority': 'MEDIUM',
                    'description': 'High CPC indicates bidding strategy needs adjustment',
                    'specific_actions': [
                        'Lower maximum bid',
                        'Use automated bidding',
                        'Improve ad quality score'
                    ]
                })
        
        return {
            'total_suggestions': len(suggestions),
            'suggestions': suggestions,
            'optimization_potential': self._calculate_optimization_potential(campaign_data)
        }
    
    def _get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            balance = self.client.get_balance()
            return float(balance['data']) if balance.get('success') else 0
        except Exception:
            return 0
    
    def _calculate_optimization_potential(self, campaign_data: Dict) -> str:
        """Calculate optimization potential"""
        
        if 'performance' in campaign_data:
            health_score = campaign_data['performance'].get('health_score', 50)
            
            if health_score >= 80:
                return 'LOW'
            elif health_score >= 60:
                return 'MEDIUM'
            else:
                return 'HIGH'
        
        return 'UNKNOWN'
