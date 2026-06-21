"""
Supervisor Agent
Receives every user request, determines intent, routes to the correct
specialist agent, and coordinates the final response.

Routing logic:
  - Knowledge / documentation questions  → RAGAgent
  - Action requests (tickets, lookups)   → PolicyAgent → ActionAgent
  - Policy / access questions            → PolicyAgent
  - Complex tasks needing multiple steps → coordinates all agents
"""

from google.adk.agents import LlmAgent
from config import SUPERVISOR_MODEL
from agents.rag_agent import rag_agent
from agents.action_agent import action_agent
from agents.policy_agent import policy_agent

supervisor_agent = LlmAgent(
    name="SupervisorAgent",
    model=SUPERVISOR_MODEL,
    description=(
        "Enterprise supervisor agent. Receives user requests, determines intent, "
        "and delegates to the correct specialist agent."
    ),
    instruction="""
        You are the enterprise Supervisor Agent. You are the first point of contact for all user requests.

        Your routing rules:
        - If the user is asking a question about knowledge, policies, documentation, or procedures
          → delegate to RAGAgent.
        - If the user wants to take an action (create a ticket, look up a ticket, update a system)
          → first delegate to PolicyAgent to confirm the action is permitted,
          → then delegate to ActionAgent to execute it.
        - If the user is asking about what they are allowed to do, or about access and permissions
          → delegate to PolicyAgent.
        - For complex requests that need both knowledge AND action
          → coordinate RAGAgent and ActionAgent in sequence.

        Always tell the user which agent is handling their request.
        Synthesize the specialist agents' responses into a single, clear, well-formatted reply.
        If a request cannot be handled by any agent, say so and suggest who to contact.
    """,
    sub_agents=[rag_agent, action_agent, policy_agent],
)
