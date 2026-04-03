"""
Pydantic V2 schemas for LLM tool inputs.
These schemas define the structure of inputs for mock tools and are
designed to be easily serializable to JSON for LLM consumption.
"""

from pydantic import BaseModel, Field
from typing import List


class SearchInput(BaseModel):
    """Input schema for search tool - validates LLM tool calls."""
    query: str = Field(
        description="The search query string to find information about",
        example="Python FastAPI",
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum number of results to return",
        example=5,
    )

    class Config:
        json_schema_extra = {
            "example": {"query": "What is FastAPI?", "max_results": 3}
        }


class CalculateInput(BaseModel):
    """Input schema for calculator tool."""
    operation: str = Field(
        description="The operation to perform: 'add', 'subtract', 'multiply', 'divide'",
        example="add",
    )
    numbers: List[float] = Field(
        description="List of numbers to perform the operation on",
        example=[2, 3, 5],
    )

    class Config:
        json_schema_extra = {
            "example": {"operation": "add", "numbers": [2, 3, 5]}
        }


class WeatherInput(BaseModel):
    """Input schema for weather tool."""
    location: str = Field(
        description="City or location to get weather for",
        example="San Francisco",
    )

    class Config:
        json_schema_extra = {
            "example": {"location": "San Francisco"}
        }
