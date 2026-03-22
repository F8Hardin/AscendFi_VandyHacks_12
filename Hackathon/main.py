#!/usr/bin/env python3
"""
FinanceAI — Multi-Agent Financial Intelligence System
=====================================================
Supervisor agent (Gemini) backed by 5 specialized financial agents:
  Risk & Investment → Claude Sonnet | Debt → GPT-4o mini
  Behaviour → Gemini | Wealth → Qwen-Plus

Features:
  • Mandatory delegation — ARIA always consults specialist agents before replying
  • Persistent memory   — conversation history saved to ~/.financeai/ across sessions

Usage:
    python main.py              → Interactive chat mode
    python main.py --demo       → Run a built-in demo scenario

In-session commands:
    history   → Show last 5 things you asked ARIA
    reset     → Clear all memory and start fresh
    demo      → Run a demo scenario
    quit      → Exit
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.table import Table
from rich import print as rprint

from agents.supervisor import SupervisorAgent

console = Console()


def print_banner(supervisor: SupervisorAgent):
    memory_line = supervisor.memory_summary
    memory_style = "dim green" if "prior" in memory_line else "dim"

    console.print()
    console.print(Panel(
        "[bold green]ARIA[/bold green] — Advanced Risk & Investment Advisor\n"
        "[dim]Powered by 5 specialized AI agents | Gemini · Claude · GPT-4o · Qwen[/dim]\n\n"
        "  [red]🔴 Risk Agent[/red]       Credit · Overdraft · Payment Risk\n"
        "  [yellow]🟠 Debt Agent[/yellow]       Payoff Plans · Consolidation\n"
        "  [yellow]🟡 Behaviour Agent[/yellow]  Spending Habits · Pattern Analysis\n"
        "  [green]🟢 Investment Agent[/green]  Simulations · Portfolio Allocation\n"
        "  [blue]🔵 Wealth Agent[/blue]     Budgeting · Net Worth · Strategy\n\n"
        f"[{memory_style}]💾 Memory: {memory_line}[/{memory_style}]\n\n"
        "[dim]Commands: [bold]quit[/bold] · [bold]reset[/bold] · [bold]history[/bold] · [bold]demo[/bold][/dim]",
        title="[bold]💰 FinanceAI[/bold]",
        border_style="green",
    ))
    console.print()


DEMO_SCENARIOS = [
    {
        "label": "Full Financial Check-Up",
        "message": (
            "I need a complete financial health assessment. Here's my situation:\n"
            "- Monthly take-home: $5,200\n"
            "- Monthly expenses: $4,800 (rent $1,600, utilities $200, groceries $400, subscriptions $150, other $2,450)\n"
            "- Average daily checking balance: $340\n"
            "- Credit score: 648, utilization 72%, 1 missed payment last month\n"
            "- Debts: Visa card $4,200 at 24.99% APR (min $105), Capital One $2,800 at 19.99% APR (min $70), "
            "Student loan $18,500 at 5.8% (min $210)\n"
            "- Savings: $800 emergency fund, no investments, 401k: 0% contribution\n"
            "- Age: 31\n\n"
            "What should I do first? I'm overwhelmed."
        ),
    },
    {
        "label": "Investment Simulation",
        "message": (
            "I just got a raise and I'm ready to start investing seriously. I'm 28 years old, "
            "moderate risk tolerance, and can invest $500/month. I have $3,000 to start with "
            "and a 6-month emergency fund. I want to retire at 60. "
            "Can you run some simulations showing me what I might have at retirement? "
            "Show me pessimistic, realistic, and optimistic scenarios. "
            "Also tell me how to allocate my portfolio."
        ),
    },
    {
        "label": "Debt Freedom Plan",
        "message": (
            "I want to get out of debt. Here are all my debts:\n"
            "- American Express: $8,500 balance, 26.99% APR, $170 minimum\n"
            "- Chase Sapphire: $3,200 balance, 21.49% APR, $80 minimum\n"
            "- Car loan: $12,400 balance, 7.9% APR, $290 minimum\n"
            "- Personal loan: $5,000 balance, 14.5% APR, $130 minimum\n\n"
            "I can put an extra $400/month toward debt. Should I use avalanche or snowball? "
            "Would consolidation help? Give me a complete plan."
        ),
    },
]


def run_demo(supervisor: SupervisorAgent):
    console.print(Rule("[bold yellow]DEMO MODE[/bold yellow]"))
    console.print()

    for i, scenario in enumerate(DEMO_SCENARIOS, 1):
        console.print(f"  [bold]{i}.[/bold] {scenario['label']}")

    console.print()
    choice = console.input("[bold yellow]Choose a demo (1-3) or press Enter for #1:[/bold yellow] ").strip()

    idx = int(choice) - 1 if choice.isdigit() and 1 <= int(choice) <= 3 else 0
    scenario = DEMO_SCENARIOS[idx]

    console.print()
    console.print(Rule(f"[bold]{scenario['label']}[/bold]"))
    console.print(Panel(scenario["message"], title="[bold cyan]Your Question[/bold cyan]", border_style="cyan"))
    console.print()
    console.print("[bold green]ARIA:[/bold green]", end=" ")

    supervisor.chat(scenario["message"], stream_callback=lambda t: print(t, end="", flush=True))
    print()


def show_history(supervisor: SupervisorAgent):
    """Display the last 5 user questions from persistent memory."""
    recent = supervisor.memory.get_recent_user_messages(n=5)
    if not recent:
        console.print("[dim]No conversation history yet.[/dim]\n")
        return

    console.print()
    console.print(Rule("[bold]Recent Conversation History[/bold]"))
    for i, msg in enumerate(recent, 1):
        ts = msg.get("timestamp", "")[:16].replace("T", " ")
        content = msg["content"]
        # Trim long messages for display
        preview = content[:120] + "..." if len(content) > 120 else content
        console.print(f"  [bold cyan]{i}.[/bold cyan] [dim]{ts}[/dim]")
        console.print(f"     {preview}")
        console.print()


def interactive_mode(supervisor: SupervisorAgent):
    console.print(
        "[dim]Share your financial situation, questions, or data. "
        "ARIA will consult her specialist team before responding.[/dim]"
    )
    console.print()

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[dim]Session ended. Good luck with your finances![/dim]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("quit", "exit", "q"):
            console.print("[dim]Session ended. Good luck with your finances![/dim]")
            break

        if cmd in ("reset", "new"):
            supervisor.reset_conversation()
            console.print("[dim]Memory cleared. Starting fresh![/dim]\n")
            continue

        if cmd == "history":
            show_history(supervisor)
            continue

        if cmd == "demo":
            run_demo(supervisor)
            continue

        console.print()
        console.print("[bold green]ARIA:[/bold green] ", end="")

        try:
            supervisor.chat(user_input, stream_callback=lambda t: print(t, end="", flush=True))
        except KeyboardInterrupt:
            console.print("\n[dim](interrupted)[/dim]")
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")

        print("\n")


def main():
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[bold red]Error:[/bold red] ANTHROPIC_API_KEY environment variable not set.")
        console.print("Copy [bold].env.example[/bold] to [bold].env[/bold] and add your key.")
        sys.exit(1)

    supervisor = SupervisorAgent()
    print_banner(supervisor)

    if "--demo" in sys.argv:
        run_demo(supervisor)
    else:
        interactive_mode(supervisor)


if __name__ == "__main__":
    main()
