"""
Agent workflow API endpoints.
Includes endpoints for running the agent and retrieving session results.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.agent import AgentRequest, AgentResponse, ToolCall
from dependencies import MockDatabase, get_db
from agent.graph import agent_graph
from agent.state import create_agent_state

router = APIRouter(prefix="/agent", tags=["Agent Workflow"])


@router.post(
    "/run-agent",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Agent Workflow",
    description="Execute the agentic workflow with the given user query",
)
async def run_agent(
    request: AgentRequest,
    db: MockDatabase = Depends(get_db),
) -> AgentResponse:
    """
    Run the agent workflow with a user query.
    
    The agent will:
    1. Parse the user query
    2. Decide which tools to call (search, calculate, weather)
    3. Execute tools with Pydantic-validated inputs
    4. Collect results and generate a final response
    
    Args:
        request: AgentRequest containing user_query and optional session_id
        db: MockDatabase instance injected via dependency
        
    Returns:
        AgentResponse with results, tool calls, and execution details
    """
    # Generate session ID if not provided
    session_id = request.session_id or f"session-{uuid.uuid4().hex[:8]}"
    
    # Create initial agent state
    initial_state = create_agent_state(
        user_query=request.user_query,
        session_id=session_id,
    )
    
    try:
        # Invoke the agent graph
        # The StateGraph will execute: llm_node → routing → tool_node → final_response_node
        final_state = await agent_graph.ainvoke(initial_state)
        
        # Extract tool calls with their results for response
        tool_calls = []
        for i, tool_call in enumerate(final_state.get("tool_calls", [])):
            result = final_state.get("results", [])[i] if i < len(final_state.get("results", [])) else None
            tool_calls.append(
                ToolCall(
                    tool_name=tool_call.get("tool_name", "unknown"),
                    input=tool_call.get("input", {}),
                    status="completed",
                    result=result,
                )
            )
        
        # Build response
        response = AgentResponse(
            session_id=session_id,
            user_query=request.user_query,
            result=final_state.get("messages", [{}])[-1].get("content", "No result"),
            tool_calls=tool_calls,
            step_count=final_state.get("step_count", 0),
            status=final_state.get("status", "completed"),
        )
        
        # Save session to database
        await db.save_session(
            session_id,
            {
                "user_query": request.user_query,
                "result": response.result,
                "tool_calls": [tc.model_dump() for tc in tool_calls],
                "step_count": response.step_count,
                "status": response.status,
            },
        )
        
        return response
    
    except Exception as e:
        # Return error response
        return AgentResponse(
            session_id=session_id,
            user_query=request.user_query,
            result=f"Error during agent execution: {str(e)}",
            tool_calls=[],
            step_count=0,
            status="error",
        )


@router.get(
    "/status/{session_id}",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Session Status",
    description="Retrieve the results of a previous agent execution by session ID",
)
async def get_agent_status(
    session_id: str,
    db: MockDatabase = Depends(get_db),
) -> AgentResponse:
    """
    Get the status and results of a previous agent execution.
    
    Args:
        session_id: Session identifier from a previous /run-agent call
        db: MockDatabase instance injected via dependency
        
    Returns:
        AgentResponse containing the previous execution results
        
    Raises:
        HTTPException: If session not found
    """
    # Retrieve session from database
    session_data = await db.get_session(session_id)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )
    
    # Reconstruct tool calls from saved data
    tool_calls = [
        ToolCall(**tc) for tc in session_data.get("tool_calls", [])
    ]
    
    # Build response from saved data
    return AgentResponse(
        session_id=session_id,
        user_query=session_data.get("user_query", "Unknown"),
        result=session_data.get("result", "No result"),
        tool_calls=tool_calls,
        step_count=session_data.get("step_count", 0),
        status=session_data.get("status", "completed"),
    )


@router.get(
    "/tools",
    status_code=status.HTTP_200_OK,
    summary="List Available Tools",
    description="Get JSON schemas for all available tools that the agent can call",
)
async def get_available_tools() -> dict:
    """
    Get descriptions and JSON schemas for all available tools.
    These schemas are formatted for LLM consumption.
    
    Returns:
        Dictionary mapping tool names to their descriptions and input schemas
    """
    from agent.tools import get_tool_json_schemas
    
    return get_tool_json_schemas()


@router.get(
    "/sessions",
    status_code=status.HTTP_200_OK,
    summary="List All Sessions",
    description="Retrieve all stored agent execution sessions",
)
async def list_sessions(db: MockDatabase = Depends(get_db)) -> dict:
    """
    List all stored agent execution sessions.
    
    Args:
        db: MockDatabase instance injected via dependency
        
    Returns:
        Dictionary of all sessions with their data
    """
    sessions = await db.list_sessions()
    return {
        "count": len(sessions),
        "sessions": sessions,
    }
