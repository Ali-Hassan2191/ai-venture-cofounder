"""
Financial Modeling Service using Pandas.
Performs unit economics projections, monthly burn rate analysis,
cash flow modeling, and break-even calculations.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class FinancialService:

    @staticmethod
    def calculate_12_month_cashflow(
        initial_budget: float,
        monthly_fixed_costs: float,
        monthly_marketing: float,
        avg_revenue_per_user: float,
        expected_monthly_growth_rate: float = 0.15,
        initial_users: int = 15,
    ) -> pd.DataFrame:
        """
        Generates a 12-month financial projection DataFrame using Pandas.
        """
        months = [f"Month {m}" for m in range(1, 13)]
        users = []
        revenues = []
        costs = []
        net_cashflows = []
        cash_balances = []

        current_users = float(initial_users)
        current_balance = float(initial_budget)

        for m in range(1, 13):
            # Compound user growth
            if m > 1:
                current_users = current_users * (1.0 + expected_monthly_growth_rate)
            users_count = int(current_users)
            users.append(users_count)

            # Revenue calculation
            rev = users_count * avg_revenue_per_user
            revenues.append(round(rev, 2))

            # Costs (fixed + variable marketing scaling lightly with users)
            cost = monthly_fixed_costs + (monthly_marketing * (1.0 + (m * 0.04)))
            costs.append(round(cost, 2))

            # Net & balance
            net = rev - cost
            net_cashflows.append(round(net, 2))
            current_balance += net
            cash_balances.append(round(current_balance, 2))

        df = pd.DataFrame({
            "Month": months,
            "Active Customers": users,
            "Revenue": revenues,
            "Operating Costs": costs,
            "Net Cash Flow": net_cashflows,
            "Treasury Balance": cash_balances,
        })
        return df

    @staticmethod
    def compute_break_even_metrics(
        fixed_costs_monthly: float,
        unit_price: float,
        variable_cost_per_unit: float,
    ) -> Dict[str, Any]:
        """
        Calculates exact break-even units and revenue thresholds using Pandas/algebra.
        """
        contribution_margin = unit_price - variable_cost_per_unit
        if contribution_margin <= 0:
            return {
                "break_even_units": None,
                "break_even_revenue": None,
                "contribution_margin": 0.0,
                "margin_ratio": 0.0,
                "status": "Negative Unit Economics",
            }

        margin_ratio = contribution_margin / (unit_price + 1e-9)
        break_even_units = int(np.ceil(fixed_costs_monthly / contribution_margin))
        break_even_revenue = round(break_even_units * unit_price, 2)

        return {
            "break_even_units": break_even_units,
            "break_even_revenue": break_even_revenue,
            "contribution_margin": round(contribution_margin, 2),
            "margin_ratio": round(margin_ratio * 100, 1),
            "status": "Sustainable",
        }

    @staticmethod
    def build_cost_breakdown_df(
        dev_cost: float,
        marketing_cost: float,
        ops_cost: float,
        reserve_cost: float,
    ) -> pd.DataFrame:
        """
        Formats initial capital allocation into a structured Pandas DataFrame.
        """
        data = [
            {"Category": "Software Engineering & Architecture", "Amount": dev_cost},
            {"Category": "Go-To-Market & Acquisition", "Amount": marketing_cost},
            {"Category": "Operations, Legal & Infrastructure", "Amount": ops_cost},
            {"Category": "Contingency & Cash Reserve", "Amount": reserve_cost},
        ]
        df = pd.DataFrame(data)
        total = df["Amount"].sum()
        df["Allocation %"] = (df["Amount"] / (total + 1e-9) * 100).round(1)
        return df
