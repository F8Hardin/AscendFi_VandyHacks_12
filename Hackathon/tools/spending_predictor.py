"""
Spending Habit Predictor
========================
Machine learning models for personal finance projections based on spending patterns.

XGBoost  (regression)   → predict_spending_trajectory
  Predicts savings balance at 3, 6, 12 months given current income/expense ratios.
  Captures non-linear interactions: high debt + variable income compounds risk
  far worse than either factor alone.

CatBoost (classification) → predict_financial_health
  Classifies financial health (CRITICAL → EXCELLENT) and overdraft risk tier.
  Handles spending categories natively — no one-hot encoding needed.

Both models train lazily on first call using 2,000 synthetic scenarios that
encode real financial rules (savings rate, debt load, emergency fund, income
stability). Training takes ~0.5s and results are cached for the session.

Callable by: Behaviour Agent, Wealth Agent
"""

import json
from typing import Any

import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from catboost import CatBoostClassifier, Pool
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False


# ── Module-level model cache ───────────────────────────────────────────────────
_xgb_model: Any = None       # XGBRegressor (multi-output via separate models)
_xgb_3mo:   Any = None
_xgb_6mo:   Any = None
_xgb_12mo:  Any = None
_xgb_ef:    Any = None       # months to emergency fund
_cat_health: Any = None      # CatBoostClassifier → health label
_cat_overdraft: Any = None   # CatBoostClassifier → overdraft risk


# ── Synthetic training data ────────────────────────────────────────────────────

def _build_training_data(n: int = 2000) -> "pd.DataFrame":
    """
    Generate synthetic financial scenarios encoding real personal finance rules.
    The non-linear structure in targets is what makes gradient boosting better
    than a linear model here.
    """
    rng = np.random.default_rng(42)
    rows = []

    for _ in range(n):
        income = rng.uniform(1500, 12000)

        # Spending ratios (fraction of income)
        rent_r    = rng.uniform(0.15, 0.55)
        food_r    = rng.uniform(0.05, 0.22)
        transport_r = rng.uniform(0.02, 0.15)
        entertain_r = rng.uniform(0.0, 0.15)
        debt_r    = rng.uniform(0.0, 0.45)
        other_r   = rng.uniform(0.01, 0.12)

        total_r   = rent_r + food_r + transport_r + entertain_r + debt_r + other_r
        savings_r = 1.0 - min(total_r, 1.25)   # capped: can't spend more than 125% forever

        ef_months = rng.uniform(0, 9)           # current emergency fund in months
        income_var = rng.integers(0, 3)         # 0=stable, 1=semi-variable, 2=variable/freelance
        current_savings = rng.uniform(0, income * 6)

        # ── XGBoost targets (regression) ──────────────────────────────────────
        monthly_delta = income * savings_r

        # Non-linear variability penalty: variable income amplifies downside
        var_penalty = income_var * max(-monthly_delta, 0) * 0.4

        savings_3mo  = current_savings + monthly_delta * 3  - var_penalty * 1
        savings_6mo  = current_savings + monthly_delta * 6  - var_penalty * 2
        savings_12mo = current_savings + monthly_delta * 12 - var_penalty * 4

        ef_target = income * 3   # 3-month emergency fund target
        if savings_r > 0.01:
            months_to_ef = max(0, (ef_target - current_savings) / (income * savings_r))
            months_to_ef += income_var * 3   # variability delays EF build
            months_to_ef = min(months_to_ef, 120)
        else:
            months_to_ef = 120

        # ── CatBoost targets (classification) ─────────────────────────────────

        # Health score rubric (additive)
        h = 0
        h += 3 if savings_r > 0.20 else (2 if savings_r > 0.10 else (1 if savings_r > 0.03 else -3))
        h += 2 if ef_months >= 6 else (1 if ef_months >= 3 else (-1 if ef_months < 1 else 0))
        h += 1 if debt_r < 0.10 else (-1 if debt_r > 0.25 else (-2 if debt_r > 0.38 else 0))
        h += 1 if rent_r < 0.30 else (-1 if rent_r > 0.45 else 0)
        h -= income_var * 0.8  # variable income penalises stability score
        h -= 1 if (rent_r + debt_r) > 0.60 else 0  # combined obligation burden

        health = (
            "EXCELLENT" if h >= 5
            else "GOOD"    if h >= 3
            else "FAIR"    if h >= 1
            else "POOR"    if h >= -1
            else "CRITICAL"
        )

        # Overdraft risk rubric
        od = 0
        od += 3 if savings_r < -0.10 else (2 if savings_r < 0 else (1 if savings_r < 0.03 else 0))
        od += 2 if ef_months < 0.5 else (1 if ef_months < 1.5 else 0)
        od += 2 if debt_r > 0.40 else (1 if debt_r > 0.28 else 0)
        od += income_var           # 0,1,2 additive risk
        od += 1 if (rent_r + debt_r) > 0.65 else 0

        overdraft = (
            "CRITICAL" if od >= 6
            else "HIGH"     if od >= 4
            else "MODERATE" if od >= 2
            else "LOW"
        )

        rows.append({
            # Features
            "monthly_income":     income,
            "rent_ratio":         rent_r,
            "food_ratio":         food_r,
            "transport_ratio":    transport_r,
            "entertainment_ratio": entertain_r,
            "debt_payment_ratio": debt_r,
            "other_ratio":        other_r,
            "total_expense_ratio": total_r,
            "savings_ratio":      savings_r,
            "emergency_fund_months": ef_months,
            "income_variability": income_var,
            "current_savings":    current_savings,
            # XGBoost targets
            "savings_3mo":        savings_3mo,
            "savings_6mo":        savings_6mo,
            "savings_12mo":       savings_12mo,
            "months_to_ef":       months_to_ef,
            # CatBoost targets
            "health_label":       health,
            "overdraft_label":    overdraft,
        })

    return pd.DataFrame(rows)


