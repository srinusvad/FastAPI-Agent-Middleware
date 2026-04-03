"""
FastAPI Application Entry Point

FastAPI-Agent-Middleware: A demonstration of Python + agentic AI capabilities.

This project showcases:
- Async FastAPI endpoints
- Pydantic V2 schema validation for LLM tool calls
- LangGraph state-based agentic workflow
- Dependency injection with mock database
- Kubernetes-compatible health checks
- Clean separation of concerns
"""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import routers
from routers import health, workflow

# Create FastAPI app with metadata
app = FastAPI(
    title="FastAPI-Agent-Middleware",
    description="A Python FastAPI project demonstrating agentic AI with Pydantic V2 schemas and LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Include routers
app.include_router(health.router)
app.include_router(workflow.router)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Welcome Endpoint",
    tags=["Info"],
)
async def root() -> dict:
    """
    Welcome endpoint with project information.
    """
    return {
        "message": "Welcome to FastAPI-Agent-Middleware",
        "description": "A Python FastAPI project demonstrating agentic AI capabilities",
        "version": "1.0.0",
        "features": [
            "Async FastAPI endpoints",
            "Pydantic V2 schema validation",
            "LangGraph agentic workflow",
            "Dependency injection with mock database",
            "Kubernetes-compatible health checks",
        ],
        "endpoints": {
            "health": "/health (GET)",
            "readiness": "/status/ready (GET)",
            "liveness": "/status/live (GET)",
            "run_agent": "/agent/run-agent (POST)",
            "agent_status": "/agent/status/{session_id} (GET)",
            "list_tools": "/agent/tools (GET)",
            "list_sessions": "/agent/sessions (GET)",
            "docs": "/docs (GET)",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get(
    "/api/version",
    status_code=status.HTTP_200_OK,
    summary="API Version",
    tags=["Info"],
)
async def get_version() -> dict:
    """
    Get API version information.
    """
    return {
        "api_version": "1.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "timestamp": datetime.now().isoformat(),
    }


# Middleware for logging (optional but useful)
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware to log HTTP requests and responses.
    """
    import time
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log to console (in production, use proper logging)
    print(f"{request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response


# Exception handlers (optional but good practice)
@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc):
    """
    Handle ValueError exceptions with proper HTTP response.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


# Event handlers for startup/shutdown (optional)
@app.on_event("startup")
async def startup_event():
    """
    Event handler for application startup.
    """
    print("FastAPI-Agent-Middleware starting up...")
    print(f"Server started at {datetime.now().isoformat()}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Event handler for application shutdown.
    """
    print(f"Server shut down at {datetime.now().isoformat()}")


if __name__ == "__main__":
    """
    Development server entry point.
    
    Run with: uvicorn main:app --reload
    """
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
