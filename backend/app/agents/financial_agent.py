import os
import anthropic

SYSTEM_PROMPT = """You are a compassionate and knowledgeable financial recovery advisor.
Your role is to help users who are facing financial hardship by:
- Assessing their current financial situation
- Identifying immediate relief options (debt relief, assistance programs, etc.)
- Creating actionable recovery plans
- Providing emotional support alongside practical advice
- Explaining financial concepts in plain language

Always be empathetic, non-judgmental, and practical. Prioritize the user's well-being and
financial stability. When appropriate, recommend seeking professional financial or legal advice."""

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def stream_financial_advice(messages: list[dict]):
    """Stream responses from Claude for financial recovery guidance."""
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
