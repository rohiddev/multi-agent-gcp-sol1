"""
Enterprise tool definitions.
Each function is a plain Python function — ADK converts them into callable tools automatically.
Add new tools here and pass them to the relevant agent's tools= list.
"""

import logging

logger = logging.getLogger(__name__)


def search_knowledge_base(query: str) -> dict:
    """Search the enterprise knowledge base for relevant information.

    Args:
        query: Natural language question or search phrase.

    Returns:
        dict: status and retrieved content.
    """
    # Replace with Agent Search or RAG Engine call — see retrieval/
    logger.info("knowledge_base_search query=%s", query)
    return {"status": "success", "content": f"[stub] Results for: {query}"}


def get_ticket_status(ticket_id: str) -> dict:
    """Retrieve the current status of a service ticket or work item.

    Args:
        ticket_id: The ticket identifier (e.g. INC0012345).

    Returns:
        dict: status and ticket details.
    """
    logger.info("get_ticket_status ticket_id=%s", ticket_id)
    return {"status": "success", "ticket": {"id": ticket_id, "state": "open", "priority": "P2"}}


def create_ticket(summary: str, description: str, priority: str = "P3") -> dict:
    """Create a new service ticket in the ticketing system.

    Args:
        summary: One-line summary of the issue.
        description: Full description of the request.
        priority: P1 | P2 | P3 | P4 (default P3).

    Returns:
        dict: status and new ticket ID.
    """
    logger.info("create_ticket summary=%s priority=%s", summary, priority)
    return {"status": "success", "ticket_id": "INC0099999"}


def check_policy(action: str, user_role: str, resource: str) -> dict:
    """Check whether the requested action is permitted under enterprise policy.

    Args:
        action: The action being requested (e.g. 'delete', 'read', 'approve').
        user_role: The role of the requesting user.
        resource: The resource being accessed.

    Returns:
        dict: allowed (bool) and reason.
    """
    logger.info("check_policy action=%s role=%s resource=%s", action, user_role, resource)
    # Replace with actual IAM / OPA / policy engine call
    allowed = action in ("read", "search", "create_ticket")
    return {
        "allowed": allowed,
        "reason": "permitted by enterprise policy" if allowed else "action requires elevated access",
    }
