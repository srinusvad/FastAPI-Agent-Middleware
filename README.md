# FastAPI-Agent-Middleware

A production-ready Python FastAPI project demonstrating **agentic AI capabilities** with:
- **Pydantic V2 schemas** for LLM tool call validation
- **LangGraph state machine** for agentic workflows
- **Dependency injection pattern** with mock database
- **Kubernetes-compatible health checks** (readiness, liveness, detailed health)
- **Clean separation of concerns** (routers, schemas, dependencies, agent logic)

> **Status**: ✅ Fully functional with mock tools. All endpoints tested and working.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements:**
- FastAPI >= 0.108.0
- Uvicorn >= 0.25.0
- Pydantic >= 2.5.0
- LangChain >= 0.1.0
- LangGraph >= 0.0.15
- Python >= 3.10

### 2. Run the Server

```bash
uvicorn main:app --reload
```

Server starts at: `http://localhost:8000`

### 3. Access API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📋 Project Structure

```
FastAPI-Agent-Middleware/
├── main.py                          # FastAPI app entry point + root endpoints
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── agent/                           # Agentic workflow logic
│   ├── __init__.py
│   ├── state.py                    # AgentState TypedDict + create_agent_state()
│   ├── tools.py                    # Mock tool implementations (search, calculate, weather)
│   └── graph.py                    # LangGraph StateGraph + nodes + routing logic
│
├── routers/                         # FastAPI route handlers
│   ├── __init__.py
│   ├── health.py                   # Health, readiness, liveness endpoints
│   └── workflow.py                 # Agent workflow endpoints (run, status, tools, sessions)
│
├── schemas/                         # Pydantic V2 validation models
│   ├── __init__.py
│   ├── agent.py                    # AgentRequest, AgentResponse, ToolCall, HealthStatus
│   └── tools.py                    # SearchInput, CalculateInput, WeatherInput schemas
│
└── dependencies.py                  # Dependency injection (MockDatabase, get_db)
```

---

## 🏗️ Architecture: Mock Agentic Workflow

### State Machine Overview

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│   llm_node       │  ← Mocked LLM decides which tools to call
│  (Heuristic      │    based on user query keywords
│   routing)       │
└────────┬─────────┘
         │ (tool_calls, step_count+1)
         │
    ┌────▼────────────────────┐
    │  routing_logic()         │
    │  - If tool_calls: go tools
    │  - If results: go finish
    │  - Else: END
    └─┬──────┬────────────┬────┘
      │      │            │
   tools  finish         END
      │      │
      ▼      ▼
┌──────────────┐
│  tool_node   │  ← Executes tools with Pydantic-validated inputs
│  (Pydantic   │    Tool outputs merged into state
│   validation)│
└──────┬───────┘
       │ (results, step_count+1)
       │
       ▼
┌──────────────────────────┐
│  final_response_node     │  ← Summarizes results into answer
│  (Consolidation)         │
└────────┬─────────────────┘
         │
         ▼
       ┌──────┐
       │ END  │
       └──────┘
```

**Key Details:**
- **State Type**: `AgentState` (TypedDict with Annotated reducers for immutable updates)
- **Message Format**: Plain Python dicts with `{"role": "...", "content": "..."}` to avoid LangChain compatibility issues
- **Tool Registry**: `TOOLS` dict mapping tool names to implementations
- **Pydantic Validation**: All tool inputs validated via Pydantic V2 schemas before execution

---

## 🛠️ Available Tools

### 1. **Search Tool**
Searches for information about a topic.

**Input Schema:**
```python
class SearchInput(BaseModel):
    query: str              # Search query
    max_results: int = 5    # Max results (1-100)
```

**Example:**
```json
{
  "tool_name": "search",
  "input": {"query": "Python FastAPI", "max_results": 3}
}
```

**Response:**
```
Found 3 results for 'Python FastAPI': Result 1: ... Result 2: ... Result 3: ...
```

---

### 2. **Calculate Tool**
Performs mathematical operations on lists of numbers.

**Input Schema:**
```python
class CalculateInput(BaseModel):
    operation: str          # "add", "subtract", "multiply", "divide"
    numbers: List[float]    # Numbers to operate on
```

**Example:**
```json
{
  "tool_name": "calculate",
  "input": {"operation": "add", "numbers": [2, 3, 5]}
}
```

**Response:**
```
Addition result: 2.0 + 3.0 + 5.0 = 10.0
```

---

### 3. **Weather Tool**
Gets weather information for a location.

**Input Schema:**
```python
class WeatherInput(BaseModel):
    location: str  # City or location name
```

**Example:**
```json
{
  "tool_name": "weather",
  "input": {"location": "San Francisco"}
}
```

**Response:**
```
Weather for San Francisco: Sunny, 72°F, 10% humidity
```

---

## 📡 API Endpoints

### **Health & Status Endpoints**

#### 1. `GET /health` — Detailed Health Check
**Description**: Comprehensive system health information.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-04-03T10:30:00.123456"
}
```

