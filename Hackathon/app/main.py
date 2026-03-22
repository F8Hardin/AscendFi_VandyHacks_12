"""
AscendFi FastAPI Server

Exposes the multi-agent financial system as HTTP endpoints that the
Nuxt frontend and Node backend can consume.

Endpoints
─────────
GET  /health                         Health check (used by Node container orchestrator)
POST /chat/stream                    SSE streaming chat via SupervisorAgent (ARIA)
POST /api/dashboard                  AI-computed financial dashboard payload
GET  /api/market/quotes              Batch real-time stock/ETF quotes (yfinance)
GET  /api/market/history/{symbol}    Price history for a symbol (for chart)
GET  /api/market/overview            Major indices snapshot (S&P 500, NASDAQ, etc.)
"""

import asyncio
import json
import math
import queue as stdlib_queue
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# ── Path setup ────────────────────────────────────────────────────────────────
# Ensure the Hackathon root is on sys.path so agents/tools/config are importable
# when uvicorn starts from `cwd=Hackathon/` with module `app.main:app`.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="AscendFi Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Supervisor singleton ───────────────────────────────────────────────────────
_supervisor = None
_supervisor_lock = threading.Lock()


def get_supervisor():
    global _supervisor
    if _supervisor is None:
        with _supervisor_lock:
            if _supervisor is None:
                from agents.supervisor import SupervisorAgent  # noqa: PLC0415
                _supervisor = SupervisorAgent()
    return _supervisor


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Chat stream ───────────────────────────────────────────────────────────────

@app.post("/chat/stream")
async def chat_stream(request: Request):
    """
    SSE endpoint: run messages through the SupervisorAgent (ARIA) and stream
    the response back token-by-token.

    Request body:
      { messages: [{role, content}, ...], context: { ...financial snapshot } }

    SSE event types:
      data: {"type": "token",      "text":    "..."}
      data: {"type": "tool_start", "name":    "Risk Agent"}
      data: {"type": "error",      "message": "..."}
      data: {"type": "done"}
    """
    body = await request.json()
    messages: list[dict] = body.get("messages", [])
    context: dict = body.get("context", {})

    # Extract last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg["content"]
            break

    if not user_message:
        async def _empty():
            yield f'data: {json.dumps({"type": "done"})}\n\n'
        return StreamingResponse(_empty(), media_type="text/event-stream")

    # Prepend financial context so ARIA has the full picture
    if context:
        ctx_lines = json.dumps(context, indent=2)
        user_message = f"[User Financial Context]\n{ctx_lines}\n\n{user_message}"

    supervisor = get_supervisor()
    event_queue: stdlib_queue.Queue = stdlib_queue.Queue()

    def _stream_callback(text: str) -> None:
        """Translate supervisor output tokens into SSE event dicts."""
        if not text:
            return
        stripped = text.strip()
        # Supervisor emits "🔄 Consulting AgentName..." when delegating
        if "🔄 Consulting" in text:
            agent_name = stripped.replace("🔄 Consulting", "").replace("...", "").strip()
            event_queue.put({"type": "tool_start", "name": agent_name})
        # Skip box-drawing characters from the agent output panes
        elif stripped and not stripped.startswith("┌") and not stripped.startswith("└") and not stripped.startswith("│") and not stripped.startswith("─"):
            event_queue.put({"type": "token", "text": text})

    def _run_agent() -> None:
        try:
            supervisor.chat(user_message, stream_callback=_stream_callback)
        except Exception as exc:  # noqa: BLE001
            event_queue.put({"type": "error", "message": str(exc)})
        finally:
            event_queue.put(None)  # sentinel

    thread = threading.Thread(target=_run_agent, daemon=True)
    thread.start()

    async def _generate():
        loop = asyncio.get_running_loop()
        while True:
            try:
                event = await loop.run_in_executor(
                    None,
                    lambda: event_queue.get(timeout=120),  # 2-min hard timeout
                )
            except stdlib_queue.Empty:
                yield f'data: {json.dumps({"type": "error", "message": "Agent response timeout"})}\n\n'
                break
            if event is None:
                yield f'data: {json.dumps({"type": "done"})}\n\n'
                break
            yield f'data: {json.dumps(event)}\n\n'

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

