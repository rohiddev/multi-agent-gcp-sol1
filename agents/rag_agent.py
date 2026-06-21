"""
RAG / Search Agent
Retrieves trusted knowledge from enterprise data sources using the configured
retrieval backend (Agent Search, RAG Engine, or Vector Search).
"""

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from retrieval import retrieve
from config import RAG_MODEL


def search_enterprise_knowledge(query: str, tool_context: ToolContext) -> dict:
    """Search enterprise knowledge base and return grounded results.

    Args:
        query: The question or search phrase to retrieve information for.

    Returns:
        dict: status, results list, and source backend used.
    """
    results = retrieve(query, top_k=5)
    tool_context.state["last_retrieval_query"] = query
    tool_context.state["last_retrieval_results"] = results
    return {
        "status": "success",
        "results": results,
        "result_count": len(results),
    }


rag_agent = LlmAgent(
    name="RAGAgent",
    model=RAG_MODEL,
    description=(
        "Retrieves accurate, grounded answers from enterprise knowledge sources "
        "including policies, SOPs, runbooks, and internal documentation."
    ),
    instruction="""
        You are the enterprise Knowledge Retrieval Agent.

        Your responsibilities:
        1. Use search_enterprise_knowledge to retrieve relevant information for the user's question.
        2. Ground your answer strictly in the retrieved content — do not add information not present in results.
        3. Always cite the source of your answer.
        4. If no relevant results are found, say so clearly — do not fabricate information.
        5. For complex questions that require multiple retrievals, call the tool multiple times.

        Format: answer first, then sources.
    """,
    tools=[search_enterprise_knowledge],
)
