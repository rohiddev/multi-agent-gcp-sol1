"""
RAG / Search Agent
Retrieves trusted knowledge from enterprise data sources using the configured
retrieval backend (Agent Search, RAG Engine, or Vector Search).
"""

from google.adk.agents import LlmAgent
from tools import search_enterprise_knowledge
from config import RAG_MODEL

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
        4. If the tool returns status "error", report the failure clearly — do not fabricate information.
        5. If no relevant results are found, say so clearly — do not fabricate information.
        6. For complex questions that require multiple retrievals, call the tool multiple times.

        Format: answer first, then sources.
    """,
    tools=[search_enterprise_knowledge],
)
