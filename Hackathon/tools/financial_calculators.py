"""
Financial calculation tools used by specialized agents.
Each function is a tool that Claude can call.
"""

import json
import math
from typing import Any


# ─── Risk Tools ───────────────────────────────────────────────────────────────

def calculate_overdraft_probability(
    average_daily_balance: float,
    monthly_income: float,
    monthly_expenses: float,
    num_overdrafts_last_12m: int,
) -> dict[str, Any]:
    """Estimate the probability of an overdraft in the next 30 days."""
    expense_ratio = monthly_expenses / max(monthly_income, 1)
    buffer_days = average_daily_balance / max((monthly_expenses / 30), 1)
    history_factor = min(num_overdrafts_last_12m / 12, 1.0)

    # Simple logistic-style score
    raw_score = (expense_ratio - 0.8) * 2 + (1 / max(buffer_days, 0.5)) * 0.3 + history_factor * 0.4
    probability = 1 / (1 + math.exp(-raw_score))
    probability = round(min(max(probability, 0.01), 0.99), 3)

    risk_level = "LOW" if probability < 0.3 else "MEDIUM" if probability < 0.65 else "HIGH"

    return {
        "overdraft_probability": probability,
        "risk_level": risk_level,
        "buffer_days_of_cash": round(buffer_days, 1),
        "expense_to_income_ratio": round(expense_ratio, 2),
        "recommendation": (
            "Build a 30-day cash buffer" if risk_level == "HIGH"
            else "Monitor spending closely" if risk_level == "MEDIUM"
            else "Maintain current habits"
        ),
    }


def predict_credit_score_change(
    current_score: int,
    credit_utilization_pct: float,
    missed_payments_last_6m: int,
    new_credit_inquiries: int,
    account_age_years: float,
) -> dict[str, Any]:
    """Predict direction and magnitude of credit score change over 3 months."""
    delta = 0.0
    factors = []

    # Utilization impact
    if credit_utilization_pct > 30:
        penalty = (credit_utilization_pct - 30) * 0.8
        delta -= penalty
        factors.append(f"High utilization ({credit_utilization_pct:.0f}%) hurts score by ~{penalty:.0f} pts")
    elif credit_utilization_pct < 10:
        delta += 5
        factors.append("Low utilization boosts score by ~5 pts")

    # Payment history
    delta -= missed_payments_last_6m * 40
    if missed_payments_last_6m:
        factors.append(f"{missed_payments_last_6m} missed payment(s) drag score by ~{missed_payments_last_6m*40} pts")

    # New inquiries
    delta -= new_credit_inquiries * 5
    if new_credit_inquiries:
        factors.append(f"{new_credit_inquiries} hard inquiry(ies) cost ~{new_credit_inquiries*5} pts")

    # Account age bonus
    if account_age_years > 5:
        delta += 3
        factors.append("Long credit history adds ~3 pts")

    projected_score = int(max(300, min(850, current_score + delta)))
    change = projected_score - current_score

    return {
        "current_score": current_score,
        "projected_score_3m": projected_score,
        "expected_change": change,
        "direction": "INCREASE" if change > 0 else "DECREASE" if change < 0 else "STABLE",
        "key_factors": factors,
        "priority_action": (
            "Pay down balances to below 30% utilization" if credit_utilization_pct > 30
            else "Never miss a payment — autopay recommended" if missed_payments_last_6m
            else "Maintain current credit behaviour"
        ),
    }