CHART_COLORS = [
    "var(--chart-1)", "var(--chart-2)", "var(--chart-3)",
    "var(--chart-4)", "var(--chart-5)", "var(--chart-6)", "var(--chart-7)",
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@app.post("/api/dashboard")
async def generate_dashboard(request: Request):
    """
    Run the full suite of financial calculation tools against the user's
    profile and return a dashboard payload matching the DashboardPayload
    shape expected by the Nuxt frontend.

    Request body:
    {
      "profile": {
        "name":          string,
        "monthlyIncome": number,
        "checking":      number,
        "savings":       number,
        "creditScore":   number,
        "age":           number  (optional, default 30),
        "monthlyRent":   number  (optional),
        "debts": [
          { name, balance, rate, min, type, dueInDays?, creditLimit? }
        ],
        "transactions":  [{ date, description, amount, category }],
        "recentActivity": [{ date, description, amount, category }]
      }
    }
    """
    body = await request.json()
    profile: dict[str, Any] = body.get("profile", {})

    # ── Extract inputs ─────────────────────────────────────────────────────────
    name           = profile.get("name", "User")
    monthly_income = float(profile.get("monthlyIncome", 4500))
    checking       = float(profile.get("checking", 1247.83))
    savings        = float(profile.get("savings", 823.50))
    credit_score   = int(profile.get("creditScore", 634))
    age            = int(profile.get("age", 30))
    raw_debts      = profile.get("debts", [])
    transactions   = profile.get("transactions", [])
    recent_activity = profile.get("recentActivity", [])

    # Normalise debt fields (frontend sends camelCase)
    debts_calc = [
        {
            "name":        d.get("name", "Debt"),
            "balance":     float(d.get("balance", 0)),
            "apr":         float(d.get("rate", d.get("apr", 0))),
            "min_payment": float(d.get("min", d.get("min_payment", 0))),
        }
        for d in raw_debts
    ]

    total_debt        = sum(d["balance"] for d in debts_calc)
    total_min_payment = sum(d["min_payment"] for d in debts_calc)
    monthly_rent      = float(profile.get("monthlyRent", monthly_income * 0.30))
    # Rough monthly expense estimate: rent + debt mins + living costs
    monthly_expenses  = monthly_rent + total_min_payment + (monthly_income * 0.25)

    # ── Import calculators ─────────────────────────────────────────────────────
    from tools.financial_calculators import (  # noqa: PLC0415
        analyse_spending_patterns,
        assess_missing_payment_risk,
        calculate_overdraft_probability,
        debt_payoff_plan,
        net_worth_tracker,
        paycheck_split_recommendation,
        predict_credit_score_change,
    )

    # ── Risk: overdraft ────────────────────────────────────────────────────────
    overdraft_result = calculate_overdraft_probability(
        average_daily_balance=checking,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        num_overdrafts_last_12m=1,
    )
    overdraft_prob  = overdraft_result["overdraft_probability"]
    overdraft_level = overdraft_result["risk_level"].lower()

    # ── Risk: credit shift ─────────────────────────────────────────────────────
    # Estimate utilization from debts (credit cards only)
    cc_balance = sum(d["balance"] for d in debts_calc
                     if "credit" in d.get("name", "").lower() or d.get("type", "").lower() in ("credit card", "credit"))
    cc_limit   = sum(
        float(d.get("creditLimit", d.get("balance", 1) * 1.4))
        for d in raw_debts
        if "credit" in d.get("name", "").lower() or d.get("type", "").lower() in ("credit card", "credit")
    ) or max(cc_balance * 1.4, 1)
    credit_utilization = min((cc_balance / cc_limit) * 100, 100) if cc_limit else 71.0

    credit_result = predict_credit_score_change(
        current_score=credit_score,
        credit_utilization_pct=credit_utilization,
        missed_payments_last_6m=1,
        new_credit_inquiries=0,
        account_age_years=float(profile.get("accountAgeYears", 4.0)),
    )
    credit_change = credit_result["expected_change"]
    credit_prob   = min(0.99, abs(credit_change) / 100) if credit_change < 0 else 0.1
    credit_level  = "high" if credit_change <= -20 else "moderate" if credit_change < 0 else "low"

    # ── Risk: missing payments ─────────────────────────────────────────────────
    bills_for_risk = [
        {
            "name":              d.get("name", "Debt"),
            "amount":            float(d.get("min", d.get("min_payment", 0))),
            "due_date_days_away": int(d.get("dueInDays", 30)),
            "autopay":           False,
        }
        for d in raw_debts
    ]
    payment_result = assess_missing_payment_risk(
        bills=bills_for_risk,
        current_balance=checking,
    )
    at_risk_count = payment_result["at_risk_count"]
    total_bills   = max(payment_result["bills_analysed"], 1)
    payment_prob  = min(0.99, at_risk_count / total_bills * 0.8
                        + (0.2 if checking < total_min_payment else 0))
    payment_level = "high" if payment_prob > 0.6 else "moderate" if payment_prob > 0.3 else "low"

    # ── Paycheck split ─────────────────────────────────────────────────────────
    paycheck_result = paycheck_split_recommendation(
        net_monthly_income=monthly_income,
        current_rent=monthly_rent,
        current_debt_payments=total_min_payment,
        has_emergency_fund=(savings >= monthly_income * 0.5),
        retirement_contribution_pct=3.0,
    )
    alloc = paycheck_result["allocation"]
    paycheck_amounts = [
        round(alloc["needs_50pct"]["target"], 2),
        round(alloc["needs_50pct"]["rent_debt"], 2),
        round(alloc["savings_20pct"]["emergency_fund"], 2),
        round(alloc["savings_20pct"]["investing"], 2),
        round(alloc["wants_30pct"]["target"], 2),
    ]

    # ── Net worth ──────────────────────────────────────────────────────────────
    nw_result = net_worth_tracker(
        assets={"Checking Account": checking, "Savings Account": savings},
        liabilities={d["name"]: d["balance"] for d in debts_calc},
    )

    # ── Spending patterns ──────────────────────────────────────────────────────
    if transactions:
        spend_result = analyse_spending_patterns(
            transactions=[
                {
                    "category": t.get("category", "Other"),
                    "amount":   abs(float(t.get("amount", 0))),
                    "merchant": t.get("description", ""),
                    "date_label": t.get("date", ""),
                }
                for t in transactions
                if float(t.get("amount", 0)) < 0  # expenses only
            ]
        )
        spend_cats: dict[str, float] = {
            c["category"]: c["amount"]
            for c in spend_result["top_5_categories"]
        }
    else:
        # Default spending distribution from income
        spend_cats = {
            "Housing":       round(monthly_rent, 2),
            "Food":          round(monthly_income * 0.15, 2),
            "Transport":     round(monthly_income * 0.065, 2),
            "Utilities":     round(monthly_income * 0.04, 2),
            "Entertainment": round(monthly_income * 0.04, 2),
            "Medical":       round(monthly_income * 0.02, 2),
            "Misc":          round(monthly_income * 0.047, 2),
        }

    spend_labels  = list(spend_cats.keys())
    spend_amounts = [round(v, 2) for v in spend_cats.values()]
    spend_colors  = CHART_COLORS[:len(spend_labels)]

    # ── Debt timeline chart ────────────────────────────────────────────────────
    extra_payment    = max(0.0, monthly_income * 0.15 - total_min_payment)
    future_months    = _future_month_labels(11)
    debt_timeline    = _project_debt_timeline(
        debts_calc, total_min_payment + extra_payment, 11
    )

    # ── Financial gains chart (last 6 months) ─────────────────────────────────
    past_labels    = _past_month_labels(6)
    savings_series = _project_savings_trend(savings, monthly_income, monthly_expenses, 6)
    net_gain_series = [
        round(savings_series[i] - (savings_series[i - 1] if i > 0 else savings), 2)
        for i in range(6)
    ]

    # ── Recent activity fallback ───────────────────────────────────────────────
    if not recent_activity:
        recent_activity = [
            {"date": "Today",     "description": "Paycheck Deposit",  "amount":  round(monthly_income / 2, 2),     "category": "Income"},
            {"date": "Yesterday", "description": "Grocery Store",     "amount": -round(monthly_income * 0.038, 2), "category": "Food"},
            {"date": "2d ago",    "description": "Gas Station",       "amount": -round(monthly_income * 0.012, 2), "category": "Transport"},
        ]

    # ── Behavior insights ──────────────────────────────────────────────────────
    behavior = _build_behavior(spend_cats, monthly_income, overdraft_prob, total_debt)

    # ── Assemble payload ───────────────────────────────────────────────────────
    return {
        "user": {
            "name": name,
            "monthlyIncome": monthly_income,
        },
        "accounts": {
            "checking":   checking,
            "savings":    savings,
            "creditScore": credit_score,
            "netWorth":   nw_result["net_worth"],
        },
        "risks": {
            "overdraft": {
                "probability": overdraft_prob,
                "level":       overdraft_level,
                "label":       "Overdraft Risk",
                "factors": [
                    f"${checking:,.0f} balance vs ${monthly_expenses:,.0f} in monthly expenses",
                    f"{overdraft_result['buffer_days_of_cash']:.1f} days of cash buffer remaining",
                    overdraft_result["recommendation"],
                ],
            },
            "missingPayments": {
                "probability": round(payment_prob, 2),
                "level":       payment_level,
                "label":       "Missing Payments",
                "factors": [
                    (f"{at_risk_count} bill(s) at risk of being missed"
                     if at_risk_count else "All upcoming bills appear covered"),
                    f"${checking:,.0f} checking balance",
                    f"${total_min_payment:,.0f} total minimum payments due",
                ],
            },
            "creditShift": {
                "probability": round(credit_prob, 2),
                "level":       credit_level,
                "label":       "Credit Score Drop",
                "factors": (
                    credit_result["key_factors"][:3]
                    if credit_result["key_factors"]
                    else [
                        f"Current score: {credit_score}",
                        f"3-month projection: {credit_change:+d} pts",
                        credit_result["priority_action"],
                    ]
                ),
            },
        },
        "debts": [
            {
                "name":      d.get("name", "Debt"),
                "balance":   float(d.get("balance", 0)),
                "rate":      float(d.get("rate", d.get("apr", 0))),
                "min":       float(d.get("min", d.get("min_payment", 0))),
                "type":      d.get("type", "Debt"),
                "dueInDays": int(d.get("dueInDays", 30)),
                **({"creditLimit": float(d["creditLimit"])} if "creditLimit" in d else {}),
                **({"last4": d["last4"]} if "last4" in d else {}),
            }
            for d in raw_debts
        ],
        "spending": {
            "labels":  spend_labels,
            "amounts": spend_amounts,
            "colors":  spend_colors,
        },
        "debtTimeline": {
            "labels": ["Now", *future_months],
            "datasets": [{
                "label": "Total Debt",
                "data":  debt_timeline,
                "color": "#ef4444",
                "fill":  True,
            }],
        },
        "financialGains": {
            "labels": past_labels,
            "datasets": [
                {
                    "label": "Net Monthly Gain",
                    "data":  net_gain_series,
                    "color": "#22c55e",
                    "fill":  True,
                },
                {
                    "label":  "Savings Balance",
                    "data":   savings_series,
                    "color":  "#3b82f6",
                    "fill":   False,
                    "dashed": True,
                },
            ],
        },
        "paycheckSplit": {
            "labels":  ["Needs", "Debt Payoff", "Emergency Fund", "Investments", "Discretionary"],
            "amounts": paycheck_amounts,
            "colors":  ["var(--chart-1)", "var(--color-danger)", "var(--chart-2)", "var(--chart-4)", "var(--chart-3)"],
        },
        "behavior":       behavior,
        "recentActivity": recent_activity,
    }


# ── Chart helpers ──────────────────────────────────────────────────────────────

def _future_month_labels(n: int) -> list[str]:
    now = datetime.now()
    return [MONTH_NAMES[(now.month - 1 + i) % 12] for i in range(1, n + 1)]


def _past_month_labels(n: int) -> list[str]:
    now = datetime.now()
    return [MONTH_NAMES[(now.month - 1 - (n - 1 - i)) % 12] for i in range(n)]


def _project_debt_timeline(
    debts: list[dict], monthly_payment: float, months: int
) -> list[float]:
    """Simulate debt payoff (avalanche) for N future months."""
    if not debts:
        return [0.0] * (months + 1)

    balances = {d["name"]: d["balance"] for d in debts}
    priority = sorted(debts, key=lambda d: d["apr"], reverse=True)
    total    = sum(balances.values())
    timeline = [round(total, 2)]

    for _ in range(months):
        remaining = monthly_payment
        for d in priority:
            name = d["name"]
            if balances[name] <= 0:
                continue
            rate     = d["apr"] / 100 / 12
            interest = balances[name] * rate
            payment  = min(remaining, balances[name] + interest)
            balances[name] = max(0.0, balances[name] + interest - payment)
            remaining = max(0.0, remaining - payment)
            if remaining <= 0:
                break
        timeline.append(round(sum(max(0.0, b) for b in balances.values()), 2))

    return timeline


def _project_savings_trend(
    current_savings: float, income: float, expenses: float, months: int
) -> list[float]:
    """Project savings balance from `months` ago to now."""
    monthly_save = max(0.0, (income - expenses) * 0.3)
    data: list[float] = []
    for i in range(months):
        # i=0 is oldest month, i=months-1 is current
        past_offset = months - 1 - i
        data.append(round(max(0.0, current_savings - past_offset * monthly_save), 2))
    return data


# ── Behavior insights builder ──────────────────────────────────────────────────

def _build_behavior(
    spend_cats: dict[str, float],
    monthly_income: float,
    overdraft_prob: float,
    total_debt: float,
) -> dict:
    """
    Construct a BehaviorInsightsPayload-compatible dict from the calculated
    financial data. Matches the TypeScript interface exactly.
    """
    score = max(20, min(90, int(80 - overdraft_prob * 50)))
    band: str
    if score >= 65:
        band = "disciplined"
    elif score >= 45:
        band = "unstable"
    else:
        band = "risky"

    top_cats = sorted(spend_cats.items(), key=lambda x: x[1], reverse=True)[:3]

    # Spending by hour (derived from typical patterns — static shape)
    hour_amounts = [30, 85, 45, 125, 160, 90]
    if overdraft_prob > 0.6:
        hour_amounts = [25, 90, 50, 140, 190, 110]  # elevated evening spend

    # 7-day projected spend (scaled from income)
    daily_avg   = monthly_income / 30
    day_labels  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    proj_spend  = [
        round(daily_avg * m, 2)
        for m in [0.9, 0.85, 0.95, 1.0, 1.35, 1.45, 1.0]
    ]
    next7_total = round(sum(proj_spend), 2)

    debt_progress    = max(0.0, min(1.0, 1.0 - total_debt / max(monthly_income * 36, 1)))
    savings_progress = max(0.0, min(1.0, (spend_cats.get("Housing", monthly_income * 0.3)) / (monthly_income * 6)))

    has_high_risk = overdraft_prob > 0.65
    archetype_id  = "reactive_buyer" if has_high_risk else "builder"

    return {
        "score":    score,
        "scoreBand": band,
        "trend": {
            "direction": "up"   if overdraft_prob < 0.5 else "down",
            "text":      "Improving" if overdraft_prob < 0.5 else "Needs attention this week",
        },
        "aiSummary": (
            "Cash flow is tight — overdraft risk is elevated. "
            "Prioritise reducing daily discretionary spend and building a small buffer."
            if overdraft_prob > 0.6
            else "Finances look stable. Keep building savings momentum and chip away at debt."
        ),
        "patterns": {
            "timeOfDay": {
                "headline": "~40% more spend after 9PM" if overdraft_prob > 0.5 else "Spending is spread evenly across the day",
                "byHour": [
                    {"label": "8a",  "amount": hour_amounts[0]},
                    {"label": "12p", "amount": hour_amounts[1]},
                    {"label": "4p",  "amount": hour_amounts[2]},
                    {"label": "8p",  "amount": hour_amounts[3]},
                    {"label": "10p", "amount": hour_amounts[4]},
                    {"label": "12a", "amount": hour_amounts[5]},
                ],
            },
            "dayPattern": {
                "headline": "Peaks on Fri & Sat" if overdraft_prob > 0.5 else "Consistent weekday pattern",
                "detail":   "Dining and delivery cluster on those days." if overdraft_prob > 0.5 else "Weekend spend stays close to weekday average.",
            },
            "triggers": (
                ["Stress spending", "Post-paycheck splurge", "Late-night impulse buys"]
                if overdraft_prob > 0.6
                else ["Routine purchases", "Planned discretionary"]
            ),
            "categories": [
                {
                    "headline": f"{cat} is your #1 spending category",
                    "detail":   f"${amt:,.0f}/mo — {round(amt/max(monthly_income,1)*100,0):.0f}% of income.",
                }
                for cat, amt in top_cats[:2]
            ],
        },
        "risks": [
            {
                "id":          "overdraft",
                "title":       "Overdraft Risk",
                "body":        f"Balance may fall below zero within the month (prob: {overdraft_prob:.0%}).",
                "level":       "high"   if overdraft_prob > 0.65 else "medium" if overdraft_prob > 0.35 else "low",
                "probability": round(overdraft_prob, 2),
            },
            *(
                [{
                    "id":          "impulse",
                    "title":       "Elevated impulse-spend pattern",
                    "body":        "Multiple small unplanned charges detected — common with high-stress periods.",
                    "level":       "medium",
                    "probability": 0.62,
                }]
                if overdraft_prob > 0.5 else []
            ),
        ],
        "forecast": {
            "next7Spend":    next7_total,
            "changePct":     round((overdraft_prob - 0.4) * 30, 1),
            "labels":        day_labels,
            "projectedSpend": proj_spend,
            "alerts": (
                ["High overdraft risk — consider delaying non-essential purchases."]
                if overdraft_prob > 0.65 else
                (["Slightly elevated weekend spend expected."] if overdraft_prob > 0.4 else [])
            ),
            "aiMessage": (
                "At this trajectory your checking account may dip dangerously low before month-end. "
                "Moving $100–$200 of discretionary spend to after your next paycheck could prevent an overdraft."
                if overdraft_prob > 0.6
                else "Spending looks on-track. Staying consistent this week locks in your savings goal."
            ),
        },
        "recommendations": [
            {
                "id":          "buffer",
                "title":       "Build a 30-day cash buffer",
                "detail":      "Aim for 1 month of expenses in checking before investing.",
                "actionLabel": "Set auto-transfer",
            },
            {
                "id":          "debt-first",
                "title":       "Avalanche your highest-rate debt",
                "detail":      "Every extra dollar on the highest-APR balance saves the most interest.",
                "actionLabel": "See debt plan",
            },
            *(
                [{
                    "id":          "spending-guard",
                    "title":       "Enable spending guard for late nights",
                    "detail":      "A soft pause before charges after 9PM cuts impulse buys significantly.",
                    "actionLabel": "Turn on",
                }]
                if overdraft_prob > 0.5 else []
            ),
        ],
        "controlDefaults": {
            "spendingGuard":       overdraft_prob > 0.5,
            "impulseDelay":        overdraft_prob > 0.6,
            "categoryLimits": [
                {"category": cat, "max": round(amt * 1.05, 2)}
                for cat, amt in top_cats[:3]
            ],
            "dailyAlertThreshold": round(daily_avg * 1.5, 2),
        },
        "trends": {
            "weekLabels":    ["W1", "W2", "W3", "W4", "W5", "W6"],
            "scores":        _score_trend(score),
            "disciplineNote": (
                "Score slipping — cash flow pressure is rising."
                if overdraft_prob > 0.6
                else "Score holding steady — keep the momentum."
            ),
        },
        "goals": {
            "items": [
                {"name": "Debt payoff",        "aligned": total_debt < monthly_income * 6},
                {"name": "Emergency savings",  "aligned": spend_cats.get("Housing", 0) < monthly_income * 0.35},
            ],
            "debtProgress":         round(debt_progress, 2),
            "savingsProgress":      round(savings_progress, 2),
            "investmentReadiness":  round(max(0.0, 1.0 - overdraft_prob), 2),
        },
        "profile": {
            "archetypeId":  archetype_id,
            "title":        "Financial Survivor" if has_high_risk else "Wealth Builder",
            "emoji":        "🔴" if has_high_risk else "🟢",
            "description": (
                "Cash flow is your #1 challenge. Stability comes first — growth follows."
                if has_high_risk
                else "You're building good habits. Stay consistent and accelerate debt payoff."
            ),
            "strengths":   ["Aware of financial situation", "Tracking debts"],
            "weaknesses":  (["Cash flow management", "Impulse spending"] if has_high_risk else []),
        },
    }


def _score_trend(current_score: int) -> list[int]:
    """Generate a 6-week score trend ending at current_score."""
    import random
    random.seed(current_score)
    trend = [current_score]
    for _ in range(5):
        delta = random.randint(-4, 6)
        trend.append(max(20, min(90, trend[-1] - delta)))
    return list(reversed(trend))


# ── Market data endpoints ──────────────────────────────────────────────────────

DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META",
                   "VTI", "VOO", "SPY", "BND", "QQQ", "SCHD", "VXUS"]

