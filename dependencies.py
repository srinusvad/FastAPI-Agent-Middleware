"""
Dependency injection setup for FastAPI.
Includes MockDatabase and dependency functions for use with FastAPI's Depends().
"""

from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from fastapi import Depends


class MockDatabase:
    """
    Mock in-memory database for storing agent session results.
    In production, this would be replaced with async SQLAlchemy or similar.
    """
    
    def __init__(self):
        """Initialize empty in-memory storage."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[int, Dict[str, Any]] = {}
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the database.
        
        Returns:
            True if database is healthy
        """
        try:
            # In real DB, check connection
            return True
        except Exception:
            return False
    
    async def save_session(self, session_id: str, result: Dict[str, Any]) -> bool:
        """
        Save an agent execution result to the database.
        
        Args:
            session_id: Unique session identifier
            result: Session result data
            
        Returns:
            True if save was successful
        """
        try:
            self.sessions[session_id] = {
                **result,
                "saved_at": datetime.now().isoformat(),
            }
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a previously saved session result.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    async def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all saved sessions.
        
        Returns:
            Dictionary of all sessions
        """
        return self.sessions.copy()
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User data if found, None otherwise
        """
        return self.users.get(user_id)
    
    async def save_user(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """
        Save user information.
        
        Args:
            user_id: User identifier
            user_data: User data to save
            
        Returns:
            True if save was successful
        """
        try:
            self.users[user_id] = {
                **user_data,
                "saved_at": datetime.now().isoformat(),
            }
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    async def close(self) -> None:
        """
        Close database connection (cleanup).
        In production, close real DB connection here.
        """
        pass


# Global database instance
_db_instance: Optional[MockDatabase] = None


async def get_db() -> AsyncGenerator[MockDatabase, None]:
    """
    FastAPI dependency function to provide database connection.
    Used with FastAPI's Depends() in routes.
    
    Usage in routes:
        @app.get("/endpoint")
        async def my_endpoint(db: MockDatabase = Depends(get_db)):
            await db.get_session("session-123")
    
    Yields:
        MockDatabase instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = MockDatabase()
    
    try:
        yield _db_instance
    finally:
        # Cleanup if needed
        await _db_instance.close()


class AgentContext:
    """
    Runtime context for agent execution.
    Can be used to pass configuration and dependencies to the agent graph.
    """
    
    def __init__(self, db: MockDatabase, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent context.
        
        Args:
            db: MockDatabase instance
            config: Optional configuration dictionary
        """
        self.db = db
        self.config = config or {}
        self.created_at = datetime.now().isoformat()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)


async def get_agent_context(db: MockDatabase = Depends(get_db)) -> AsyncGenerator[AgentContext, None]:
    """
    FastAPI dependency to provide agent context with database access.
    
    Args:
        db: Database instance from get_db dependency
        
    Yields:
        AgentContext instance
    """
    context = AgentContext(
        db=db,
        config={
            "max_steps": 10,
            "timeout_seconds": 300,
            "model": "mock-gpt",
        },
    )
    yield context
