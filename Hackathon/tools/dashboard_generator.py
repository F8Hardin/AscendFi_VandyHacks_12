"""
Financial Dashboard Generator
==============================
Creates interactive HTML dashboards using Plotly when users ask for
financial plans with a specified time period.

Dashboards auto-open in the browser and are saved to ~/.financeai/dashboards/.

Tools exposed (callable by agents):
  generate_debt_payoff_dashboard      — debt timeline, interest vs principal
  generate_investment_dashboard       — compound growth scenarios over time
  generate_budget_dashboard           — income allocation, savings trajectory
  generate_financial_plan_dashboard   — comprehensive multi-panel plan view

Requires: plotly (pip install plotly)
"""

import json
import math
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

DASHBOARD_DIR = Path.home() / ".financeai" / "dashboards"
COLOUR_PALETTE = {
    "red":    "#E74C3C",
    "orange": "#E67E22",
    "green":  "#27AE60",
    "blue":   "#2980B9",
    "purple": "#8E44AD",
    "teal":   "#16A085",
    "gold":   "#F39C12",
    "dark":   "#2C3E50",
    "light":  "#ECF0F1",
    "grid":   "#BDC3C7",
}


def _try_import_plotly():
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        return go, make_subplots
    except ImportError:
        return None, None


def _save_and_open(fig, name: str) -> dict:
    """Write dashboard to disk and open it in the default browser."""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = DASHBOARD_DIR / f"{name}_{ts}.html"
    fig.write_html(
        str(filepath),
        auto_open=False,
        include_plotlyjs="cdn",
        full_html=True,
    )
    webbrowser.open(filepath.resolve().as_uri())
    return {
        "status": "dashboard_opened",
        "filepath": str(filepath),
        "message": f"Dashboard opened in your browser. Saved to {filepath}",
    }


# ── Internal simulation helpers ───────────────────────────────────────────────

def _simulate_debts_monthly(
    debts: list[dict],
    extra_monthly_payment: float,
    strategy: str,
    cap_months: int = 360,
) -> list[dict]:
    """
    Month-by-month debt simulation.
    Returns a list of monthly snapshots:
      [{"month": 1, "total": 12000.0, "Visa": 4000.0, "Car": 8000.0}, ...]
    """
    import copy
    active = copy.deepcopy(debts)
    for d in active:
        d["balance"] = float(d.get("balance", 0))
        d["apr"] = float(d.get("apr", 0))
        d["min_payment"] = float(d.get("min_payment", d.get("minimum_payment", d["balance"] * 0.02)))

    if strategy == "avalanche":
        active.sort(key=lambda x: x["apr"], reverse=True)
    else:
        active.sort(key=lambda x: x["balance"])

    snapshots = []
    for month in range(1, cap_months + 1):
        # Apply interest
        for d in active:
            if d["balance"] > 0:
                d["balance"] += d["balance"] * (d["apr"] / 100 / 12)

        # Apply min payments
        for d in active:
            if d["balance"] > 0:
                payment = min(d["min_payment"], d["balance"])
                d["balance"] = max(0.0, d["balance"] - payment)

        # Apply extra to top-priority debt
        remaining = extra_monthly_payment
        for d in active:
            if d["balance"] > 0 and remaining > 0:
                payment = min(remaining, d["balance"])
                d["balance"] = max(0.0, d["balance"] - payment)
                remaining -= payment
                break

        snap = {"month": month}
        for d in active:
            snap[d["name"]] = round(max(0.0, d["balance"]), 2)
        snap["total"] = round(sum(snap[d["name"]] for d in active), 2)
        snapshots.append(snap)

        if snap["total"] == 0:
            break

    return snapshots


def _simulate_investment_yearly(
    initial: float,
    monthly: float,
    annual_return_pct: float,
    years: int,
) -> list[dict]:
    """Year-by-year investment simulation. Returns [{year, balance, contributed}]."""
    rate = annual_return_pct / 100 / 12
    balance = initial
    contributed = initial
    snapshots = []
    for year in range(1, years + 1):
        for _ in range(12):
            balance = balance * (1 + rate) + monthly
            contributed += monthly
        snapshots.append({
            "year": year,
            "balance": round(balance, 2),
            "contributed": round(contributed, 2),
            "growth": round(balance - contributed, 2),
        })
    return snapshots


# ── Dashboard 1: Debt Payoff ───────────────────────────────────────────────────

