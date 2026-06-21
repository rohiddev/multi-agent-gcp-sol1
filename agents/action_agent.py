"""
Action / Workflow Agent
Executes actions against enterprise systems: creating tickets, retrieving
system records, invoking APIs, coordinating tool calls.
"""

from google.adk.agents import LlmAgent
from tools import get_ticket_status, create_ticket
from config import ACTION_MODEL

action_agent = LlmAgent(
    name="ActionAgent",
    model=ACTION_MODEL,
    description=(
        "Executes actions against enterprise systems. "
        "Can look up ticket status, create new tickets, retrieve system records, "
        "and coordinate multi-step workflows."
    ),
    instruction="""
        You are the enterprise Action and Workflow Agent.

        Your responsibilities:
        1. Execute the requested action using the available tools.
        2. Always confirm what action you are about to take before executing it.
        3. Report the result clearly — include IDs, states, and next steps.
        4. If an action fails, explain why and suggest alternatives.
        5. Never take destructive or irreversible actions without explicit user confirmation.

        Available actions: ticket lookup, ticket creation.
        For actions not covered by your tools, tell the user and suggest who can help.
    """,
    tools=[get_ticket_status, create_ticket],
)
