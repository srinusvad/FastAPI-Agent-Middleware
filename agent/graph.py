"""
LangGraph StateGraph for the agentic workflow.
This defines the core agent loop with nodes for LLM calls and tool execution,
and conditional routing logic.
"""

import json
import random
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.tools import execute_tool, TOOLS


async def llm_node(state: AgentState) -> Dict[str, Any]:
    """
    Mock LLM node that decides whether to call tools or return a final answer.
    A real implementation would call an actual LLM (OpenAI, Anthropic, etc.)
    
    This is a mocked version that:
    1. Randomly decides to call tools or finish
    2. If calling tools, selects from available tools
    3. Returns tool calls in a structured format
    
    Args:
        state: Current AgentState
        
    Returns:
        Dict with updated state fields (messages, tool_calls, step_count)
    """
    # Simulate LLM processing
    user_query = state["user_query"].lower()
    step_count = state["step_count"]
    
    # Heuristics to determine which tools to call based on query
    tool_calls = []
    
    if "search" in user_query or "find" in user_query or "information" in user_query:
        tool_calls.append({
            "tool_name": "search",
            "input": {"query": user_query, "max_results": 3},
        })
    
    if "calculate" in user_query or "compute" in user_query or "math" in user_query or any(
        op in user_query for op in ["+", "-", "*", "/"]
    ):
        # Extract numbers from query for mock calculation
        numbers = [float(s) for s in user_query.split() if s.replace(".", "").isdigit()]
        if not numbers:
            numbers = [2, 3]  # Default
        
        tool_calls.append({
            "tool_name": "calculate",
            "input": {"operation": "add", "numbers": numbers[:3]},
        })
    
    if "weather" in user_query:
        location = "San Francisco"  # Default location
        # Try to extract location from query
        if "in " in user_query:
            parts = user_query.split("in ")
            if len(parts) > 1:
                location = parts[1].split()[0].capitalize()
        
        tool_calls.append({
            "tool_name": "weather",
            "input": {"location": location},
        })
    
    # If no tools matched, use search as default
    if not tool_calls:
        tool_calls.append({
            "tool_name": "search",
            "input": {"query": user_query, "max_results": 5},
        })
    
    # Update state with new tool calls and increment step count
    return {
        "messages": [
            {
                "role": "assistant",
                "content": f"I'll help you with: {user_query}. Calling tools: {[tc['tool_name'] for tc in tool_calls]}",
            }
        ],
        "tool_calls": tool_calls,
        "step_count": step_count + 1,
    }


async def tool_node(state: AgentState) -> Dict[str, Any]:
    """
    Tool execution node that runs the tools returned by the LLM node.
    Each tool input is validated with Pydantic V2 schemas.
    
    Args:
        state: Current AgentState containing tool_calls
        
    Returns:
        Dict with updated state fields (results, step_count)
    """
    results = []
    step_count = state["step_count"]
    
    # Execute each tool call
    for tool_call in state["tool_calls"]:
        tool_name = tool_call.get("tool_name")
        tool_input = tool_call.get("input", {})
        
        try:
            # Execute the tool (input is validated by Pydantic inside tool functions)
            result = await execute_tool(tool_name, tool_input)
            results.append(result)
        except Exception as e:
            results.append(f"Error executing {tool_name}: {str(e)}")
    
    # Build message summarizing tool execution
    message = {
        "role": "assistant",
        "content": f"Tool Results: {'; '.join(results)}" if results else "No tools executed",
    }
    
    return {
        "results": results,
        "step_count": step_count + 1,
        "messages": [message],
    }


async def final_response_node(state: AgentState) -> Dict[str, Any]:
    """
    Final response node that summarizes results into a final answer.
    
    Args:
        state: Current AgentState containing all accumulated results
        
    Returns:
        Dict with updated state fields (status, messages)
    """
    results_text = "\n".join(state["results"]) if state["results"] else "No results found"
    
    final_message = f"Based on my analysis:\n{results_text}"
    
    return {
        "status": "completed",
        "step_count": state["step_count"] + 1,
        "messages": [
            {
                "role": "assistant",
                "content": final_message,
            }
        ],
    }


def routing_logic(state: AgentState) -> Literal["tools", "finish", END]:
    """
    Conditional routing logic that determines next node based on state.
    
    Routes:
    - "tools": If there are pending tool calls to execute
    - "finish": If all tools are executed, go to final response
    - END: Final completion
    
    Args:
        state: Current AgentState
        
    Returns:
        Next node name or END
    """
    # If we have tool calls that haven't been executed yet
    if state["tool_calls"] and not state["results"]:
        return "tools"
    
    # If we have results, generate final response
    if state["results"]:
        return "finish"
    
    # Otherwise we're done
    return END


def create_agent_graph() -> Any:
    """
    Create and compile the LangGraph StateGraph for the agent workflow.
    
    Graph structure:
    START → llm_node → routing_logic → tools_node → finish_node → END
    
    Returns:
        Compiled StateGraph ready for invocation
    """
    # Create StateGraph with AgentState
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("llm", llm_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("finish", final_response_node)
    
    # Set entry point
    workflow.set_entry_point("llm")
    
    # Add conditional routing from llm node
    workflow.add_conditional_edges("llm", routing_logic)
    
    # Add edges
    workflow.add_edge("tools", "finish")
    workflow.add_edge("finish", END)
    
    # Compile the graph
    graph = workflow.compile()
    
    return graph


# Create the agent graph at module load time
agent_graph = create_agent_graph()