def assess_missing_payment_risk(
    bills: list[dict],  # [{name, due_date_days_away, amount, autopay}]
    current_balance: float,
) -> dict[str, Any]:
    """Identify which upcoming bills are at risk of being missed."""
    at_risk = []
    running_balance = current_balance

    for bill in sorted(bills, key=lambda b: b.get("due_date_days_away", 30)):
        name = bill.get("name", "Unknown")
        amount = bill.get("amount", 0)
        days = bill.get("due_date_days_away", 30)
        autopay = bill.get("autopay", False)

        running_balance -= amount
        status = "OK"
        if not autopay and running_balance < 0:
            status = "RISK — insufficient funds"
        elif not autopay and running_balance < amount * 0.2:
            status = "WARNING — low buffer"

        at_risk.append({
            "bill": name,
            "amount": amount,
            "due_in_days": days,
            "autopay": autopay,
            "balance_after": round(running_balance, 2),
            "status": status,
        })

    urgent = [b for b in at_risk if "RISK" in b["status"]]
    return {
        "bills_analysed": len(bills),
        "at_risk_count": len(urgent),
        "at_risk_bills": urgent,
        "all_bills": at_risk,
        "total_upcoming": sum(b["amount"] for b in bills),
    }


# ─── Debt Tools ───────────────────────────────────────────────────────────────

def debt_payoff_plan(
    debts: list[dict],  # [{name, balance, apr, min_payment}]
    extra_monthly_payment: float = 0,
    strategy: str = "avalanche",  # avalanche | snowball
) -> dict[str, Any]:
    """Generate an optimised debt payoff plan."""
    debts = [d.copy() for d in debts]
    for d in debts:
        d["monthly_rate"] = d["apr"] / 100 / 12

    if strategy == "avalanche":
        priority = sorted(debts, key=lambda d: d["apr"], reverse=True)
    else:
        priority = sorted(debts, key=lambda d: d["balance"])

    total_interest = 0.0
    month = 0
    MAX_MONTHS = 360

    balances = {d["name"]: d["balance"] for d in debts}

    while any(b > 0 for b in balances.values()) and month < MAX_MONTHS:
        month += 1
        remaining_extra = extra_monthly_payment

        for d in priority:
            name = d["name"]
            if balances[name] <= 0:
                continue
            interest = balances[name] * d["monthly_rate"]
            total_interest += interest
            payment = d["min_payment"] + remaining_extra
            payment = min(payment, balances[name] + interest)
            balances[name] = max(0, balances[name] + interest - payment)
            remaining_extra = max(0, remaining_extra - max(0, payment - d["min_payment"]))

    total_debt = sum(d["balance"] for d in debts)
    return {
        "strategy": strategy,
        "payoff_months": month,
        "payoff_years": round(month / 12, 1),
        "total_interest_paid": round(total_interest, 2),
        "total_paid": round(total_debt + total_interest, 2),
        "priority_order": [d["name"] for d in priority],
        "monthly_extra_applied": extra_monthly_payment,
    }


def debt_consolidation_analysis(
    debts: list[dict],  # [{name, balance, apr}]
    consolidation_rate: float,
    consolidation_term_months: int = 60,
) -> dict[str, Any]:
    """Compare current debt cost vs consolidation loan."""
    total_balance = sum(d["balance"] for d in debts)
    weighted_rate = sum(d["balance"] * d["apr"] for d in debts) / max(total_balance, 1)

    # Monthly payment for consolidation loan
    r = consolidation_rate / 100 / 12
    if r > 0:
        monthly_payment = total_balance * r / (1 - (1 + r) ** -consolidation_term_months)
    else:
        monthly_payment = total_balance / consolidation_term_months

    consolidation_total = monthly_payment * consolidation_term_months
    consolidation_interest = consolidation_total - total_balance

    current_min_payments = sum(float(d.get("min_payment") or d["balance"] * 0.02) for d in debts)

    return {
        "total_debt": round(total_balance, 2),
        "current_weighted_apr": round(weighted_rate, 2),
        "consolidation_apr": consolidation_rate,
        "consolidation_monthly_payment": round(monthly_payment, 2),
        "consolidation_total_interest": round(consolidation_interest, 2),
        "current_monthly_minimums": round(current_min_payments, 2),
        "saves_interest": consolidation_rate < weighted_rate,
        "recommendation": (
            "Consolidation recommended — lower rate saves money"
            if consolidation_rate < weighted_rate
            else "Consolidation not recommended — current rate is better"
        ),
    }


# ─── Investment Tools ──────────────────────────────────────────────────────────

