import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic (Supervisor + Risk + Investment agents)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "gemini-3.1-pro-preview"           # Supervisor
RISK_AGENT_MODEL = "gemini-3.1-pro-preview"       # Risk Agent
INVESTMENT_AGENT_MODEL = "gemini-3.1-pro-preview" # Investment Agent
MAX_TOKENS = 16000
STREAM_MAX_TOKENS = 64000

# Google Gemini (Supervisor + Behaviour Agent + Wealth Agent)
# Dashboard: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
SUPERVISOR_MODEL = "gemini-3.1-pro-preview"       # Supervisor (ARIA)
BEHAVIOUR_AGENT_MODEL = "gemini-3.1-pro-preview"  # Behaviour Agent
WEALTH_AGENT_MODEL = "gemini-3.1-pro-preview"     # Wealth Agent
RESEARCH_AGENT_MODEL = "gemini-3.1-pro-preview"         # Research Agent (fast web search)

# OpenAI (Debt Agent)
# Dashboard: https://platform.openai.com/api-keys
OPENAI_API_KEY = os.getenv("OPEN_API_KEY", "")
DEBT_AGENT_MODEL = "gpt-4o-mini"

# Capital One DevExchange API
# Register at https://developer.capitalone.com
CAPITAL_ONE_API_KEY  = os.getenv("CAPITAL_ONE_API_KEY", "")
CAPITAL_ONE_BASE_URL = os.getenv("CAPITAL_ONE_BASE_URL", "https://api.capitalone.com")