---

#### 2. `GET /status/ready` — Readiness Probe (K8s)
**Description**: Kubernetes-compatible readiness check. Returns ready=true if service can accept traffic.

**Response (200 OK):**
```json
{
  "ready": true,
  "db_healthy": true,
  "timestamp": "2026-04-03T10:30:00.123456"
}
```

---

#### 3. `GET /status/live` — Liveness Probe (K8s)
**Description**: Simple Kubernetes liveness check.

**Response (200 OK):**
```json
{
  "alive": true
}
```

---

### **Agent Workflow Endpoints**

#### 4. `POST /agent/run-agent` — Execute Agent Workflow
**Description**: Run the agentic workflow with a user query. The agent decides which tools to call, executes them, and returns results.

**Request:**
```bash
curl -X POST http://localhost:8000/agent/run-agent \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "What is the weather in London?",
    "session_id": "optional-session-123"
  }'
```

**Request Schema:**
```python
class AgentRequest(BaseModel):
    user_query: str              # The question/task for the agent
    session_id: Optional[str]    # Optional session ID for tracking
```

**Response (200 OK):**
```json
{
  "session_id": "session-1ec30496",
  "user_query": "What is the weather in London?",
  "result": "Based on my analysis:\nWeather for London: Sunny, 70°F, 50% humidity (default for London)",
  "tool_calls": [
    {
      "tool_name": "weather",
      "input": {
        "location": "London"
      },
      "status": "completed",
      "result": "Weather for London: Sunny, 70°F, 50% humidity (default for London)"
    }
  ],
  "step_count": 3,
  "status": "completed",
  "timestamp": "2026-04-03T03:32:25.001413"
}
```

**Response Schema:**
```python
class AgentResponse(BaseModel):
    session_id: str              # Unique session ID
    user_query: str              # Original query
    result: str                  # Final answer from agent
    tool_calls: List[ToolCall]   # All tool calls made
    step_count: int              # Number of execution steps
    status: str                  # "success" or "error"
    timestamp: datetime          # Execution timestamp
```

---

#### 5. `GET /agent/status/{session_id}` — Get Previous Session Results
**Description**: Retrieve results from a previously executed session.

**Request:**
```bash
curl http://localhost:8000/agent/status/session-1ec30496
```

**Response (200 OK):**
```json
{
  "session_id": "session-1ec30496",
  "user_query": "What is the weather in London?",
  "result": "Based on my analysis:\nWeather for London: Sunny, 70°F, 50% humidity (default for London)",
  "tool_calls": [...],
  "step_count": 3,
  "status": "completed",
  "timestamp": "2026-04-03T03:32:25.001413"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Session 'invalid-session-id' not found"
}
```

---

#### 6. `GET /agent/tools` — List Available Tools
**Description**: Returns JSON schemas for all available tools (for LLM consumption).

**Request:**
```bash
curl http://localhost:8000/agent/tools
```

**Response (200 OK):**
```json
{
  "search": {
    "description": "Search for information about a topic",
    "input_schema": {
      "title": "SearchInput",
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search query string"
        },
        "max_results": {
          "type": "integer",
          "default": 5,
          "description": "Maximum number of results"
        }
      },
      "required": ["query"]
    }
  },
  "calculate": {
    "description": "Perform mathematical calculations",
    "input_schema": {...}
  },
  "weather": {
    "description": "Get weather information for a location",
    "input_schema": {...}
  }
}
```

---

#### 7. `GET /agent/sessions` — List All Sessions
**Description**: Retrieve all stored agent execution sessions.

**Request:**
```bash
curl http://localhost:8000/agent/sessions
```

**Response (200 OK):**
```json
{
  "count": 2,
  "sessions": {
    "session-846b496c": {
      "user_query": "Calculate 2 + 3",
      "result": "Based on my analysis:\nAddition result: 2.0 + 3.0 = 5.0",
      "tool_calls": [
        {
          "tool_name": "calculate",
          "input": {"operation": "add", "numbers": [2.0, 3.0]},
          "status": "completed",
          "result": "Addition result: 2.0 + 3.0 = 5.0"
        }
      ],
      "step_count": 3,
      "status": "completed",
      "saved_at": "2026-04-03T03:31:35.604285"
    },
    "session-1ec30496": {...}
  }
}
```

---

### **Info Endpoints**

#### 8. `GET /` — Welcome/Info
**Description**: Project information and available endpoints.