def run_investment_simulation(
    initial_amount: float,
    monthly_contribution: float,
    annual_return_pct: float,
    years: int,
    inflation_pct: float = 2.5,
) -> dict[str, Any]:
    """Monte Carlo-style compound growth simulation."""
    monthly_rate = annual_return_pct / 100 / 12
    monthly_inflation = inflation_pct / 100 / 12
    balance = initial_amount
    total_contributed = initial_amount

    yearly_snapshots = []
    for year in range(1, years + 1):
        for _ in range(12):
            balance = balance * (1 + monthly_rate) + monthly_contribution
            total_contributed += monthly_contribution

        real_value = balance / ((1 + monthly_inflation) ** (year * 12))
        yearly_snapshots.append({
            "year": year,
            "nominal_value": round(balance, 2),
            "real_value_todays_dollars": round(real_value, 2),
        })

    total_gain = balance - total_contributed
    return {
        "initial_investment": initial_amount,
        "monthly_contribution": monthly_contribution,
        "annual_return_pct": annual_return_pct,
        "years": years,
        "final_balance": round(balance, 2),
        "total_contributed": round(total_contributed, 2),
        "total_gain": round(total_gain, 2),
        "return_multiple": round(balance / max(total_contributed, 1), 2),
        "real_value_todays_dollars": round(yearly_snapshots[-1]["real_value_todays_dollars"], 2),
        "yearly_snapshots": yearly_snapshots,
    }


def portfolio_allocation_recommendation(
    age: int,
    risk_tolerance: str,  # conservative | moderate | aggressive
    investment_horizon_years: int,
    emergency_fund_months: float,
) -> dict[str, Any]:
    """Recommend an asset allocation based on user profile."""
    base_equity = max(20, 110 - age)

    adjustments = {
        "conservative": -15,
        "moderate": 0,
        "aggressive": +15,
    }
    equity_pct = min(95, max(20, base_equity + adjustments.get(risk_tolerance, 0)))

    if investment_horizon_years < 3:
        equity_pct = min(equity_pct, 40)
    elif investment_horizon_years < 7:
        equity_pct = min(equity_pct, 70)

    bond_pct = max(5, 100 - equity_pct - 5)
    cash_pct = 100 - equity_pct - bond_pct

    return {
        "recommended_allocation": {
            "equities": f"{equity_pct}%",
            "bonds": f"{bond_pct}%",
            "cash_and_equivalents": f"{cash_pct}%",
        },
        "equity_breakdown": {
            "us_stocks": f"{int(equity_pct * 0.6)}%",
            "international_stocks": f"{int(equity_pct * 0.3)}%",
            "real_estate_reits": f"{int(equity_pct * 0.1)}%",
        },
        "emergency_fund_status": (
            "Adequate" if emergency_fund_months >= 6
            else "Build to 6 months before investing aggressively"
        ),
        "rationale": (
            f"Age {age}, {risk_tolerance} risk tolerance, "
            f"{investment_horizon_years}-year horizon"
        ),
    }


# ─── Wealth Tools ──────────────────────────────────────────────────────────────

def paycheck_split_recommendation(
    net_monthly_income: float,
    current_rent: float,
    current_debt_payments: float,
    has_emergency_fund: bool,
    retirement_contribution_pct: float,
) -> dict[str, Any]:
    """Recommend how to split a paycheck using a 50/30/20 framework."""
    needs_cap = net_monthly_income * 0.50
    wants_cap = net_monthly_income * 0.30
    savings_target = net_monthly_income * 0.20

    fixed_needs = current_rent + current_debt_payments
    remaining_for_wants = max(0, needs_cap - fixed_needs)

    retirement_amount = net_monthly_income * (retirement_contribution_pct / 100)
    emergency_fund_target = 6 * (net_monthly_income * 0.80)
    emergency_monthly = net_monthly_income * 0.10 if not has_emergency_fund else 0

    investing = max(0, savings_target - retirement_amount - emergency_monthly)

    return {
        "framework": "50/30/20",
        "monthly_income": net_monthly_income,
        "allocation": {
            "needs_50pct": {
                "target": round(needs_cap, 2),
                "rent_debt": round(fixed_needs, 2),
                "remaining_for_groceries_utilities": round(remaining_for_wants, 2),
            },
            "wants_30pct": {
                "target": round(wants_cap, 2),
                "note": "Dining, entertainment, subscriptions",
            },
            "savings_20pct": {
                "target": round(savings_target, 2),
                "retirement": round(retirement_amount, 2),
                "emergency_fund": round(emergency_monthly, 2),
                "investing": round(investing, 2),
            },
        },
        "emergency_fund_target": round(emergency_fund_target, 2),
        "emergency_fund_status": "Complete" if has_emergency_fund else "In progress",
    }


