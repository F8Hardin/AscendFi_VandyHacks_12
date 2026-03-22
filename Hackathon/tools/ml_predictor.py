"""
ML Prediction Engine
====================
Machine learning models trained on Yahoo Finance historical data.
Shared by all specialist agents for:
  - Technical indicator analysis (RSI, MACD, Bollinger Bands)
  - Market trend prediction  (RandomForest classifier on 2y OHLCV data)
  - Stock momentum scoring   (composite multi-timeframe signal)
  - Portfolio volatility     (correlation-adjusted risk + beta + Sharpe)

No external TA library needed — all indicators computed from scratch.
Requires: yfinance, scikit-learn, pandas, numpy
"""

import json
from typing import Any

import numpy as np

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


# ─── Internal indicator helpers ───────────────────────────────────────────────

def _rsi(prices: "pd.Series", period: int = 14) -> "pd.Series":
    delta = prices.diff()
    gains = delta.clip(lower=0).rolling(window=period).mean()
    losses = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gains / losses.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _macd(prices: "pd.Series", fast=12, slow=26, signal=9):
    """Returns (macd_line, signal_line, histogram)."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line, macd_line - signal_line


def _bollinger(prices: "pd.Series", period=20, std_dev=2):
    """Returns (upper, mid, lower, band_position 0-1)."""
    mid = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    pos = (prices - lower) / (upper - lower).replace(0, np.nan)
    return upper, mid, lower, pos


def _feature_matrix(df: "pd.DataFrame") -> "pd.DataFrame":
    """Build ML feature matrix from OHLCV data."""
    close  = df["Close"]
    volume = df["Volume"]

    feats = pd.DataFrame(index=df.index)

    # Price momentum (%)
    for n in (5, 10, 20):
        feats[f"mom_{n}d"] = (close / close.shift(n) - 1) * 100

    # RSI
    feats["rsi_14"] = _rsi(close, 14)
    feats["rsi_7"]  = _rsi(close, 7)

    # MACD histogram + line
    macd_l, sig_l, hist = _macd(close)
    feats["macd_hist"] = hist
    feats["macd_line"] = macd_l

    # Bollinger band position (0 = at lower, 1 = at upper)
    _, _, _, bb_pos = _bollinger(close)
    feats["bb_position"] = bb_pos

    # MA ratio: 20d vs 50d
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    feats["ma_ratio_20_50"] = (ma20 / ma50 - 1) * 100

    # Volume relative strength
    feats["volume_ratio"] = volume / volume.rolling(20).mean()

    # Daily range + rolling volatility
    feats["daily_range_pct"] = (df["High"] - df["Low"]) / close * 100
    feats["vol_20d"] = close.pct_change().rolling(20).std() * 100

    return feats.dropna()


# ─── Public tool functions ─────────────────────────────────────────────────────

def get_technical_indicators(symbol: str) -> dict[str, Any]:
    """
    Compute technical analysis indicators for any stock or ETF using
    6 months of Yahoo Finance daily data. Returns RSI, MACD, Bollinger Bands,
    moving averages, volume analysis, 52-week range position, and an overall
    technical bias (BULLISH / BEARISH / MIXED).
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}
    if not PANDAS_AVAILABLE:
        return {"error": "pandas not installed. Run: pip install pandas"}

    try:
        df = yf.Ticker(symbol.upper()).history(period="6mo", interval="1d")
        if df.empty or len(df) < 30:
            return {"error": f"Insufficient data for {symbol}. Need ≥30 days."}

        close = df["Close"]
        volume = df["Volume"]
        price = float(close.iloc[-1])

        # RSI
        rsi_val = float(_rsi(close, 14).iloc[-1])
        rsi_signal = (
            "oversold (potential bounce)" if rsi_val < 30
            else "overbought (potential pullback)" if rsi_val > 70
            else "neutral"
        )

        # MACD
        macd_l, sig_l, hist = _macd(close)
        macd_v = float(macd_l.iloc[-1])
        sig_v  = float(sig_l.iloc[-1])
        hist_v = float(hist.iloc[-1])

        # Bollinger
        upper, mid, lower, bb_pos = _bollinger(close)
        bb_p = float(bb_pos.iloc[-1])
        bb_signal = (
            "near_lower_band (oversold, potential reversal up)" if bb_p < 0.2
            else "near_upper_band (overbought, potential reversal down)" if bb_p > 0.8
            else "mid_band (neutral)"
        )

        # Moving averages
        ma20  = float(close.rolling(20).mean().iloc[-1])
        ma50  = float(close.rolling(50).mean().iloc[-1])  if len(close) >= 50  else None
        ma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

        cross = None
        if ma50 and ma200:
            cross = "golden_cross (bullish)" if ma50 > ma200 else "death_cross (bearish)"

        # Volume
        avg_vol = float(volume.rolling(20).mean().iloc[-1])
        vol_ratio = float(volume.iloc[-1]) / avg_vol if avg_vol > 0 else 1.0

        # 52-week range
        h52 = float(close.tail(252).max()) if len(close) >= 252 else float(close.max())
        l52 = float(close.tail(252).min()) if len(close) >= 252 else float(close.min())
        range_pos = (price - l52) / (h52 - l52) * 100 if h52 > l52 else 50.0

        # Count bullish signals
        bullish = sum([
            rsi_val > 50,
            macd_v > sig_v,
            hist_v > 0,
            bb_p > 0.5,
            bool(ma50 and ma200 and ma50 > ma200),
            vol_ratio > 1.0,
        ])
        bias = (
            "BULLISH"      if bullish >= 4
            else "BEARISH" if bullish <= 2
            else "MIXED/NEUTRAL"
        )

        return {
            "symbol": symbol.upper(),
            "current_price": round(price, 2),
            "overall_technical_bias": bias,
            "rsi": {
                "value": round(rsi_val, 1),
                "signal": rsi_signal,
            },
            "macd": {
                "macd_line": round(macd_v, 4),
                "signal_line": round(sig_v, 4),
                "histogram": round(hist_v, 4),
                "direction": "bullish" if macd_v > sig_v else "bearish",
            },
            "bollinger_bands": {
                "upper": round(float(upper.iloc[-1]), 2),
                "middle": round(float(mid.iloc[-1]), 2),
                "lower": round(float(lower.iloc[-1]), 2),
                "position_pct": round(bb_p * 100, 1),
                "signal": bb_signal,
            },
            "moving_averages": {
                "ma_20d": round(ma20, 2),
                "ma_50d": round(ma50, 2) if ma50 else None,
                "ma_200d": round(ma200, 2) if ma200 else None,
                "price_above_ma20": price > ma20,
                "price_above_ma50": price > ma50 if ma50 else None,
                "cross_signal": cross,
            },
            "volume": {
                "ratio_vs_20d_avg": round(vol_ratio, 2),
                "signal": (
                    "high_volume_confirmation" if vol_ratio > 1.5
                    else "low_volume_caution" if vol_ratio < 0.5
                    else "average_volume"
                ),
            },
            "year_range": {
                "52w_high": round(h52, 2),
                "52w_low": round(l52, 2),
                "position_in_range_pct": round(range_pos, 1),
            },
        }

    except Exception as e:
        return {"error": f"Technical indicator computation failed for {symbol}: {e}"}


