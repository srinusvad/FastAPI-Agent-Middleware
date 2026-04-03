"""
Mock tool implementations for the agentic workflow.
These tools are called by the agent to perform tasks.
Each tool validates inputs using Pydantic schemas.
"""

from typing import Dict, Any, List
from schemas.tools import SearchInput, CalculateInput, WeatherInput


async def search_tool(input_data: Dict[str, Any]) -> str:
    """
    Mock search tool that validates input with SearchInput schema.
    
    Args:
        input_data: Tool input containing query and max_results
        
    Returns:
        Mock search results as a string
    """
    try:
        # Validate input using Pydantic V2 schema
        search_input = SearchInput(**input_data)
        
        # Mock search results based on query
        results = [
            f"Result 1: '{search_input.query}' - Information from source A",
            f"Result 2: '{search_input.query}' - Information from source B",
            f"Result 3: '{search_input.query}' - Information from source C",
        ]
        
        # Limit to max_results
        limited_results = results[: search_input.max_results]
        
        return f"Found {len(limited_results)} results for '{search_input.query}': " + "; ".join(
            limited_results
        )
    except Exception as e:
        return f"Search error: {str(e)}"


async def calculate_tool(input_data: Dict[str, Any]) -> str:
    """
    Mock calculator tool that validates input with CalculateInput schema.
    
    Args:
        input_data: Tool input containing operation and numbers
        
    Returns:
        Calculation result as a string
    """
    try:
        # Validate input using Pydantic V2 schema
        calc_input = CalculateInput(**input_data)
        
        operation = calc_input.operation.lower()
        numbers = calc_input.numbers
        
        if not numbers:
            return "Error: No numbers provided for calculation"
        
        if operation == "add":
            result = sum(numbers)
            return f"Addition result: {' + '.join(map(str, numbers))} = {result}"
        
        elif operation == "subtract":
            result = numbers[0]
            for num in numbers[1:]:
                result -= num
            return f"Subtraction result: {result}"
        
        elif operation == "multiply":
            result = 1
            for num in numbers:
                result *= num
            return f"Multiplication result: {' × '.join(map(str, numbers))} = {result}"
        
        elif operation == "divide":
            if any(n == 0 for n in numbers[1:]):
                return "Error: Division by zero"
            result = numbers[0]
            for num in numbers[1:]:
                result /= num
            return f"Division result: {result}"
        
        else:
            return f"Error: Unknown operation '{operation}'. Use: add, subtract, multiply, divide"
    
    except Exception as e:
        return f"Calculation error: {str(e)}"


async def weather_tool(input_data: Dict[str, Any]) -> str:
    """
    Mock weather tool that validates input with WeatherInput schema.
    
    Args:
        input_data: Tool input containing location
        
    Returns:
        Mock weather information as a string
    """
    try:
        # Validate input using Pydantic V2 schema
        weather_input = WeatherInput(**input_data)
        location = weather_input.location
        
        # Mock weather data
        mock_weather = {
            "San Francisco": "Sunny, 72°F, 10% humidity",
            "New York": "Cloudy, 65°F, 60% humidity",
            "London": "Rainy, 55°F, 85% humidity",
            "Tokyo": "Clear, 68°F, 45% humidity",
        }
        
        weather = mock_weather.get(location, f"Sunny, 70°F, 50% humidity (default for {location})")
        return f"Weather for {location}: {weather}"
    
    except Exception as e:
        return f"Weather error: {str(e)}"


# Tool registry mapping tool names to their implementations
TOOLS: Dict[str, Any] = {
    "search": {
        "func": search_tool,
        "description": "Search for information about a topic",
        "input_schema": SearchInput,
    },
    "calculate": {
        "func": calculate_tool,
        "description": "Perform mathematical calculations",
        "input_schema": CalculateInput,
    },
    "weather": {
        "func": weather_tool,
        "description": "Get weather information for a location",
        "input_schema": WeatherInput,
    },
}


async def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Execute a tool by name with validated input.
    
    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        
    Returns:
        Tool execution result as a string
    """
    if tool_name not in TOOLS:
        return f"Error: Unknown tool '{tool_name}'. Available tools: {', '.join(TOOLS.keys())}"
    
    tool_impl = TOOLS[tool_name]
    return await tool_impl["func"](tool_input)


def get_tool_json_schemas() -> Dict[str, Dict[str, Any]]:
    """
    Get JSON schemas for all available tools.
    These are formatted for LLM consumption.
    
    Returns:
        Dict mapping tool names to their JSON schemas
    """
    schemas = {}
    for tool_name, tool_impl in TOOLS.items():
        schema_class = tool_impl["input_schema"]
        schemas[tool_name] = {
            "description": tool_impl["description"],
            "input_schema": schema_class.model_json_schema(),
        }
    return schemas