FEATURE_COLS = [
    "monthly_income", "rent_ratio", "food_ratio", "transport_ratio",
    "entertainment_ratio", "debt_payment_ratio", "other_ratio",
    "total_expense_ratio", "savings_ratio", "emergency_fund_months",
    "income_variability", "current_savings",
]


def _ensure_models_trained():
    """Train and cache all models on first call (lazy init)."""
    global _xgb_3mo, _xgb_6mo, _xgb_12mo, _xgb_ef
    global _cat_health, _cat_overdraft

    if _xgb_3mo is not None:
        return   # already trained

    df = _build_training_data(2000)
    X  = df[FEATURE_COLS].values

    # ── XGBoost regressors (one per target) ───────────────────────────────────
    xgb_params = dict(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        min_child_weight=3, reg_alpha=0.1, reg_lambda=1.0,
        random_state=42, n_jobs=-1, verbosity=0,
    )
    _xgb_3mo  = XGBRegressor(**xgb_params).fit(X, df["savings_3mo"].values)
    _xgb_6mo  = XGBRegressor(**xgb_params).fit(X, df["savings_6mo"].values)
    _xgb_12mo = XGBRegressor(**xgb_params).fit(X, df["savings_12mo"].values)
    _xgb_ef   = XGBRegressor(**xgb_params).fit(X, df["months_to_ef"].values)

    # ── CatBoost classifiers ───────────────────────────────────────────────────
    cat_params = dict(
        iterations=300, depth=6, learning_rate=0.05,
        l2_leaf_reg=3, random_seed=42,
        verbose=False, allow_writing_files=False,
    )
    _cat_health = CatBoostClassifier(
        **cat_params,
        class_names=["CRITICAL", "POOR", "FAIR", "GOOD", "EXCELLENT"],
    ).fit(X, df["health_label"].values)

    _cat_overdraft = CatBoostClassifier(
        **cat_params,
        class_names=["LOW", "MODERATE", "HIGH", "CRITICAL"],
    ).fit(X, df["overdraft_label"].values)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _income_var_from_type(income_type: str) -> int:
    mapping = {
        "salary":     0,
        "hourly":     0,
        "part_time":  1,
        "freelance":  2,
        "commission": 2,
        "mixed":      1,
        "variable":   2,
    }
    return mapping.get(income_type.lower().replace("-", "_"), 1)


# ── Public tool functions ──────────────────────────────────────────────────────