**Response (200 OK):**
```json
{
  "message": "Welcome to FastAPI-Agent-Middleware",
  "description": "A Python FastAPI project demonstrating agentic AI capabilities",
  "version": "1.0.0",
  "features": [
    "Async FastAPI endpoints",
    "Pydantic V2 schema validation",
    "LangGraph agentic workflow",
    "Dependency injection with mock database",
    "Kubernetes-compatible health checks"
  ],
  "endpoints": {
    "health": "/health (GET)",
    "readiness": "/status/ready (GET)",
    "liveness": "/status/live (GET)",
    "run_agent": "/agent/run-agent (POST)",
    "agent_status": "/agent/status/{session_id} (GET)",
    "list_tools": "/agent/tools (GET)",
    "list_sessions": "/agent/sessions (GET)",
    "docs": "/docs (GET)"
  },
  "timestamp": "2026-04-03T10:30:00.123456"
}
```

---

#### 9. `GET /api/version` — API Version
**Description**: API and Python version information.

**Response (200 OK):**
```json
{
  "api_version": "1.0.0",
  "python_version": "3.14.3",
  "timestamp": "2026-04-03T10:30:00.123456"
}
```

---

## 📝 Example Workflows

### Example 1: Mathematical Calculation Query

**Request:**
```powershell
$body = @{"user_query"="Calculate 2 + 3"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/agent/run-agent `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

**Response:**
```json
{
  "session_id": "session-846b496c",
  "user_query": "Calculate 2 + 3",
  "result": "Based on my analysis:\nAddition result: 2.0 + 3.0 = 5.0",
  "tool_calls": [
    {
      "tool_name": "calculate",
      "input": {
        "operation": "add",
        "numbers": [2.0, 3.0]
      },
      "status": "completed",
      "result": "Addition result: 2.0 + 3.0 = 5.0"
    }
  ],
  "step_count": 3,
  "status": "completed",
  "timestamp": "2026-04-03T03:31:35.579165"
}
```

**What Happened:**
1. **llm_node**: Parsed query, detected math operation, created tool call for "calculate"
2. **routing_logic**: Found tool_calls, routed to "tools" node
3. **tool_node**: Executed calculate tool with Pydantic-validated input `{"operation": "add", "numbers": [2.0, 3.0]}`
4. **tool_node**: Merged result into state
5. **routing_logic**: Found results, routed to "finish" node
6. **final_response_node**: Summarized results into final answer
7. **Response**: Returned AgentResponse with all details

---

### Example 2: Weather Query

**Request:**
```powershell
$body = @{"user_query"="What is the weather in London?"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/agent/run-agent `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

**Response:**
```json
{
  "session_id": "session-1ec30496",
  "user_query": "What is the weather in London?",
  "result": "Based on my analysis:\nWeather for London: Sunny, 70°F, 50% humidity (default for London)",
  "tool_calls": [
    {
      "tool_name": "weather",
      "input": {
        "location": "London"
      },
      "status": "completed",
      "result": "Weather for London: Sunny, 70°F, 50% humidity (default for London)"
    }
  ],
  "step_count": 3,
  "status": "completed",
  "timestamp": "2026-04-03T03:32:25.001413"
}
```

**What Happened:**
1. **llm_node**: Parsed query, detected "weather" keyword, created tool call for weather tool
2. **routing_logic**: Routed to tool execution
3. **tool_node**: Called `weather_tool()` with WeatherInput schema validation
4. **Tool execution**: Looked up "London" in mock weather database
5. **final_response_node**: Formatted final answer
6. **Database**: Session stored in MockDatabase for retrieval via `/agent/status/{session_id}`

---

### Example 3: Search Query

**Request:**
```powershell
$body = @{"user_query"="Search for Python programming"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/agent/run-agent `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

**Response:**
```json
{
  "session_id": "session-9d5d2f1f",
  "user_query": "Search for Python programming",
  "result": "Based on my analysis:\nFound 3 results for 'search for python programming': Result 1: ... Result 2: ... Result 3: ...",
  "tool_calls": [
    {
      "tool_name": "search",
      "input": {
        "query": "search for python programming",
        "max_results": 5
      },
      "status": "completed",
      "result": "Found 3 results for 'search for python programming': Result 1: ... Result 2: ... Result 3: ..."
    }
  ],
  "step_count": 3,
  "status": "completed",
  "timestamp": "2026-04-03T03:30:49.981987"
}
```

---

## 🔧 Key Implementation Details

### 1. **Pydantic V2 Schema Validation**

All tool inputs are validated using Pydantic V2 `BaseModel` classes with `Field()` descriptions:

```python
class CalculateInput(BaseModel):
    operation: str = Field(
        description="The operation to perform: 'add', 'subtract', 'multiply', 'divide'",
        example="add",
    )
    numbers: List[float] = Field(
        description="List of numbers to perform the operation on",
        example=[2, 3, 5],
    )
```