def predict_market_trend(symbol: str, horizon_days: int = 5) -> dict[str, Any]:
    """
    Train a RandomForest classifier on 2 years of Yahoo Finance OHLCV data,
    then predict the trend direction for the given symbol over the next
    horizon_days trading days. Returns prediction (BULLISH/BEARISH/NEUTRAL),
    confidence, model test accuracy, and top signal drivers.
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}
    if not SKLEARN_AVAILABLE:
        return {"error": "scikit-learn not installed. Run: pip install scikit-learn"}
    if not PANDAS_AVAILABLE:
        return {"error": "pandas not installed. Run: pip install pandas"}

    horizon_days = min(max(int(horizon_days), 3), 20)

    try:
        df = yf.Ticker(symbol.upper()).history(period="2y", interval="1d")
        if df.empty or len(df) < 120:
            return {"error": f"Insufficient data for {symbol}. Need ≥120 trading days."}

        feats = _feature_matrix(df)
        close = df["Close"].reindex(feats.index)

        # Label: +1 if price up >1% in horizon, -1 if down >1%, else 0
        future_ret = close.shift(-horizon_days) / close - 1
        labels = future_ret.map(lambda r: 1 if r > 0.01 else (-1 if r < -0.01 else 0))

        valid = feats.index.intersection(labels.dropna().index)
        X = feats.loc[valid].values
        y = labels.loc[valid].values

        if len(X) < 60:
            return {"error": f"Not enough aligned data to train model for {symbol}."}

        split = int(len(X) * 0.80)
        X_tr, X_te = X[:split], X[split:]
        y_tr, y_te = y[:split], y[split:]

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_tr_s, y_tr)
        test_acc = float(accuracy_score(y_te, model.predict(X_te_s)))

        # Predict on most recent row
        X_cur = scaler.transform(feats.iloc[-1:].values)
        pred  = int(model.predict(X_cur)[0])
        proba = model.predict_proba(X_cur)[0]
        prob_map = {int(c): float(p) for c, p in zip(model.classes_, proba)}

        direction  = {1: "BULLISH", -1: "BEARISH", 0: "NEUTRAL"}.get(pred, "NEUTRAL")
        confidence = prob_map.get(pred, 0.33)
        conf_label = "high" if confidence > 0.60 else "moderate" if confidence > 0.45 else "low"

        # Top feature importances
        top_features = sorted(
            zip(feats.columns, model.feature_importances_),
            key=lambda x: x[1], reverse=True,
        )[:5]

        recent_5d  = float((close.iloc[-1] / close.iloc[-6]  - 1) * 100) if len(close) >= 6  else None
        recent_20d = float((close.iloc[-1] / close.iloc[-21] - 1) * 100) if len(close) >= 21 else None

        return {
            "symbol": symbol.upper(),
            "horizon": f"{horizon_days} trading days",
            "ml_prediction": direction,
            "confidence": round(confidence, 3),
            "confidence_label": conf_label,
            "probabilities": {
                "bullish":  round(prob_map.get(1,  0.0), 3),
                "neutral":  round(prob_map.get(0,  0.0), 3),
                "bearish":  round(prob_map.get(-1, 0.0), 3),
            },
            "model_test_accuracy": round(test_acc, 3),
            "top_signal_drivers": [
                {"feature": f, "importance": round(imp, 3)} for f, imp in top_features
            ],
            "recent_actual_performance": {
                "5d_return_pct":  round(recent_5d,  2) if recent_5d  is not None else None,
                "20d_return_pct": round(recent_20d, 2) if recent_20d is not None else None,
            },
            "disclaimer": "ML model trained on historical price patterns. Not financial advice.",
        }

    except Exception as e:
        return {"error": f"ML trend prediction failed for {symbol}: {e}"}


def predict_stock_momentum(symbol: str) -> dict[str, Any]:
    """
    Compute a composite momentum score from -100 (strong downtrend) to +100
    (strong uptrend). Combines 5/10/20/60/90-day price returns, RSI, MACD,
    and moving average alignment. Returns score, signal (BUY/ACCUMULATE/
    HOLD/REDUCE/SELL), and multi-timeframe return breakdown.
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}
    if not PANDAS_AVAILABLE:
        return {"error": "pandas not installed. Run: pip install pandas"}

    try:
        df = yf.Ticker(symbol.upper()).history(period="1y", interval="1d")
        if df.empty or len(df) < 20:
            return {"error": f"Insufficient data for {symbol}."}

        close = df["Close"]

        def mom(n):
            if len(close) < n + 1:
                return None
            return float((close.iloc[-1] / close.iloc[-(n + 1)] - 1) * 100)

        m5, m10, m20 = mom(5), mom(10), mom(20)
        m60 = mom(60) if len(close) >= 61 else None
        m90 = mom(90) if len(close) >= 91 else None

        rsi_val = float(_rsi(close, 14).iloc[-1])
        _, _, hist = _macd(close)
        macd_h = float(hist.iloc[-1])

        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
        price = float(close.iloc[-1])

        # Build composite score
        score = (rsi_val - 50) * 0.6  # RSI centred at 50

        if m5  is not None: score += min(max(m5  * 4,   -20), 20)
        if m10 is not None: score += min(max(m10 * 2,   -20), 20)
        if m20 is not None: score += min(max(m20 * 1.5, -15), 15)
        if m60 is not None: score += min(max(m60 * 0.5, -10), 10)

        score += 5  if price > ma20           else -5
        score += 5  if (ma50 and price > ma50) else -5
        score += 5  if macd_h > 0             else -5

        score = min(max(score, -100), 100)

        signal = (
            "BUY"       if score >= 40
            else "ACCUMULATE"  if score >= 15
            else "SELL/AVOID"  if score <= -40
            else "REDUCE"      if score <= -15
            else "HOLD/WAIT"
        )
        signal_desc = {
            "BUY":        "Strong positive momentum across timeframes",
            "ACCUMULATE": "Positive momentum building — consider adding",
            "HOLD/WAIT":  "Mixed signals — no clear directional edge",
            "REDUCE":     "Negative momentum developing — consider trimming",
            "SELL/AVOID": "Strong negative momentum — avoid or exit",
        }[signal]

        strength = (
            "STRONG"   if abs(score) >= 50
            else "MODERATE" if abs(score) >= 25
            else "WEAK"
        )

        return {
            "symbol": symbol.upper(),
            "momentum_score": round(score, 1),
            "momentum_strength": strength,
            "signal": signal,
            "signal_description": signal_desc,
            "multi_timeframe_returns": {
                "5d_pct":  round(m5,  2) if m5  is not None else None,
                "10d_pct": round(m10, 2) if m10 is not None else None,
                "20d_pct": round(m20, 2) if m20 is not None else None,
                "60d_pct": round(m60, 2) if m60 is not None else None,
                "90d_pct": round(m90, 2) if m90 is not None else None,
            },
            "supporting_indicators": {
                "rsi_14":         round(rsi_val, 1),
                "above_20d_ma":   price > ma20,
                "above_50d_ma":   price > ma50 if ma50 else None,
                "macd_histogram": round(macd_h, 4),
                "macd_direction": "positive" if macd_h > 0 else "negative",
            },
        }

    except Exception as e:
        return {"error": f"Momentum calculation failed for {symbol}: {e}"}


