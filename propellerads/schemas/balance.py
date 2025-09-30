"""
Balance and financial schemas
"""

from typing import Optional
from pydantic import Field
from decimal import Decimal
from datetime import datetime

from .base import PropellerBaseSchema


class Balance(PropellerBaseSchema):
    """Account balance information"""
    
    balance: Decimal = Field(description="Current account balance")
    currency: str = Field(default="USD", description="Currency code")
    last_updated: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"${self.balance}"
    
    @property
    def formatted_balance(self) -> str:
        """Get formatted balance string"""
        return f"${self.balance:,.2f}"


class Transaction(PropellerBaseSchema):
    """Transaction record"""
    
    id: int
    amount: Decimal
    type: str  # deposit, withdrawal, spend, refund
    description: Optional[str] = None
    created_at: datetime
    status: str = "completed"  # pending, completed, failed
    
    
class FinancialSummary(PropellerBaseSchema):
    """Financial summary statistics"""
    
    total_spend: Decimal = Field(default=Decimal('0'))
    total_revenue: Decimal = Field(default=Decimal('0'))
    total_profit: Decimal = Field(default=Decimal('0'))
    average_cpc: Decimal = Field(default=Decimal('0'))
    average_cpm: Decimal = Field(default=Decimal('0'))
    
    # Time period
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
