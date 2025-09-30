"""
Balance API implementation
"""

from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from .base import BaseAPI
from ..schemas.balance import Balance, Transaction, FinancialSummary

logger = logging.getLogger(__name__)


class BalanceAPI(BaseAPI):
    """Balance and financial operations API"""
    
    def get_balance(self):
        """
        Get current account balance
        
        Returns:
            Current balance information
        """
        logger.debug("Getting account balance")
        
        response = self.client._make_request('GET', '/adv/balance')
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict) and 'amount' in data:
            balance_value = data['amount']
            currency = data.get('currency', 'USD')
        else:
            balance_value = data
            currency = 'USD'
        
        # Return compatible balance object
        from ..client import BalanceResponse
        return BalanceResponse(balance_value, currency)
    
    async def get_transactions(
        self, 
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """
        Get transaction history
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            transaction_type: Filter by type (deposit, withdrawal, spend, refund)
            limit: Maximum number of transactions
            offset: Offset for pagination
            
        Returns:
            List of transactions
        """
        logger.debug("Getting transaction history")
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        if transaction_type:
            params['type'] = transaction_type
        
        response = await self._get('/adv/transactions', params=params)
        
        transactions = []
        if 'data' in response:
            for tx_data in response['data']:
                transactions.append(Transaction.from_api_response(tx_data))
        
        return transactions
    
    async def get_financial_summary(
        self, 
        date_from: str, 
        date_to: str
    ) -> FinancialSummary:
        """
        Get financial summary for date range
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Financial summary
        """
        logger.debug(f"Getting financial summary: {date_from} to {date_to}")
        
        params = {
            'date_from': date_from,
            'date_to': date_to
        }
        
        response = await self._get('/adv/financial-summary', params=params)
        
        return FinancialSummary(
            total_spend=response.get('total_spend', 0),
            total_revenue=response.get('total_revenue', 0),
            total_profit=response.get('total_profit', 0),
            average_cpc=response.get('average_cpc', 0),
            average_cpm=response.get('average_cpm', 0),
            period_start=datetime.fromisoformat(date_from),
            period_end=datetime.fromisoformat(date_to)
        )
    
    async def get_spending_forecast(self, days: int = 30) -> Dict[str, Any]:
        """
        Get spending forecast based on current campaigns
        
        Args:
            days: Number of days to forecast
            
        Returns:
            Spending forecast data
        """
        logger.debug(f"Getting spending forecast for {days} days")
        
        params = {'days': days}
        response = await self._get('/adv/spending-forecast', params=params)
        
        return response
    
    async def set_budget_alert(
        self, 
        threshold: float, 
        alert_type: str = 'email'
    ) -> Dict[str, Any]:
        """
        Set budget alert threshold
        
        Args:
            threshold: Budget threshold amount
            alert_type: Alert type (email, webhook)
            
        Returns:
            Alert configuration
        """
        logger.info(f"Setting budget alert: ${threshold}")
        
        data = {
            'threshold': threshold,
            'type': alert_type
        }
        
        response = await self._post('/adv/budget-alerts', data=data)
        return response
    
    async def get_budget_alerts(self) -> List[Dict[str, Any]]:
        """
        Get configured budget alerts
        
        Returns:
            List of budget alerts
        """
        logger.debug("Getting budget alerts")
        
        response = await self._get('/adv/budget-alerts')
        return response.get('data', [])
    
    async def delete_budget_alert(self, alert_id: int) -> bool:
        """
        Delete budget alert
        
        Args:
            alert_id: Alert ID to delete
            
        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting budget alert: {alert_id}")
        
        await self._delete(f'/adv/budget-alerts/{alert_id}')
        return True