**Benefits:**
- Automatic type validation
- JSON schema generation (used by `/agent/tools` endpoint)
- Self-documenting API with examples
- LLM-friendly descriptions for tool calling

---

### 2. **State Management with TypedDict & Reducers**

AgentState uses Annotated reducers for immutable state transitions:

```python
class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, str]], add_messages_simple]
    tool_calls: Annotated[List[Dict[str, Any]], add_tool_calls]
    results: Annotated[List[str], add_results]
    step_count: int
    ...
```

**Benefits:**
- Deterministic state transitions
- Immutable message history
- Type-safe state definitions
- LangGraph-native patterns

---

### 3. **Dependency Injection**

MockDatabase is injected via FastAPI's `Depends()`:

```python
@router.post("/agent/run-agent")
async def run_agent(
    request: AgentRequest,
    db: MockDatabase = Depends(get_db),
) -> AgentResponse:
    # db is automatically provided by FastAPI
    await db.save_session(session_id, result_data)
    return response
```

**Benefits:**
- Easy testing (override dependencies)
- Centralized dependency management
- Type-safe injections
- Production-ready pattern

---

### 4. **Tool Execution with Validation**

Tools are executed with Pydantic validation inside the tool function:

```python
async def search_tool(input_data: Dict[str, Any]) -> str:
    # Validate input using Pydantic V2 schema
    search_input = SearchInput(**input_data)  # Raises ValidationError if invalid
    
    # Execute tool logic
    results = [...]
    return f"Found {len(results)} results..."
```

**Benefits:**
- Runtime validation of LLM-provided inputs
- Clear error messages
- Type safety in tool implementations

---

## 🧪 Testing

### Quick Health Check
```bash
curl http://localhost:8000/health
# Output: {"status":"healthy","version":"1.0.0","timestamp":"..."}
```

### Readiness Check (for K8s)
```bash
curl http://localhost:8000/status/ready
# Output: {"ready":true,"db_healthy":true,"timestamp":"..."}
```

### Run Agent Workflow
```bash
curl -X POST http://localhost:8000/agent/run-agent \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Calculate 5 + 7"}'
```

### List Available Sessions
```bash
curl http://localhost:8000/agent/sessions
# Output: {"count":3,"sessions":{...}}
```

### View Tool Schemas
```bash
curl http://localhost:8000/agent/tools
# Output: JSON schemas for search, calculate, weather
```

---

## 🐳 Production Considerations

### What This Project Demonstrates ✅
- ✅ Async/await patterns with FastAPI
- ✅ Pydantic V2 validation and schema generation
- ✅ LangGraph state machine architecture
- ✅ Dependency injection for testability
- ✅ Kubernetes-ready health checks
- ✅ RESTful API design
- ✅ Error handling and logging
- ✅ Session persistence (mock database)

### What to Add for Production 🚀
- **Real LLM Integration**: Replace mocked LLM with OpenAI, Anthropic, or similar
- **Persistent Database**: Replace MockDatabase with async SQLAlchemy + PostgreSQL
- **Authentication**: Add JWT/OAuth2 token validation
- **Rate Limiting**: Add per-user/IP rate limits
- **Logging**: Add structured logging (Python logging + log aggregation)
- **Monitoring**: Add Prometheus metrics and distributed tracing
- **Error Handling**: Add comprehensive error handling and retries
- **Documentation**: Auto-generated OpenAPI docs (already provided via `/docs`)

---

## 📚 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Python Files** | 12 files |
| **Total Lines of Code** | ~1200 lines |
| **API Endpoints** | 9 endpoints |
| **Pydantic Schemas** | 10+ schemas |
| **Mock Tools** | 3 tools (search, calculate, weather) |
| **Test Coverage** | All endpoints tested & working |
| **Dependencies** | 9 packages |

---

## 🎓 Learning Outcomes

This project proves understanding of:

1. **Python FastAPI Framework**
   - Async route handlers
   - Dependency injection
   - Automatic OpenAPI documentation
   - Request/response validation

2. **Pydantic V2**
   - BaseModel schemas with validation
   - Field descriptions and examples
   - JSON schema generation
   - Type hints and constraints

3. **LangGraph Agentic Patterns**
   - StateGraph definition and compilation
   - Node functions with state updates
   - Conditional routing logic
   - Message reducers for immutability

4. **Software Engineering Best Practices**
   - Clean code architecture
   - Separation of concerns
   - Dependency injection
   - Test-driven development readiness

---

## 📄 License

MIT License - See included LICENSE file for details.

---

## 🤝 Contributing

This is a demonstration project. For questions or improvements, feel free to submit issues or pull requests!

---

## 📞 Support

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **Health Check**: `curl http://localhost:8000/health`

---

**Built with ❤️ using FastAPI, Pydantic V2, and LangGraph**

Version: 1.0.0 | Last Updated: April 3, 2026