def generate_debt_payoff_dashboard(
    debts: list[dict],
    extra_monthly_payment: float = 0,
    strategy: str = "avalanche",
    time_period_months: Optional[int] = None,
    title: str = "Debt Freedom Plan",
) -> dict:
    """
    Generate an interactive debt payoff dashboard.

    Creates:
    - Line chart: total debt balance declining over time
    - Stacked area: per-debt breakdown
    - Donut: interest paid vs principal paid
    - Milestone annotations: when each debt is eliminated

    Returns dict with status, filepath, and summary.
    """
    go, make_subplots = _try_import_plotly()
    if go is None:
        return {"error": "plotly not installed. Run: pip install plotly>=5.0.0"}

    total_debt = sum(float(d.get("balance", 0)) for d in debts)
    snapshots = _simulate_debts_monthly(debts, extra_monthly_payment, strategy)
    payoff_month = len(snapshots)

    # Cap display to time_period_months if specified
    display_months = min(time_period_months or payoff_month, payoff_month)
    snaps = snapshots[:display_months]
    months = [s["month"] for s in snaps]
    total_balances = [s["total"] for s in snaps]

    debt_names = [d["name"] for d in debts]
    colours = [
        COLOUR_PALETTE["red"], COLOUR_PALETTE["orange"], COLOUR_PALETTE["blue"],
        COLOUR_PALETTE["purple"], COLOUR_PALETTE["teal"], COLOUR_PALETTE["green"],
    ]

    # Calculate interest paid per debt
    total_paid = 0.0
    for d in debts:
        total_paid += sum(
            (snaps[i]["total"] - snaps[i - 1]["total"]) if i > 0 else 0
            for i in range(len(snaps))
        )
    # Simpler: total interest = total_paid_over_period - (initial_balance - remaining_balance)
    remaining = snaps[-1]["total"] if snaps else 0
    debt_eliminated = total_debt - remaining
    # Estimate interest: approximate from simulation
    total_min_payments = sum(float(d.get("min_payment", d.get("balance", 0) * 0.02)) for d in debts)
    total_payments_made = (total_min_payments + extra_monthly_payment) * display_months
    interest_paid = max(0, total_payments_made - debt_eliminated)
    principal_paid = debt_eliminated

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Total Debt Balance Over Time",
            "Per-Debt Breakdown",
            "Payments: Principal vs Interest",
            "Monthly Payment Composition",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "pie"},     {"type": "bar"}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    # ── Chart 1: Total balance line ──────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=months, y=total_balances,
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(231,76,60,0.15)",
            line=dict(color=COLOUR_PALETTE["red"], width=3),
            name="Total Debt",
            hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # Mark payoff if within window
    if payoff_month <= display_months:
        fig.add_vline(
            x=payoff_month,
            line_dash="dash",
            line_color=COLOUR_PALETTE["green"],
            row=1, col=1,
            annotation_text=f"✅ Debt Free: Month {payoff_month}",
            annotation_position="top right",
            annotation_font_color=COLOUR_PALETTE["green"],
        )

    # ── Chart 2: Per-debt stacked area ───────────────────────────────────────
    for i, name in enumerate(debt_names):
        per_debt = [s.get(name, 0) for s in snaps]
        fig.add_trace(
            go.Scatter(
                x=months, y=per_debt,
                mode="lines",
                stackgroup="debts",
                name=name,
                line=dict(color=colours[i % len(colours)], width=1),
                fillcolor=colours[i % len(colours)].replace(")", ",0.4)").replace("rgb", "rgba")
                          if colours[i % len(colours)].startswith("rgb") else colours[i % len(colours)] + "66",
                hovertemplate=f"{name}: $%{{y:,.0f}}<extra></extra>",
            ),
            row=1, col=2,
        )

    # ── Chart 3: Donut — principal vs interest ────────────────────────────────
    fig.add_trace(
        go.Pie(
            labels=["Principal Paid", "Interest Paid", "Remaining Balance"],
            values=[round(principal_paid, 0), round(interest_paid, 0), round(remaining, 0)],
            marker=dict(colors=[COLOUR_PALETTE["green"], COLOUR_PALETTE["red"], COLOUR_PALETTE["grid"]]),
            hole=0.45,
            textinfo="label+percent",
            hovertemplate="%{label}: $%{value:,.0f}<extra></extra>",
            showlegend=False,
        ),
        row=2, col=1,
    )

    # ── Chart 4: Monthly payment bar ─────────────────────────────────────────
    bar_months = list(range(1, min(display_months, 24) + 1))
    monthly_payment = total_min_payments + extra_monthly_payment
    principal_per_month = [
        round((snaps[i - 1]["total"] - snaps[i]["total"]) if i > 0 else 0, 2)
        for i in range(min(len(snaps), 24))
    ]
    interest_per_month = [
        max(0, round(monthly_payment - p, 2)) for p in principal_per_month
    ]
    fig.add_trace(
        go.Bar(
            x=bar_months, y=principal_per_month,
            name="Principal",
            marker_color=COLOUR_PALETTE["green"],
            hovertemplate="Month %{x} — Principal: $%{y:,.0f}<extra></extra>",
        ),
        row=2, col=2,
    )
    fig.add_trace(
        go.Bar(
            x=bar_months, y=interest_per_month,
            name="Interest",
            marker_color=COLOUR_PALETTE["red"],
            hovertemplate="Month %{x} — Interest: $%{y:,.0f}<extra></extra>",
        ),
        row=2, col=2,
    )

    yrs = round(payoff_month / 12, 1)
    subtitle = (
        f"Strategy: {strategy.title()} | Starting debt: ${total_debt:,.0f} | "
        f"Extra payment: ${extra_monthly_payment:,.0f}/mo | "
        f"Debt-free in: {yrs} years ({payoff_month} months)"
    )
    fig.update_layout(
        title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0.5, xanchor="center"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", color=COLOUR_PALETTE["dark"]),
        barmode="stack",
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"], tickprefix="$", tickformat=",")

    result = _save_and_open(fig, "debt_payoff")
    result.update({
        "summary": (
            f"Debt payoff dashboard generated. {strategy.title()} strategy: "
            f"debt-free in {yrs} years ({payoff_month} months). "
            f"Total debt: ${total_debt:,.0f}. "
            f"Estimated interest paid: ${interest_paid:,.0f}."
        )
    })
    return result


# ── Dashboard 2: Investment Growth ────────────────────────────────────────────

def generate_investment_dashboard(
    initial_amount: float,
    monthly_contribution: float,
    time_period_years: int,
    title: str = "Investment Growth Projection",
    risk_tolerance: str = "moderate",
) -> dict:
    """
    Generate an investment growth dashboard with three scenarios.

    Creates:
    - Line chart: pessimistic / realistic / optimistic growth curves
    - Area chart: contributions vs compounding growth
    - Bar chart: year-by-year ending balances
    - Summary: total contributed, total growth, retirement readiness
    """
    go, make_subplots = _try_import_plotly()
    if go is None:
        return {"error": "plotly not installed. Run: pip install plotly>=5.0.0"}

    scenarios = {
        "Pessimistic (5%)": 5.0,
        "Realistic (7%)":   7.0,
        "Optimistic (10%)": 10.0,
    }
    scenario_colours = {
        "Pessimistic (5%)": COLOUR_PALETTE["red"],
        "Realistic (7%)":   COLOUR_PALETTE["blue"],
        "Optimistic (10%)": COLOUR_PALETTE["green"],
    }

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Growth Scenarios Over Time",
            "Contributions vs Compounding (Realistic)",
            "Year-by-Year Final Balance",
            "Scenario Comparison at Year " + str(time_period_years),
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "bar"},     {"type": "bar"}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    all_snaps = {}
    for label, rate in scenarios.items():
        snaps = _simulate_investment_yearly(initial_amount, monthly_contribution, rate, time_period_years)
        all_snaps[label] = snaps
        years = [s["year"] for s in snaps]
        balances = [s["balance"] for s in snaps]

        fig.add_trace(
            go.Scatter(
                x=years, y=balances,
                name=label,
                mode="lines+markers",
                line=dict(color=scenario_colours[label], width=2.5),
                marker=dict(size=4),
                hovertemplate=f"{label}<br>Year %{{x}}: $%{{y:,.0f}}<extra></extra>",
            ),
            row=1, col=1,
        )

    # Realistic: contributions vs growth
    realistic_snaps = all_snaps["Realistic (7%)"]
    years = [s["year"] for s in realistic_snaps]
    contributions = [s["contributed"] for s in realistic_snaps]
    growths = [s["growth"] for s in realistic_snaps]

    fig.add_trace(
        go.Scatter(
            x=years, y=contributions,
            name="Total Contributed",
            fill="tozeroy",
            fillcolor="rgba(41,128,185,0.2)",
            line=dict(color=COLOUR_PALETTE["blue"], width=2),
            hovertemplate="Year %{x}: Contributed $%{y:,.0f}<extra></extra>",
        ),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=years, y=[c + g for c, g in zip(contributions, growths)],
            name="Total Balance",
            fill="tonexty",
            fillcolor="rgba(39,174,96,0.25)",
            line=dict(color=COLOUR_PALETTE["green"], width=2),
            hovertemplate="Year %{x}: Balance $%{y:,.0f}<extra></extra>",
        ),
        row=1, col=2,
    )

    # Year-by-year for realistic
    fig.add_trace(
        go.Bar(
            x=years, y=[s["balance"] for s in realistic_snaps],
            name="Year-End Balance (Realistic)",
            marker_color=COLOUR_PALETTE["blue"],
            hovertemplate="Year %{x}: $%{y:,.0f}<extra></extra>",
        ),
        row=2, col=1,
    )

    # Scenario comparison bar
    labels = list(scenarios.keys())
    final_balances = [all_snaps[l][-1]["balance"] for l in labels]
    fig.add_trace(
        go.Bar(
            x=labels, y=final_balances,
            marker_color=[scenario_colours[l] for l in labels],
            showlegend=False,
            hovertemplate="%{x}<br>Final: $%{y:,.0f}<extra></extra>",
            text=[f"${b:,.0f}" for b in final_balances],
            textposition="outside",
        ),
        row=2, col=2,
    )

    total_contrib = realistic_snaps[-1]["contributed"]
    final_realistic = realistic_snaps[-1]["balance"]
    total_growth = realistic_snaps[-1]["growth"]

    subtitle = (
        f"Initial: ${initial_amount:,.0f} | Monthly: ${monthly_contribution:,.0f} | "
        f"Period: {time_period_years} years | "
        f"Realistic outcome: ${final_realistic:,.0f} "
        f"(${total_contrib:,.0f} contributed + ${total_growth:,.0f} growth)"
    )
    fig.update_layout(
        title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0.5, xanchor="center"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", color=COLOUR_PALETTE["dark"]),
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"], tickprefix="$", tickformat=",")

    result = _save_and_open(fig, "investment_growth")
    result.update({
        "summary": (
            f"Investment dashboard generated. Over {time_period_years} years with "
            f"${monthly_contribution:,.0f}/mo contributions starting from ${initial_amount:,.0f}: "
            f"pessimistic ${all_snaps['Pessimistic (5%)'][-1]['balance']:,.0f}, "
            f"realistic ${final_realistic:,.0f}, "
            f"optimistic ${all_snaps['Optimistic (10%)'][-1]['balance']:,.0f}."
        )
    })
    return result


# ── Dashboard 3: Budget Breakdown ────────────────────────────────────────────

def generate_budget_dashboard(
    net_monthly_income: float,
    expenses: dict,         # {"Housing": 1600, "Food": 400, ...}
    time_period_months: int = 12,
    savings_rate_pct: float = 20.0,
    title: str = "Budget & Savings Plan",
) -> dict:
    """
    Generate an interactive budget breakdown dashboard.

    Creates:
    - Donut: income allocation (needs / wants / savings / debt)
    - Bar chart: expense categories ranked
    - Line chart: cumulative savings trajectory over the period
    - Gauge: savings rate vs recommended 20%
    """
    go, make_subplots = _try_import_plotly()
    if go is None:
        return {"error": "plotly not installed. Run: pip install plotly>=5.0.0"}

    total_expenses = sum(expenses.values())
    monthly_surplus = net_monthly_income - total_expenses
    actual_savings_rate = (monthly_surplus / net_monthly_income) * 100 if net_monthly_income else 0

    categories = list(expenses.keys())
    amounts = list(expenses.values())
    sorted_pairs = sorted(zip(amounts, categories), reverse=True)
    sorted_amounts, sorted_cats = zip(*sorted_pairs) if sorted_pairs else ([], [])

    bar_colours = [COLOUR_PALETTE["red"] if a > net_monthly_income * 0.3 else COLOUR_PALETTE["blue"]
                   for a in sorted_amounts]

    # Savings trajectory
    months = list(range(0, time_period_months + 1))
    cumulative_savings = [monthly_surplus * m for m in months]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Income Allocation",
            "Expense Categories",
            "Cumulative Savings Trajectory",
            "Monthly Cash Flow",
        ),
        specs=[
            [{"type": "pie"},     {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}],
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12,
    )

    # ── Donut: income allocation ──────────────────────────────────────────────
    pie_labels = list(expenses.keys()) + ["Monthly Surplus"]
    pie_values = list(expenses.values()) + [max(0, monthly_surplus)]
    pie_colours = (
        [COLOUR_PALETTE["red"], COLOUR_PALETTE["orange"], COLOUR_PALETTE["blue"],
         COLOUR_PALETTE["teal"], COLOUR_PALETTE["purple"], COLOUR_PALETTE["gold"]][:len(expenses)]
        + [COLOUR_PALETTE["green"]]
    )
    fig.add_trace(
        go.Pie(
            labels=pie_labels, values=pie_values,
            marker=dict(colors=pie_colours),
            hole=0.45,
            textinfo="label+percent",
            hovertemplate="%{label}: $%{value:,.0f}/mo<extra></extra>",
            showlegend=False,
        ),
        row=1, col=1,
    )

    # ── Bar: expense categories ───────────────────────────────────────────────
    fig.add_trace(
        go.Bar(
            x=list(sorted_amounts), y=list(sorted_cats),
            orientation="h",
            marker_color=bar_colours,
            hovertemplate="%{y}: $%{x:,.0f}/mo<extra></extra>",
            showlegend=False,
        ),
        row=1, col=2,
    )

    # ── Line: cumulative savings ──────────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=months, y=cumulative_savings,
            mode="lines+markers",
            fill="tozeroy",
            fillcolor="rgba(39,174,96,0.15)",
            line=dict(color=COLOUR_PALETTE["green"], width=2.5),
            marker=dict(size=4),
            name="Cumulative Savings",
            hovertemplate="Month %{x}: $%{y:,.0f} saved<extra></extra>",
        ),
        row=2, col=1,
    )

    # ── Bar: monthly cash flow (income vs expenses) ───────────────────────────
    flow_labels = ["Income", "Expenses", "Surplus"]
    flow_values = [net_monthly_income, total_expenses, max(0, monthly_surplus)]
    flow_colours = [COLOUR_PALETTE["green"], COLOUR_PALETTE["red"],
                    COLOUR_PALETTE["teal"] if monthly_surplus >= 0 else COLOUR_PALETTE["red"]]
    fig.add_trace(
        go.Bar(
            x=flow_labels, y=flow_values,
            marker_color=flow_colours,
            text=[f"${v:,.0f}" for v in flow_values],
            textposition="outside",
            hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
            showlegend=False,
        ),
        row=2, col=2,
    )

    total_saved = monthly_surplus * time_period_months
    subtitle = (
        f"Monthly income: ${net_monthly_income:,.0f} | "
        f"Total expenses: ${total_expenses:,.0f} | "
        f"Monthly surplus: ${monthly_surplus:,.0f} | "
        f"Savings rate: {actual_savings_rate:.1f}% | "
        f"Projected savings in {time_period_months} months: ${total_saved:,.0f}"
    )
    fig.update_layout(
        title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0.5, xanchor="center"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", color=COLOUR_PALETTE["dark"]),
        height=700,
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"], row=2, col=1)
    fig.update_yaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"])

    result = _save_and_open(fig, "budget_plan")
    result.update({
        "summary": (
            f"Budget dashboard generated. Monthly surplus: ${monthly_surplus:,.0f} "
            f"({actual_savings_rate:.1f}% savings rate). "
            f"Over {time_period_months} months you'll save ${total_saved:,.0f}."
        )
    })
    return result


# ── Dashboard 4: Comprehensive Financial Plan (Supervisor tool) ───────────────

def generate_financial_plan_dashboard(
    time_period_months: int,
    title: str = "My Financial Plan",
    net_monthly_income: float = 0,
    monthly_expenses: float = 0,
    debts: Optional[list[dict]] = None,
    extra_debt_payment: float = 0,
    debt_strategy: str = "avalanche",
    initial_investment: float = 0,
    monthly_investment: float = 0,
    current_savings: float = 0,
) -> dict:
    """
    Comprehensive multi-panel financial plan dashboard.

    Combines into a single dashboard:
    - Net worth trajectory (savings + investments - debt)
    - Debt elimination timeline
    - Investment compound growth (realistic scenario)
    - Monthly cash flow breakdown
    - Key milestone annotations
    - Progress indicators

    This is the Supervisor-level tool called after agents have provided their analysis.
    """
    go, make_subplots = _try_import_plotly()
    if go is None:
        return {"error": "plotly not installed. Run: pip install plotly>=5.0.0"}

    debts = debts or []
    time_period_years = max(1, round(time_period_months / 12))
    months = list(range(0, time_period_months + 1))

    # ── Simulate debt payoff ─────────────────────────────────────────────────
    debt_snaps = []
    if debts:
        debt_snaps = _simulate_debts_monthly(debts, extra_debt_payment, debt_strategy, time_period_months)

    def total_debt_at(m: int) -> float:
        if not debt_snaps:
            return 0.0
        idx = min(m - 1, len(debt_snaps) - 1)
        return debt_snaps[idx]["total"] if m > 0 else sum(float(d.get("balance", 0)) for d in debts)

    # ── Simulate savings ─────────────────────────────────────────────────────
    monthly_surplus = max(0, net_monthly_income - monthly_expenses) if net_monthly_income else 0
    savings_at = [current_savings + monthly_surplus * m for m in months]

    # ── Simulate investment ──────────────────────────────────────────────────
    inv_snaps = []
    if initial_investment or monthly_investment:
        inv_snaps = _simulate_investment_yearly(
            initial_investment, monthly_investment, 7.0, time_period_years
        )

    def investment_at_month(m: int) -> float:
        if not inv_snaps:
            return initial_investment if m == 0 else initial_investment + monthly_investment * m
        year_idx = min(int(m / 12), len(inv_snaps) - 1)
        return inv_snaps[year_idx]["balance"]

    # ── Net worth ─────────────────────────────────────────────────────────────
    net_worth = [
        savings_at[m] + investment_at_month(m) - total_debt_at(m)
        for m in months
    ]

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            "Net Worth Trajectory",
            "Debt Elimination Timeline",
            "Investment Growth (7% Scenario)",
            "Monthly Cash Flow",
            "Savings Accumulation",
            "Financial Milestones",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}],
        ],
        vertical_spacing=0.10,
        horizontal_spacing=0.10,
        row_heights=[0.35, 0.35, 0.30],
    )

    # ── Chart 1: Net Worth ────────────────────────────────────────────────────
    net_worth_colour = [COLOUR_PALETTE["red"] if nw < 0 else COLOUR_PALETTE["teal"] for nw in net_worth]
    fig.add_trace(
        go.Scatter(
            x=months, y=net_worth,
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(22,160,133,0.15)",
            line=dict(color=COLOUR_PALETTE["teal"], width=3),
            name="Net Worth",
            hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>",
        ),
        row=1, col=1,
    )
    fig.add_hline(y=0, line_dash="dash", line_color=COLOUR_PALETTE["grid"], row=1, col=1)

    # ── Chart 2: Debt Timeline ────────────────────────────────────────────────
    if debt_snaps:
        debt_months = [s["month"] for s in debt_snaps[:time_period_months]]
        debt_totals = [s["total"] for s in debt_snaps[:time_period_months]]
        fig.add_trace(
            go.Scatter(
                x=debt_months, y=debt_totals,
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(231,76,60,0.15)",
                line=dict(color=COLOUR_PALETTE["red"], width=2.5),
                name="Total Debt",
                hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>",
            ),
            row=1, col=2,
        )
        payoff_m = len(debt_snaps)
        if payoff_m <= time_period_months:
            fig.add_annotation(
                x=payoff_m, y=0,
                text="🎉 Debt Free!",
                arrowhead=2,
                arrowcolor=COLOUR_PALETTE["green"],
                font=dict(color=COLOUR_PALETTE["green"], size=11),
                row=1, col=2,
            )
    else:
        fig.add_trace(
            go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0),
                       name="No debt data", showlegend=False),
            row=1, col=2,
        )

    # ── Chart 3: Investment Growth ────────────────────────────────────────────
    if inv_snaps:
        inv_years = [s["year"] for s in inv_snaps]
        inv_balances = [s["balance"] for s in inv_snaps]
        inv_contrib = [s["contributed"] for s in inv_snaps]
        fig.add_trace(
            go.Scatter(
                x=inv_years, y=inv_contrib,
                name="Contributions",
                fill="tozeroy",
                fillcolor="rgba(41,128,185,0.2)",
                line=dict(color=COLOUR_PALETTE["blue"], width=1.5),
                hovertemplate="Year %{x}: Contributed $%{y:,.0f}<extra></extra>",
            ),
            row=2, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=inv_years, y=inv_balances,
                name="Portfolio Value",
                fill="tonexty",
                fillcolor="rgba(39,174,96,0.25)",
                line=dict(color=COLOUR_PALETTE["green"], width=2.5),
                hovertemplate="Year %{x}: $%{y:,.0f}<extra></extra>",
            ),
            row=2, col=1,
        )

    # ── Chart 4: Monthly Cash Flow ────────────────────────────────────────────
    if net_monthly_income:
        surplus = max(0, net_monthly_income - monthly_expenses)
        debt_pmt = extra_debt_payment + sum(float(d.get("min_payment", 0)) for d in debts)
        invest_pmt = monthly_investment
        remaining_exp = monthly_expenses
        labels_cf = ["Expenses", "Debt Payments", "Investments", "Savings"]
        values_cf = [
            max(0, remaining_exp - debt_pmt),
            debt_pmt,
            invest_pmt,
            max(0, surplus - invest_pmt),
        ]
        colours_cf = [COLOUR_PALETTE["orange"], COLOUR_PALETTE["red"],
                      COLOUR_PALETTE["green"], COLOUR_PALETTE["teal"]]
        fig.add_trace(
            go.Bar(
                x=labels_cf, y=values_cf,
                marker_color=colours_cf,
                text=[f"${v:,.0f}" for v in values_cf],
                textposition="outside",
                showlegend=False,
                hovertemplate="%{x}: $%{y:,.0f}/mo<extra></extra>",
            ),
            row=2, col=2,
        )

    # ── Chart 5: Savings Accumulation ────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=months, y=savings_at,
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(142,68,173,0.15)",
            line=dict(color=COLOUR_PALETTE["purple"], width=2.5),
            name="Savings",
            hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>",
        ),
        row=3, col=1,
    )

    # ── Chart 6: Key Milestones ────────────────────────────────────────────────
    milestones = []
    milestone_values = []
    milestone_colours = []

    if debts:
        total_debt_start = sum(float(d.get("balance", 0)) for d in debts)
        payoff_mo = len(debt_snaps) if debt_snaps else 0
        if payoff_mo and payoff_mo <= time_period_months:
            milestones.append(f"Debt Free\n(Month {payoff_mo})")
            milestone_values.append(total_debt_start)
            milestone_colours.append(COLOUR_PALETTE["green"])

    if net_monthly_income:
        emergency_target = monthly_expenses * 6
        em_months = math.ceil(emergency_target / max(monthly_surplus, 1)) if monthly_surplus > 0 else 999
        if em_months <= time_period_months:
            milestones.append(f"6-Month\nEmergency Fund\n(Month {em_months})")
            milestone_values.append(emergency_target)
            milestone_colours.append(COLOUR_PALETTE["teal"])

    if inv_snaps:
        milestones.append(f"Portfolio at\nYear {time_period_years}")
        milestone_values.append(inv_snaps[-1]["balance"])
        milestone_colours.append(COLOUR_PALETTE["blue"])

    milestones.append(f"Net Worth at\nMonth {time_period_months}")
    milestone_values.append(net_worth[-1])
    milestone_colours.append(COLOUR_PALETTE["purple"] if net_worth[-1] >= 0 else COLOUR_PALETTE["red"])

    fig.add_trace(
        go.Bar(
            x=milestones,
            y=milestone_values,
            marker_color=milestone_colours,
            text=[f"${v:,.0f}" for v in milestone_values],
            textposition="outside",
            showlegend=False,
            hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
        ),
        row=3, col=2,
    )

    time_label = (
        f"{time_period_years} year{'s' if time_period_years != 1 else ''}"
        if time_period_years >= 1
        else f"{time_period_months} months"
    )
    subtitle_parts = []
    if net_monthly_income:
        subtitle_parts.append(f"Income: ${net_monthly_income:,.0f}/mo")
    if debts:
        total_debt_s = sum(float(d.get("balance", 0)) for d in debts)
        subtitle_parts.append(f"Debt: ${total_debt_s:,.0f}")
    if monthly_investment:
        subtitle_parts.append(f"Investing: ${monthly_investment:,.0f}/mo")
    subtitle_parts.append(f"Period: {time_label}")
    subtitle_parts.append(f"Projected net worth: ${net_worth[-1]:,.0f}")

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br><sup>{' | '.join(subtitle_parts)}</sup>",
            x=0.5,
            xanchor="center",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", color=COLOUR_PALETTE["dark"]),
        height=950,
        legend=dict(orientation="h", yanchor="bottom", y=-0.08, xanchor="center", x=0.5),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=COLOUR_PALETTE["grid"], tickprefix="$", tickformat=",")

    result = _save_and_open(fig, "financial_plan")
    result.update({
        "summary": (
            f"Comprehensive financial plan dashboard generated for {time_label}. "
            f"Projected net worth: ${net_worth[-1]:,.0f}. "
            + (f"Debt-free in {len(debt_snaps)} months. " if debt_snaps and len(debt_snaps) <= time_period_months else "")
            + (f"Investment portfolio: ${inv_snaps[-1]['balance']:,.0f} at year {time_period_years}." if inv_snaps else "")
        )
    })
    return result


