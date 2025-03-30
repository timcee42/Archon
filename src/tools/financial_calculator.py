"""Financial calculator tool for EUC Assessment Agent team.

This module provides tools for performing financial calculations such as ROI, TCO, and NPV.
"""

import logging
import math
from typing import Dict, List, Union, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """A tool for performing financial calculations."""

    @staticmethod
    def calculate_tco(
        initial_costs: float,
        recurring_costs: Dict[str, float],
        timeframe_years: int
    ) -> Dict[str, Any]:
        """Calculate Total Cost of Ownership (TCO).
        
        Args:
            initial_costs: One-time initial costs
            recurring_costs: Dictionary of recurring costs with frequency (e.g., "monthly", "yearly")
            timeframe_years: Number of years to calculate TCO for
            
        Returns:
            Dictionary with TCO calculation results
        """
        total_recurring = 0.0
        breakdown = {"initial": initial_costs, "recurring": {}}
        
        # Calculate recurring costs for the timeframe
        for cost_type, annual_amount in recurring_costs.items():
            cost_for_timeframe = annual_amount * timeframe_years
            total_recurring += cost_for_timeframe
            breakdown["recurring"][cost_type] = cost_for_timeframe
        
        # Calculate TCO
        tco = initial_costs + total_recurring
        
        return {
            "tco": tco,
            "timeframe_years": timeframe_years,
            "initial_costs": initial_costs,
            "recurring_costs_total": total_recurring,
            "breakdown": breakdown
        }

    @staticmethod
    def calculate_roi(
        initial_investment: float,
        annual_benefits: float,
        annual_costs: float,
        timeframe_years: int
    ) -> Dict[str, Any]:
        """Calculate Return on Investment (ROI).
        
        Args:
            initial_investment: Initial investment amount
            annual_benefits: Annual benefits/savings
            annual_costs: Annual costs
            timeframe_years: Number of years to calculate ROI for
            
        Returns:
            Dictionary with ROI calculation results
        """
        total_benefits = annual_benefits * timeframe_years
        total_costs = initial_investment + (annual_costs * timeframe_years)
        
        # Calculate ROI as a percentage
        if total_costs == 0:
            roi_percentage = 0.0  # Avoid division by zero
        else:
            roi_percentage = ((total_benefits - total_costs) / total_costs) * 100
        
        # Calculate payback period in years
        if annual_benefits - annual_costs <= 0:
            payback_period = float('inf')  # No payback if annual net benefit is zero or negative
        else:
            payback_period = initial_investment / (annual_benefits - annual_costs)
        
        return {
            "roi_percentage": roi_percentage,
            "timeframe_years": timeframe_years,
            "total_benefits": total_benefits,
            "total_costs": total_costs,
            "annual_net_benefit": annual_benefits - annual_costs,
            "payback_period_years": payback_period,
            "net_benefit": total_benefits - total_costs
        }

    @staticmethod
    def calculate_npv(
        initial_investment: float,
        cash_flows: List[float],
        discount_rate: float
    ) -> Dict[str, Any]:
        """Calculate Net Present Value (NPV).
        
        Args:
            initial_investment: Initial investment amount (negative)
            cash_flows: List of cash flows for each period
            discount_rate: Discount rate (percentage, e.g., 10 for 10%)
            
        Returns:
            Dictionary with NPV calculation results
        """
        discount_rate_decimal = discount_rate / 100.0
        
        # Calculate NPV
        npv = initial_investment
        discounted_cash_flows = []
        
        for i, cash_flow in enumerate(cash_flows):
            period = i + 1  # Period is 1-indexed
            discounted_cf = cash_flow / ((1 + discount_rate_decimal) ** period)
            npv += discounted_cf
            discounted_cash_flows.append({
                "period": period,
                "cash_flow": cash_flow,
                "discounted_cash_flow": discounted_cf
            })
        
        return {
            "npv": npv,
            "discount_rate": discount_rate,
            "initial_investment": initial_investment,
            "discounted_cash_flows": discounted_cash_flows,
            "is_profitable": npv > 0
        }

    @staticmethod
    def calculate_license_costs(
        license_unit_cost: float,
        num_licenses: int,
        years: int = 1,
        discount_percentage: float = 0.0
    ) -> Dict[str, Any]:
        """Calculate licensing costs with optional volume discount.
        
        Args:
            license_unit_cost: Cost per license
            num_licenses: Number of licenses
            years: Number of years
            discount_percentage: Volume discount percentage
            
        Returns:
            Dictionary with licensing cost calculation results
        """
        # Calculate base cost
        base_cost = license_unit_cost * num_licenses
        
        # Apply discount if applicable
        discount_amount = base_cost * (discount_percentage / 100.0)
        discounted_cost = base_cost - discount_amount
        
        # Calculate total cost for the specified years
        total_cost = discounted_cost * years
        
        return {
            "total_cost": total_cost,
            "annual_cost": discounted_cost,
            "unit_cost": license_unit_cost,
            "num_licenses": num_licenses,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "years": years
        }


# Singleton instance
_calculator = None


def get_financial_calculator() -> FinancialCalculator:
    """Get the singleton financial calculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = FinancialCalculator()
    return _calculator 