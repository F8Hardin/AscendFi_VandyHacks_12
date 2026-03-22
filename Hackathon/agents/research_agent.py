"""
Research Agent — Live Web Intelligence Officer.

Sole purpose: search the internet using Gemini's native Google Search grounding
and return accurate, up-to-date financial data.

Uses the google.genai SDK directly (not the OpenAI-compatible layer) so that
Google Search grounding works natively — no extra API key required.

Results are published to the AgentBus so every specialist agent (Risk, Debt,
Behaviour, Investment, Wealth) receives them automatically via peer-context
injection before they generate their own analysis.
"""

import warnings
from config import GEMINI_API_KEY, RESEARCH_AGENT_MODEL
from agents.agent_bus import bus

# Suppress deprecation noise from google libraries
warnings.filterwarnings("ignore", category=FutureWarning, module="google")

import google.genai as genai
from google.genai import types


RESEARCH_SYSTEM_PROMPT = """You are a Financial Research Specialist — a real-time web intelligence agent.

Your ONLY job is to search the internet (via Google Search) and retrieve accurate,
current financial data for the specialist agents who will use your findings.

When given a research request:
1. Search for each piece of data needed — be specific and targeted.
2. Always find exact numbers, not estimates.
3. Always include the source and how fresh the data is.

ALWAYS include in your response:
- Exact numbers and prices (never round or estimate unless the source does)
- The source name / URL for every data point
- The date or freshness of the information
- A clear "NOT FOUND" if you could not locate something

Do NOT make up, estimate, or extrapolate data. If a search fails, say so clearly.
Do NOT give financial advice — only facts and data.

End every response with this clearly labelled block:

━━━━━━━━━━━━━━━━━━━━━━━━━━
RESEARCH FINDINGS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━
[Data point]: [Exact value] — Source: [name/URL]
[Data point]: [Exact value] — Source: [name/URL]
Data freshness: [date/time if known]
━━━━━━━━━━━━━━━━━━━━━━━━━━

This block is what the other specialist agents will read.
"""


class ResearchAgent:
    """
    Gemini-native research agent with Google Search grounding.
    Publishes findings to AgentBus after every run so peer agents
    can incorporate fresh data into their own responses.
    """

    def __init__(self):
        self.name = "Research Agent"
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = RESEARCH_AGENT_MODEL

    def run(self, user_message: str, stream_callback=None) -> str:
        """
        Run a research query with Google Search grounding enabled.
        Streams output via stream_callback if provided.
        Returns the full text response.
        """
        # Inject any existing peer context (findings from other agents this turn)
        peer_context = bus.get_peer_context_block(self.name)
        enriched = f"{user_message}\n\n{peer_context}" if peer_context else user_message

        config = types.GenerateContentConfig(
            system_instruction=RESEARCH_SYSTEM_PROMPT,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )

        full_response = ""

        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=enriched,
                config=config,
            ):
                if chunk.text:
                    full_response += chunk.text
                    if stream_callback:
                        stream_callback(chunk.text)
        except Exception as e:
            error_msg = f"[Research Agent error: {e}]"
            if stream_callback:
                stream_callback(error_msg)
            return error_msg

        # Publish findings to bus so all specialist agents receive them
        if full_response:
            summary = full_response.strip()[:500]
            bus.publish(
                sender=self.name,
                topic="web_research_findings",
                data=full_response[:3000],
                summary=summary,
            )

        return full_response


def create_research_agent() -> ResearchAgent:
    return ResearchAgent()