def predict_spending_trajectory(
    monthly_income: float,
    monthly_rent: float,
    monthly_food: float,
    monthly_transport: float,
    monthly_entertainment: float,
    monthly_debt_payments: float,
    monthly_other: float = 0.0,
    current_savings: float = 0.0,
    income_type: str = "salary",
) -> dict[str, Any]:
    """
    XGBoost regression: project the user's savings balance at 3, 6, and 12 months
    based on their current income and spending breakdown. Also estimates how many
    months until a 3-month emergency fund is reached.

    income_type: salary | hourly | part_time | freelance | commission | mixed
    All monetary inputs are monthly amounts in the user's currency.
    """
    if not XGBOOST_AVAILABLE:
        return {"error": "xgboost not installed. Run: pip install xgboost"}
    if not PANDAS_AVAILABLE:
        return {"error": "pandas not installed. Run: pip install pandas"}

    if monthly_income <= 0:
        return {"error": "monthly_income must be positive"}

    _ensure_models_trained()

    total_expenses = (
        monthly_rent + monthly_food + monthly_transport
        + monthly_entertainment + monthly_debt_payments + monthly_other
    )
    savings_r   = (monthly_income - total_expenses) / monthly_income
    total_r     = total_expenses / monthly_income
    income_var  = _income_var_from_type(income_type)

    ef_months_cur = current_savings / monthly_income  # current EF in months

    row = np.array([[
        monthly_income,
        monthly_rent          / monthly_income,
        monthly_food          / monthly_income,
        monthly_transport     / monthly_income,
        monthly_entertainment / monthly_income,
        monthly_debt_payments / monthly_income,
        monthly_other         / monthly_income,
        total_r,
        savings_r,
        ef_months_cur,
        income_var,
        current_savings,
    ]])

    s3  = float(_xgb_3mo.predict(row)[0])
    s6  = float(_xgb_6mo.predict(row)[0])
    s12 = float(_xgb_12mo.predict(row)[0])
    ef  = float(_xgb_ef.predict(row)[0])

    monthly_net = monthly_income - total_expenses
    direction = "positive" if monthly_net >= 0 else "negative"

    ef_target       = monthly_income * 3
    ef_pct_current  = min(current_savings / ef_target * 100, 100) if ef_target > 0 else 0

    return {
        "inputs": {
            "monthly_income":     round(monthly_income, 2),
            "total_monthly_expenses": round(total_expenses, 2),
            "monthly_net":        round(monthly_net, 2),
            "savings_rate_pct":   round(savings_r * 100, 1),
            "income_type":        income_type,
        },
        "savings_projections": {
            "current_savings":       round(current_savings, 2),
            "projected_3_months":    round(s3, 2),
            "projected_6_months":    round(s6, 2),
            "projected_12_months":   round(s12, 2),
            "trend":                 direction,
        },
        "emergency_fund": {
            "target_3_month_fund":   round(ef_target, 2),
            "current_pct_of_target": round(ef_pct_current, 1),
            "months_to_reach_3mo_ef": (
                round(ef, 1) if ef < 119 else "120+ (not achievable at current savings rate)"
            ),
        },
        "expense_breakdown_pct": {
            "rent":          round(monthly_rent          / monthly_income * 100, 1),
            "food":          round(monthly_food          / monthly_income * 100, 1),
            "transport":     round(monthly_transport     / monthly_income * 100, 1),
            "entertainment": round(monthly_entertainment / monthly_income * 100, 1),
            "debt_payments": round(monthly_debt_payments / monthly_income * 100, 1),
            "other":         round(monthly_other         / monthly_income * 100, 1),
        },
        "model": "XGBoost regression trained on 2,000 financial scenarios",
        "disclaimer": "Projections assume stable spending patterns. Not financial advice.",
    }