def predict_portfolio_volatility(
    symbols: list[str],
    weights: list[float],
) -> dict[str, Any]:
    """
    Estimate annualised portfolio volatility, beta vs S&P 500, Sharpe ratio,
    and pairwise correlations for a list of holdings. Uses 1 year of Yahoo
    Finance daily returns. Weights are automatically normalised.
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}
    if not PANDAS_AVAILABLE:
        return {"error": "pandas not installed. Run: pip install pandas"}
    if len(symbols) != len(weights):
        return {"error": "symbols and weights must have equal length."}

    total_w = sum(weights)
    if total_w <= 0:
        return {"error": "Weights must sum to a positive number."}
    w_norm = [w / total_w for w in weights]

    try:
        # Fetch prices (include SPY for benchmark)
        all_syms = [s.upper() for s in symbols] + ["SPY"]
        prices: dict[str, Any] = {}
        for sym in all_syms:
            hist = yf.Ticker(sym).history(period="1y", interval="1d")
            if not hist.empty:
                prices[sym] = hist["Close"]

        if not prices:
            return {"error": "No price data retrieved."}

        price_df = pd.DataFrame(prices).dropna()
        rets = price_df.pct_change().dropna()

        avail  = [s.upper() for s in symbols if s.upper() in rets.columns]
        aw     = [w_norm[i] for i, s in enumerate(symbols) if s.upper() in rets.columns]
        aw_sum = sum(aw)
        aw     = [w / aw_sum for w in aw]

        port_daily = sum(rets[s] * w for s, w in zip(avail, aw))
        ann_vol    = float(port_daily.std() * np.sqrt(252) * 100)
        ann_ret    = float(port_daily.mean() * 252 * 100)
        risk_free  = 5.0
        sharpe     = round((ann_ret - risk_free) / ann_vol, 3) if ann_vol > 0 else None

        # Benchmark
        spy_vol, spy_ret, beta = None, None, None
        if "SPY" in rets.columns:
            spy_d   = rets["SPY"]
            spy_vol = float(spy_d.std() * np.sqrt(252) * 100)
            spy_ret = float(spy_d.mean() * 252 * 100)
            spy_var = float(spy_d.var() * 252)
            cov     = float(port_daily.cov(spy_d) * 252)
            beta    = round(cov / spy_var, 3) if spy_var > 0 else None

        # Individual vols
        ind_vols = {
            s: round(float(rets[s].std() * np.sqrt(252) * 100), 2)
            for s in avail if s in rets.columns
        }

        # Pairwise correlations
        corr_df = rets[avail].corr()
        corrs = {
            f"{s1}-{s2}": round(float(corr_df.loc[s1, s2]), 3)
            for i, s1 in enumerate(avail)
            for j, s2 in enumerate(avail)
            if i < j
        }

        risk_class = (
            "LOW (conservative, bond-like)"     if ann_vol < 8
            else "MODERATE (balanced portfolio)" if ann_vol < 15
            else "HIGH (equity-heavy)"           if ann_vol < 22
            else "VERY HIGH (aggressive/concentrated)"
        )

        return {
            "portfolio": {
                "symbols":      avail,
                "weights_pct":  [round(w * 100, 1) for w in aw],
            },
            "risk_metrics": {
                "annualized_volatility_pct":   round(ann_vol, 2),
                "risk_classification":         risk_class,
                "beta_vs_sp500":               beta,
                "estimated_1yr_return_pct":    round(ann_ret, 2),
                "sharpe_ratio_estimate":       sharpe,
            },
            "benchmark_spy": {
                "spy_annualized_vol_pct":   round(spy_vol, 2) if spy_vol else None,
                "spy_1yr_return_pct":       round(spy_ret, 2) if spy_ret else None,
                "portfolio_vs_spy_vol":     f"{round(ann_vol - spy_vol, 2):+.2f}% vs SPY" if spy_vol else None,
            },
            "individual_volatilities_pct": ind_vols,
            "pairwise_correlations":       corrs,
            "diversification_note": (
                "Low correlations reduce portfolio risk. Negative correlations = best hedge."
            ),
        }

    except Exception as e:
        return {"error": f"Portfolio volatility calculation failed: {e}"}


# ─── Tool Definitions (JSON Schema for Claude) ────────────────────────────────

ML_PREDICTOR_TOOL_DEFINITIONS = [
    {
        "name": "get_technical_indicators",
        "description": (
            "Compute technical analysis indicators for any stock or ETF using 6 months of "
            "Yahoo Finance daily data. Returns RSI (overbought/oversold), MACD (momentum), "
            "Bollinger Bands (price extremes), moving averages (20/50/200d), volume signals, "
            "52-week range position, and overall technical bias (BULLISH/BEARISH/MIXED). "
            "Use before any investment recommendation or risk assessment of a holding."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol e.g. 'AAPL', 'SPY', '^GSPC'",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "predict_market_trend",
        "description": (
            "Train a RandomForest ML model on 2 years of Yahoo Finance OHLCV data and "
            "predict the trend direction (BULLISH/BEARISH/NEUTRAL) for a stock or ETF "
            "over the next N trading days. Returns confidence score, model test accuracy, "
            "and the top signal drivers (feature importances). "
            "horizon_days: 5 (1 week), 10 (2 weeks), 20 (1 month). "
            "Use for investment timing, risk assessment, and sector trend analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol to predict trend for",
                },
                "horizon_days": {
                    "type": "integer",
                    "description": "Forecast horizon in trading days: 5, 10, or 20",
                    "default": 5,
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "predict_stock_momentum",
        "description": (
            "Calculate a composite momentum score from -100 (strong downtrend) to +100 "
            "(strong uptrend) for a stock or ETF using 5/10/20/60/90-day returns plus "
            "RSI and MACD signals. Returns momentum score, signal (BUY/ACCUMULATE/"
            "HOLD/REDUCE/SELL), and multi-timeframe breakdown. "
            "Use for ranking stocks, timing entries/exits, and identifying reversals."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol e.g. 'AAPL', 'VTI', 'QQQ'",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "predict_portfolio_volatility",
        "description": (
            "Estimate annualised portfolio volatility, beta vs S&P 500, Sharpe ratio, and "
            "pairwise correlations for a multi-asset portfolio. Input symbols with weights; "
            "weights are normalised automatically. Returns risk classification, diversification "
            "analysis, and SPY benchmark comparison. "
            "Use for portfolio risk assessment, rebalancing decisions, and suitability analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols e.g. ['VTI', 'BND', 'GLD']",
                },
                "weights": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Portfolio weights (normalised). E.g. [60, 30, 10] for 60/30/10",
                },
            },
            "required": ["symbols", "weights"],
        },
    },
]

# ─── Tool executor ────────────────────────────────────────────────────────────

ML_TOOL_FUNCTIONS = {
    "get_technical_indicators":   get_technical_indicators,
    "predict_market_trend":       predict_market_trend,
    "predict_stock_momentum":     predict_stock_momentum,
    "predict_portfolio_volatility": predict_portfolio_volatility,
}


def execute_ml_tool(name: str, inputs: dict) -> str:
    fn = ML_TOOL_FUNCTIONS.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown ML tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