# ── Tool registration ─────────────────────────────────────────────────────────

DASHBOARD_TOOL_DEFINITIONS = [
    {
        "name": "generate_debt_payoff_dashboard",
        "description": (
            "Generate an interactive visual dashboard for a debt payoff plan over a specified time period. "
            "Shows: debt balance declining over time, per-debt breakdown, interest vs principal paid, "
            "monthly payment composition. Dashboard opens automatically in the user's browser. "
            "Call this whenever the user asks for a debt plan with a timeline or time period."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "debts": {
                    "type": "array",
                    "description": "List of debts",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name":        {"type": "string",  "description": "Debt name (e.g. 'Visa Card')"},
                            "balance":     {"type": "number",  "description": "Current balance in dollars"},
                            "apr":         {"type": "number",  "description": "Annual interest rate (%)"},
                            "min_payment": {"type": "number",  "description": "Minimum monthly payment"},
                        },
                        "required": ["name", "balance", "apr", "min_payment"],
                    },
                },
                "extra_monthly_payment": {
                    "type": "number",
                    "description": "Extra monthly payment applied to priority debt (above minimums)",
                    "default": 0,
                },
                "strategy": {
                    "type": "string",
                    "enum": ["avalanche", "snowball"],
                    "description": "Payoff strategy: avalanche (highest APR first) or snowball (lowest balance first)",
                    "default": "avalanche",
                },
                "time_period_months": {
                    "type": "integer",
                    "description": "Number of months to show in the chart (defaults to full payoff period)",
                },
                "title": {
                    "type": "string",
                    "description": "Dashboard title shown at the top",
                    "default": "Debt Freedom Plan",
                },
            },
            "required": ["debts"],
        },
    },
    {
        "name": "generate_investment_dashboard",
        "description": (
            "Generate an interactive investment growth dashboard showing compound growth scenarios "
            "over a specified time period. Shows: pessimistic/realistic/optimistic growth curves, "
            "contributions vs compounding, year-by-year balances, scenario comparison. "
            "Dashboard opens automatically in the user's browser. "
            "Call this whenever the user asks for an investment plan or retirement projection with a time period."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "initial_amount": {
                    "type": "number",
                    "description": "Starting investment amount in dollars",
                },
                "monthly_contribution": {
                    "type": "number",
                    "description": "Monthly investment contribution in dollars",
                },
                "time_period_years": {
                    "type": "integer",
                    "description": "Investment horizon in years",
                },
                "title": {
                    "type": "string",
                    "description": "Dashboard title",
                    "default": "Investment Growth Projection",
                },
                "risk_tolerance": {
                    "type": "string",
                    "enum": ["conservative", "moderate", "aggressive"],
                    "description": "User's risk tolerance",
                    "default": "moderate",
                },
            },
            "required": ["initial_amount", "monthly_contribution", "time_period_years"],
        },
    },
    {
        "name": "generate_budget_dashboard",
        "description": (
            "Generate an interactive budget breakdown and savings trajectory dashboard. "
            "Shows: income allocation donut, expense categories ranked, cumulative savings over time, "
            "monthly cash flow. Dashboard opens automatically in the user's browser. "
            "Call this whenever the user asks for a budget plan or savings projection with a time period."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "net_monthly_income": {
                    "type": "number",
                    "description": "Monthly take-home income after tax",
                },
                "expenses": {
                    "type": "object",
                    "description": "Dictionary of expense category to monthly amount, e.g. {\"Housing\": 1600, \"Food\": 400}",
                    "additionalProperties": {"type": "number"},
                },
                "time_period_months": {
                    "type": "integer",
                    "description": "Savings projection period in months",
                    "default": 12,
                },
                "title": {
                    "type": "string",
                    "description": "Dashboard title",
                    "default": "Budget & Savings Plan",
                },
            },
            "required": ["net_monthly_income", "expenses"],
        },
    },
    {
        "name": "generate_financial_plan_dashboard",
        "description": (
            "Generate a COMPREHENSIVE multi-panel financial plan dashboard combining debt payoff, "
            "investment growth, savings accumulation, net worth trajectory, cash flow breakdown, "
            "and key financial milestones — all in one visual. Dashboard opens automatically in the browser. "
            "Call this for any request involving a full financial plan or roadmap with a specified time period. "
            "Provide as much data as available; all fields except time_period_months are optional."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "time_period_months": {
                    "type": "integer",
                    "description": "Plan duration in months (e.g. 60 for 5 years, 120 for 10 years)",
                },
                "title": {
                    "type": "string",
                    "description": "Dashboard title (e.g. 'Sarah's 5-Year Financial Plan')",
                    "default": "My Financial Plan",
                },
                "net_monthly_income": {
                    "type": "number",
                    "description": "Monthly take-home income after tax",
                    "default": 0,
                },
                "monthly_expenses": {
                    "type": "number",
                    "description": "Total monthly expenses (excluding debt payments)",
                    "default": 0,
                },
                "debts": {
                    "type": "array",
                    "description": "List of current debts [{name, balance, apr, min_payment}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name":        {"type": "string"},
                            "balance":     {"type": "number"},
                            "apr":         {"type": "number"},
                            "min_payment": {"type": "number"},
                        },
                        "required": ["name", "balance", "apr", "min_payment"],
                    },
                    "default": [],
                },
                "extra_debt_payment": {
                    "type": "number",
                    "description": "Extra monthly payment applied above debt minimums",
                    "default": 0,
                },
                "debt_strategy": {
                    "type": "string",
                    "enum": ["avalanche", "snowball"],
                    "default": "avalanche",
                },
                "initial_investment": {
                    "type": "number",
                    "description": "Current investment/savings already invested",
                    "default": 0,
                },
                "monthly_investment": {
                    "type": "number",
                    "description": "Monthly amount added to investments",
                    "default": 0,
                },
                "current_savings": {
                    "type": "number",
                    "description": "Current liquid savings (emergency fund, bank balance)",
                    "default": 0,
                },
            },
            "required": ["time_period_months"],
        },
    },
]

DASHBOARD_TOOL_FUNCTIONS = {
    "generate_debt_payoff_dashboard":    generate_debt_payoff_dashboard,
    "generate_investment_dashboard":     generate_investment_dashboard,
    "generate_budget_dashboard":         generate_budget_dashboard,
    "generate_financial_plan_dashboard": generate_financial_plan_dashboard,
}


def execute_dashboard_tool(name: str, inputs: dict) -> str:
    """Dispatch a dashboard tool call and return JSON string result."""
    fn = DASHBOARD_TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown dashboard tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result)
    except Exception as exc:
        return json.dumps({"error": str(exc), "tool": name})