def predict_financial_health(
    monthly_income: float,
    monthly_rent: float,
    monthly_food: float,
    monthly_transport: float,
    monthly_entertainment: float,
    monthly_debt_payments: float,
    monthly_other: float = 0.0,
    current_savings: float = 0.0,
    income_type: str = "salary",
) -> dict[str, Any]:
    """
    CatBoost classification: assess the user's overall financial health
    (CRITICAL / POOR / FAIR / GOOD / EXCELLENT) and overdraft risk tier
    (LOW / MODERATE / HIGH / CRITICAL) from their spending patterns.
    Returns the dominant risk factors and concrete improvement actions.
    """
    if not CATBOOST_AVAILABLE:
        return {"error": "catboost not installed. Run: pip install catboost"}
    if not PANDAS_AVAILABLE:
        return {"error": "pandas not installed. Run: pip install pandas"}

    if monthly_income <= 0:
        return {"error": "monthly_income must be positive"}

    _ensure_models_trained()

    total_expenses = (
        monthly_rent + monthly_food + monthly_transport
        + monthly_entertainment + monthly_debt_payments + monthly_other
    )
    savings_r   = (monthly_income - total_expenses) / monthly_income
    total_r     = total_expenses / monthly_income
    income_var  = _income_var_from_type(income_type)
    ef_months   = current_savings / monthly_income

    row = np.array([[
        monthly_income,
        monthly_rent          / monthly_income,
        monthly_food          / monthly_income,
        monthly_transport     / monthly_income,
        monthly_entertainment / monthly_income,
        monthly_debt_payments / monthly_income,
        monthly_other         / monthly_income,
        total_r,
        savings_r,
        ef_months,
        income_var,
        current_savings,
    ]])

    health_label    = _cat_health.predict(row)[0]
    od_label        = _cat_overdraft.predict(row)[0]

    health_proba    = dict(zip(_cat_health.classes_, _cat_health.predict_proba(row)[0]))
    od_proba        = dict(zip(_cat_overdraft.classes_, _cat_overdraft.predict_proba(row)[0]))

    # Identify top risk factors (rule-based, transparent to the LLM)
    risk_factors = []
    if savings_r < 0:
        risk_factors.append(f"Spending exceeds income by {abs(round(savings_r*100,1))}% — deficit spending")
    elif savings_r < 0.05:
        risk_factors.append(f"Savings rate is only {round(savings_r*100,1)}% — critically thin buffer")

    if monthly_rent / monthly_income > 0.40:
        risk_factors.append(f"Rent is {round(monthly_rent/monthly_income*100,1)}% of income — well above 30% guideline")

    if monthly_debt_payments / monthly_income > 0.30:
        risk_factors.append(f"Debt payments are {round(monthly_debt_payments/monthly_income*100,1)}% of income — high debt burden")

    if (monthly_rent + monthly_debt_payments) / monthly_income > 0.60:
        risk_factors.append("Rent + debt payments exceed 60% of income — severely limits flexibility")

    if ef_months < 1:
        risk_factors.append(f"Emergency fund covers only {round(ef_months,1)} months — dangerously low")
    elif ef_months < 3:
        risk_factors.append(f"Emergency fund at {round(ef_months,1)} months — below 3-month minimum")

    if income_var >= 2:
        risk_factors.append("Variable/freelance income amplifies all other risks")

    # Suggested priority actions
    actions = []
    if savings_r < 0.05:
        actions.append("Identify and cut the single largest discretionary spend to create a positive savings rate")
    if monthly_rent / monthly_income > 0.35:
        actions.append("Explore ways to reduce housing cost (roommate, renegotiate, relocate)")
    if monthly_debt_payments / monthly_income > 0.20:
        actions.append("Prioritise highest-APR debt payoff using the avalanche method")
    if ef_months < 3:
        actions.append(f"Build emergency fund to 3 months (${round(monthly_income*3):,}) before investing")
    if monthly_entertainment / monthly_income > 0.10:
        actions.append(f"Entertainment at {round(monthly_entertainment/monthly_income*100,1)}% of income — audit subscriptions and dining")
    if not actions:
        actions.append("Maintain current habits and direct surplus to investing and additional EF padding")

    health_descriptions = {
        "EXCELLENT": "Finances are well-managed. Strong savings rate, solid emergency fund, manageable debt.",
        "GOOD":      "On solid ground with room to optimise. Minor adjustments could push to Excellent.",
        "FAIR":      "Managing but vulnerable. One unexpected expense could cause real strain.",
        "POOR":      "Under significant financial pressure. Immediate spending review needed.",
        "CRITICAL":  "Deficit spending or extreme debt burden. Urgent intervention required.",
    }

    od_descriptions = {
        "LOW":      "Low probability of overdraft in the next 3 months under normal conditions.",
        "MODERATE": "Moderate risk — a single unexpected bill could cause a shortfall.",
        "HIGH":     "High risk — likely to experience a cash shortfall within 3 months.",
        "CRITICAL": "Near-certain shortfall. Immediate cash flow action required.",
    }

    return {
        "financial_health": {
            "rating":      health_label,
            "description": health_descriptions[health_label],
            "confidence_pct": round(health_proba.get(health_label, 0) * 100, 1),
            "score_distribution": {k: round(v*100,1) for k, v in health_proba.items()},
        },
        "overdraft_risk": {
            "rating":      od_label,
            "description": od_descriptions[od_label],
            "confidence_pct": round(od_proba.get(od_label, 0) * 100, 1),
            "risk_distribution": {k: round(v*100,1) for k, v in od_proba.items()},
        },
        "key_risk_factors": risk_factors if risk_factors else ["No major red flags identified"],
        "priority_actions": actions,
        "spending_ratios": {
            "savings_rate_pct":       round(savings_r * 100, 1),
            "housing_pct_of_income":  round(monthly_rent / monthly_income * 100, 1),
            "debt_burden_pct":        round(monthly_debt_payments / monthly_income * 100, 1),
            "emergency_fund_months":  round(ef_months, 1),
        },
        "model": "CatBoost classifier trained on 2,000 financial scenarios",
        "disclaimer": "Assessment based on provided data. Not a substitute for professional financial advice.",
    }


