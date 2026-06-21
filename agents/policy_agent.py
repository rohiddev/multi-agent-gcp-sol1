"""
Policy / Risk Agent
Checks whether a request is allowed, whether sensitive data is involved,
and whether the workflow should proceed or require approval.
"""

from google.adk.agents import LlmAgent
from tools import check_policy
from config import POLICY_MODEL

policy_agent = LlmAgent(
    name="PolicyAgent",
    model=POLICY_MODEL,
    description=(
        "Evaluates requests against enterprise policy. "
        "Determines whether an action is permitted, flags sensitive data, "
        "and decides if human approval is required before proceeding."
    ),
    instruction="""
        You are the enterprise Policy and Risk Agent.

        Your responsibilities:
        1. Use check_policy to verify the requested action is permitted for the user's role.
        2. Flag any sensitive data categories (PII, financial, health, confidential).
        3. If the action is NOT permitted, respond clearly with the reason and do not proceed.
        4. If the action IS permitted but involves sensitive data, flag it and recommend human review.
        5. If the action is fully permitted and low-risk, confirm and allow it to proceed.

        Always be explicit about your decision: PERMITTED, DENIED, or REQUIRES_APPROVAL.
    """,
    tools=[check_policy],
)
