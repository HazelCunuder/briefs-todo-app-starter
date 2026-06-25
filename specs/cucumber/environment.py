"""
Environment configuration for Cucumber (Behave) tests.

This file sets up the test environment for BDD specifications.
It handles API client initialization, database connections, and test fixtures.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add api directory to path
API_DIR = PROJECT_ROOT / "api"
sys.path.insert(0, str(API_DIR))

# Environment variables
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

# Import after path setup
from api.database import Base, engine
from api.models import Todo, User
from sqlalchemy.orm import sessionmaker


# Global test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def before_all(context):
    """Setup before all tests."""
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize context
    context.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    context.db_session = None
    context.current_user = None
    context.created_todos = []
    context.created_users = []
    context.created_lists = []
    context.created_invitations = []
    
    # Setup HTTP client
    import httpx
    context.http_client = httpx.AsyncClient(base_url=context.api_base_url, timeout=30.0)


def after_all(context):
    """Teardown after all tests."""
    # Close HTTP client
    if hasattr(context, 'http_client'):
        context.http_client.aclose()
    
    # Drop test database tables
    Base.metadata.drop_all(bind=engine)


def before_scenario(context, scenario):
    """Setup before each scenario."""
    # Create new database session for each scenario
    context.db_session = TestingSessionLocal()
    
    # Clear tracking lists
    context.created_todos = []
    context.created_users = []
    context.created_lists = []
    context.created_invitations = []
    
    # Set current user to None
    context.current_user = None


def after_scenario(context, scenario):
    """Teardown after each scenario."""
    # Close database session
    if context.db_session:
        context.db_session.close()
        context.db_session = None
    
    # Clean up created resources
    cleanup_resources(context)


def cleanup_resources(context):
    """Clean up all created resources."""
    db = context.db_session
    if not db:
        return
    
    try:
        # Delete in reverse order to respect dependencies
        for invitation in context.created_invitations:
            try:
                db.delete(invitation)
            except:
                pass
        
        for todo in context.created_todos:
            try:
                db.delete(todo)
            except:
                pass
        
        for user in context.created_users:
            try:
                db.delete(user)
            except:
                pass
        
        for list_obj in context.created_lists:
            try:
                db.delete(list_obj)
            except:
                pass
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error cleaning up resources: {e}")


def get_db_session(context):
    """Get the current database session."""
    if not context.db_session:
        context.db_session = TestingSessionLocal()
    return context.db_session


def get_http_client(context):
    """Get the HTTP client."""
    if not hasattr(context, 'http_client'):
        import httpx
        context.http_client = httpx.AsyncClient(
            base_url=context.api_base_url,
            timeout=30.0
        )
    return context.http_client