# Simple in-memory quote cache (60-second TTL to avoid hammering Yahoo Finance)
_quote_cache: dict[str, dict] = {}
_quote_cache_ts: dict[str, float] = {}
_QUOTE_TTL = 60.0  # seconds


def _cached_quote(symbol: str) -> Optional[dict]:
    import time
    ts = _quote_cache_ts.get(symbol, 0)
    if time.time() - ts < _QUOTE_TTL and symbol in _quote_cache:
        return _quote_cache[symbol]
    return None


def _store_quote(symbol: str, data: dict) -> None:
    import time
    _quote_cache[symbol] = data
    _quote_cache_ts[symbol] = time.time()


@app.get("/api/market/quotes")
async def market_quotes(symbols: str = ",".join(DEFAULT_SYMBOLS)):
    """
    Batch real-time stock/ETF quotes.
    Query param: ?symbols=AAPL,MSFT,VTI,...
    """
    from tools.market_data import get_stock_quote  # noqa: PLC0415

    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()][:20]

    async def _fetch(sym: str) -> tuple[str, dict]:
        cached = _cached_quote(sym)
        if cached:
            return sym, cached
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, get_stock_quote, sym)
        if "error" not in result:
            _store_quote(sym, result)
        return sym, result

    results = await asyncio.gather(*[_fetch(s) for s in sym_list], return_exceptions=True)

    quotes: dict[str, dict] = {}
    for r in results:
        if isinstance(r, Exception):
            continue
        sym, data = r
        quotes[sym] = data

    return {"quotes": quotes, "timestamp": datetime.now().isoformat()}


