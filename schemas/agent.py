"""
Pydantic V2 schemas for agent workflow API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ToolCall(BaseModel):
    """Schema for a tool call made by the agent."""
    tool_name: str = Field(description="Name of the tool to call")
    input: dict = Field(description="Input parameters for the tool")
    status: Optional[str] = Field(default="pending", description="Status of the tool call")
    result: Optional[str] = Field(default=None, description="Result from tool execution")


class AgentRequest(BaseModel):
    """Request schema for /run-agent endpoint."""
    user_query: str = Field(
        description="The user's query or task for the agent",
        example="What is the capital of France?",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for tracking",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_query": "Search for information about Python FastAPI",
                "session_id": "session-123",
            }
        }


class AgentResponse(BaseModel):
    """Response schema for agent workflow execution."""
    session_id: str = Field(description="Session ID for tracking")
    user_query: str = Field(description="Original user query")
    result: str = Field(description="Final result from the agent")
    tool_calls: List[ToolCall] = Field(
        description="All tool calls made during execution",
        default_factory=list,
    )
    step_count: int = Field(description="Number of steps taken")
    status: str = Field(
        description="Final status of execution: 'success', 'error'",
        example="success",
    )
    timestamp: datetime = Field(
        description="Timestamp of execution",
        default_factory=datetime.now,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "user_query": "Search for Python",
                "result": "Found 5 results about Python programming language",
                "tool_calls": [
                    {
                        "tool_name": "search",
                        "input": {"query": "Python", "max_results": 5},
                        "status": "completed",
                        "result": "Found 5 search results",
                    }
                ],
                "step_count": 2,
                "status": "success",
                "timestamp": "2024-04-03T10:30:00",
            }
        }


class HealthStatus(BaseModel):
    """Health check response schema."""
    status: str = Field(description="Overall system status")
    version: str = Field(description="API version")
    timestamp: str = Field(description="Health check timestamp")


class ReadinessStatus(BaseModel):
    """Readiness probe response schema."""
    ready: bool = Field(description="Whether the service is ready to accept traffic")
    db_healthy: bool = Field(description="Whether the database connection is healthy")
    timestamp: str = Field(description="Readiness check timestamp")
