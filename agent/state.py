"""
Agent state definition for the agentic workflow.
Uses LangGraph-style TypedDict with Annotated reducers for immutable state management.
"""

from typing import Annotated, TypedDict, List, Dict, Any, Optional
from datetime import datetime


def add_messages_simple(left: List[Dict[str, str]], right: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Simple reducer for messages - appends new messages to existing list.
    Avoids LangChain's add_messages which expects message objects.
    """
    return left + right if right else left


def add_tool_calls(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reducer for tool_calls - appends new tool calls to existing list.
    Maintains immutability by creating a new list.
    """
    return left + right if right else left


def add_results(left: List[str], right: List[str]) -> List[str]:
    """
    Reducer for results - appends new results to existing list.
    """
    return left + right if right else left


class AgentState(TypedDict):
    """
    Central state object for the agent workflow.
    Uses plain dictionary message format to avoid LangChain compatibility issues.
    
    Fields:
        messages: Chat message history as plain dicts with 'role' and 'content'
        tool_calls: List of tool calls made by the agent
        results: List of tool execution results
        step_count: Number of execution steps completed
        user_query: Original user query
        session_id: Unique session identifier
        status: Current status of execution
        created_at: Timestamp when state was created
    """
    messages: Annotated[List[Dict[str, str]], add_messages_simple]
    tool_calls: Annotated[List[Dict[str, Any]], add_tool_calls]
    results: Annotated[List[str], add_results]
    step_count: int
    user_query: str
    session_id: str
    status: str
    created_at: str


def create_agent_state(
    user_query: str,
    session_id: str,
) -> AgentState:
    """
    Factory function to create an initial AgentState.
    
    Args:
        user_query: The user's query or task
        session_id: Unique session identifier
        
    Returns:
        Initialized AgentState for the workflow
    """
    return {
        "messages": [{"role": "user", "content": user_query}],
        "tool_calls": [],
        "results": [],
        "step_count": 0,
        "user_query": user_query,
        "session_id": session_id,
        "status": "running",
        "created_at": datetime.now().isoformat(),
    }