@app.get("/api/market/history/{symbol}")
async def market_history(symbol: str, period: str = "1mo"):
    """
    Price history for a symbol — used to render the LineChart in the invest page.
    Returns { labels: [str], prices: [float], symbol: str, name: str }
    period: 1mo | 3mo | 6mo | 1y
    """
    allowed_periods = {"1mo", "3mo", "6mo", "1y"}
    if period not in allowed_periods:
        period = "1mo"

    try:
        import yfinance as yf  # noqa: PLC0415
        ticker = yf.Ticker(symbol.upper())

        loop = asyncio.get_running_loop()
        hist = await loop.run_in_executor(None, lambda: ticker.history(period=period))

        if hist.empty:
            return {"labels": [], "prices": [], "symbol": symbol.upper(), "name": symbol.upper()}

        # Format date labels based on period
        if period == "1mo":
            fmt = "%b %d"
        elif period in ("3mo", "6mo"):
            fmt = "%b %d"
        else:
            fmt = "%b '%y"

        labels = [d.strftime(fmt) for d in hist.index]
        prices = [round(float(v), 2) for v in hist["Close"].tolist()]

        # Get name from cached quote or info
        name = symbol.upper()
        cached = _cached_quote(symbol.upper())
        if cached:
            name = cached.get("name", symbol.upper())

        return {"labels": labels, "prices": prices, "symbol": symbol.upper(), "name": name}

    except Exception as exc:
        return {"error": str(exc), "labels": [], "prices": [], "symbol": symbol.upper(), "name": symbol.upper()}


@app.get("/api/market/overview")
async def market_overview():
    """
    Major market indices snapshot — used by the landing page ticker and invest page summary.
    Returns S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX.
    """
    from tools.market_data import get_market_overview  # noqa: PLC0415

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, get_market_overview)
    return result
