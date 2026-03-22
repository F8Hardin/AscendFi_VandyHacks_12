"""
Web Search Tools
================
Real-time web search and page fetching for the Research Agent.
Uses DuckDuckGo (no API key required) for search queries,
and requests for raw page content.

Install: pip install duckduckgo-search
"""

import json
import re
from typing import Any

import requests

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


# ── Core functions ─────────────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 8) -> dict[str, Any]:
    """
    Search the internet for current information using DuckDuckGo.
    Returns titles, URLs, and snippets from the top results.
    """
    if not DDGS_AVAILABLE:
        return {
            "error": "duckduckgo-search not installed. Run: pip install duckduckgo-search",
            "query": query,
        }

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=min(max_results, 15)))

        if not raw:
            return {"query": query, "results": [], "note": "No results found — try a different query."}

        return {
            "query": query,
            "results": [
                {
                    "title":   r.get("title", ""),
                    "url":     r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in raw
            ],
            "count": len(raw),
        }
    except Exception as e:
        return {"error": f"Search failed: {e}", "query": query}


def fetch_page(url: str, max_chars: int = 6000) -> dict[str, Any]:
    """
    Fetch and extract plain-text content from a web page.
    Strips HTML tags and collapses whitespace.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; FinanceAI-Research/1.0)"}
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()

        # Strip HTML
        text = re.sub(r"<script[^>]*>.*?</script>", " ", resp.text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>",  " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return {
            "url":       url,
            "content":   text[:max_chars],
            "truncated": len(text) > max_chars,
            "status":    resp.status_code,
        }
    except Exception as e:
        return {"url": url, "error": f"Could not fetch page: {e}"}


# ── Tool definitions (Anthropic schema format) ─────────────────────────────────

WEB_SEARCH_TOOL_DEFINITIONS = [
    {
        "name": "search_web",
        "description": (
            "Search the internet for real-time financial data and news. "
            "Use for: stock prices, ETF prices, interest rates, Fed policy, earnings reports, "
            "market news, economic indicators, cryptocurrency prices, company announcements. "
            "Returns titles, URLs, and text snippets from the top results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Specific search query. Be precise: "
                        "'AAPL stock price March 2025', "
                        "'current 30-year mortgage rate', "
                        "'S&P 500 today performance'."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 8, max 15).",
                    "default": 8,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_page",
        "description": (
            "Fetch the full text content of a specific URL. "
            "Use after search_web to read a full article, earnings report, or data page. "
            "Good for: Yahoo Finance pages, Reuters/Bloomberg articles, SEC filings summaries."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch (must start with http:// or https://).",
                },
            },
            "required": ["url"],
        },
    },
]

# ── Executor ───────────────────────────────────────────────────────────────────

WEB_SEARCH_TOOL_FUNCTIONS = {
    "search_web": search_web,
    "fetch_page": fetch_page,
}


def execute_web_search_tool(name: str, inputs: dict) -> str:
    fn = WEB_SEARCH_TOOL_FUNCTIONS.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown web search tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