def net_worth_tracker(
    assets: dict[str, float],
    liabilities: dict[str, float],
) -> dict[str, Any]:
    """Calculate and categorise net worth."""
    total_assets = sum(assets.values())
    total_liabilities = sum(liabilities.values())
    net_worth = total_assets - total_liabilities

    liquid_assets = sum(
        v for k, v in assets.items()
        if any(word in k.lower() for word in ["cash", "checking", "savings", "money market"])
    )

    return {
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "net_worth": round(net_worth, 2),
        "liquid_assets": round(liquid_assets, 2),
        "debt_to_asset_ratio": round(total_liabilities / max(total_assets, 1), 3),
        "assets_breakdown": {k: round(v, 2) for k, v in assets.items()},
        "liabilities_breakdown": {k: round(v, 2) for k, v in liabilities.items()},
        "status": (
            "Positive net worth" if net_worth > 0
            else "Negative net worth — focus on debt reduction"
        ),
    }


# ─── Behaviour Tools ──────────────────────────────────────────────────────────

def analyse_spending_patterns(
    transactions: list[dict],  # [{category, amount, date_label, merchant}]
) -> dict[str, Any]:
    """Identify spending patterns, top categories, and behavioural insights."""
    category_totals: dict[str, float] = {}
    merchant_counts: dict[str, int] = {}
    time_buckets: dict[str, float] = {"morning": 0, "afternoon": 0, "evening": 0, "weekend": 0}

    for t in transactions:
        cat = t.get("category", "Other")
        amount = t.get("amount", 0)
        merchant = t.get("merchant", "Unknown")
        label = t.get("date_label", "").lower()

        category_totals[cat] = category_totals.get(cat, 0) + amount
        merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1

        for bucket in time_buckets:
            if bucket in label:
                time_buckets[bucket] += amount
                break

    total_spent = sum(category_totals.values())
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_merchants = sorted(merchant_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    emotional_triggers = []
    for cat, amount in category_totals.items():
        if cat.lower() in ["food & drink", "entertainment", "shopping"] and amount / max(total_spent, 1) > 0.25:
            emotional_triggers.append(f"High {cat} spending ({amount/total_spent*100:.0f}% of budget) may indicate stress/emotional spending")

    return {
        "total_analysed": total_spent,
        "top_5_categories": [{"category": c, "amount": round(a, 2), "pct": round(a/max(total_spent,1)*100, 1)} for c, a in top_categories],
        "top_merchants": [{"merchant": m, "visits": c} for m, c in top_merchants],
        "spending_by_time": {k: round(v, 2) for k, v in time_buckets.items()},
        "behavioural_insights": emotional_triggers,
        "transactions_analysed": len(transactions),
    }


# ─── Tool Registry ─────────────────────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "calculate_overdraft_probability": calculate_overdraft_probability,
    "predict_credit_score_change": predict_credit_score_change,
    "assess_missing_payment_risk": assess_missing_payment_risk,
    "debt_payoff_plan": debt_payoff_plan,
    "debt_consolidation_analysis": debt_consolidation_analysis,
    "run_investment_simulation": run_investment_simulation,
    "portfolio_allocation_recommendation": portfolio_allocation_recommendation,
    "paycheck_split_recommendation": paycheck_split_recommendation,
    "net_worth_tracker": net_worth_tracker,
    "analyse_spending_patterns": analyse_spending_patterns,
}


def execute_tool(name: str, inputs: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