# ── Tool definitions (Anthropic schema format) ─────────────────────────────────

SPENDING_PREDICTOR_TOOL_DEFINITIONS = [
    {
        "name": "predict_spending_trajectory",
        "description": (
            "XGBoost ML model: project the user's savings balance at 3, 6, and 12 months "
            "from their current monthly income and spending breakdown. Also calculates "
            "how many months until a 3-month emergency fund is reached. "
            "Use when the user shares their budget and wants to know where they'll be financially. "
            "Handles non-linear effects: high debt + variable income compounds risk in ways "
            "a simple calculation misses."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "monthly_income":        {"type": "number", "description": "Total take-home monthly income after tax"},
                "monthly_rent":          {"type": "number", "description": "Monthly rent or mortgage payment"},
                "monthly_food":          {"type": "number", "description": "Monthly food and groceries spend"},
                "monthly_transport":     {"type": "number", "description": "Monthly transport, fuel, car payments"},
                "monthly_entertainment": {"type": "number", "description": "Monthly entertainment, dining, subscriptions"},
                "monthly_debt_payments": {"type": "number", "description": "Total monthly debt payments (credit cards, loans, excluding mortgage)"},
                "monthly_other":         {"type": "number", "description": "All other monthly expenses", "default": 0},
                "current_savings":       {"type": "number", "description": "Current total savings balance", "default": 0},
                "income_type":           {"type": "string", "enum": ["salary", "hourly", "part_time", "freelance", "commission", "mixed"], "description": "Nature of income (affects variability penalty in projections)"},
            },
            "required": ["monthly_income", "monthly_rent", "monthly_food", "monthly_transport", "monthly_entertainment", "monthly_debt_payments"],
        },
    },
    {
        "name": "predict_financial_health",
        "description": (
            "CatBoost ML model: classify the user's financial health "
            "(CRITICAL / POOR / FAIR / GOOD / EXCELLENT) and overdraft risk "
            "(LOW / MODERATE / HIGH / CRITICAL) from their spending patterns. "
            "Returns confidence scores, top risk factors, and priority actions. "
            "Use when you have the user's full budget and want a diagnostic assessment. "
            "CatBoost natively understands spending category interactions — no feature engineering needed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "monthly_income":        {"type": "number", "description": "Total take-home monthly income after tax"},
                "monthly_rent":          {"type": "number", "description": "Monthly rent or mortgage payment"},
                "monthly_food":          {"type": "number", "description": "Monthly food and groceries spend"},
                "monthly_transport":     {"type": "number", "description": "Monthly transport, fuel, car payments"},
                "monthly_entertainment": {"type": "number", "description": "Monthly entertainment, dining, subscriptions"},
                "monthly_debt_payments": {"type": "number", "description": "Total monthly debt payments"},
                "monthly_other":         {"type": "number", "description": "All other monthly expenses", "default": 0},
                "current_savings":       {"type": "number", "description": "Current total savings balance", "default": 0},
                "income_type":           {"type": "string", "enum": ["salary", "hourly", "part_time", "freelance", "commission", "mixed"], "description": "Nature of income"},
            },
            "required": ["monthly_income", "monthly_rent", "monthly_food", "monthly_transport", "monthly_entertainment", "monthly_debt_payments"],
        },
    },
]

# ── Executor ───────────────────────────────────────────────────────────────────

SPENDING_PREDICTOR_FUNCTIONS = {
    "predict_spending_trajectory": predict_spending_trajectory,
    "predict_financial_health":    predict_financial_health,
}


def execute_spending_predictor_tool(name: str, inputs: dict) -> str:
    fn = SPENDING_PREDICTOR_FUNCTIONS.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown spending predictor tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
