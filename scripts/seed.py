#!/usr/bin/env python3
"""
Database Seeding Script for To-Do App

This script populates the database with sample data for development and testing.
It can be run standalone or imported as a module.

Usage:
    # Run directly
    python scripts/seed.py
    
    # With custom options
    python scripts/seed.py --users 10 --todos-per-user 5 --force
    
    # Import and use programmatically
    from scripts.seed import seed_database, clear_database
    seed_database()
"""

import argparse
import logging
import random
import sys
from datetime import datetime, timedelta
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Sample data
SAMPLE_USERS = [
    {"username": "alice", "email": "alice@example.com", "full_name": "Alice Smith"},
    {"username": "bob", "email": "bob@example.com", "full_name": "Bob Johnson"},
    {"username": "charlie", "email": "charlie@example.com", "full_name": "Charlie Brown"},
    {"username": "diana", "email": "diana@example.com", "full_name": "Diana Prince"},
    {"username": "eve", "email": "eve@example.com", "full_name": "Eve Adams"},
]

SAMPLE_TODO_TITLES = [
    "Buy groceries",
    "Finish project",
    "Call mom",
    "Go to gym",
    "Read book",
    "Write documentation",
    "Fix bug",
    "Review PR",
    "Attend meeting",
    "Plan vacation",
    "Pay bills",
    "Clean house",
    "Learn new skill",
    "Update resume",
    "Backup data",
]

SAMPLE_TODO_DESCRIPTIONS = [
    "Buy milk, eggs, and bread from the store",
    "Complete the FastAPI project before deadline",
    "Call mom to check on her health",
    "Go to gym for 1 hour workout",
    "Read the new Python book I bought",
    "Write comprehensive documentation for the API",
    "Fix the critical bug in production",
    "Review the pull request from team member",
    "Attend the weekly team meeting at 2pm",
    "Plan summer vacation to Europe",
    "Pay electricity and internet bills",
    "Clean the entire house this weekend",
    "Learn TypeScript and Svelte",
    "Update my resume with recent projects",
    "Backup all important data to cloud",
]


def get_db_session():
    """Get a database session for seeding."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Get database URL from environment or use default
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://appuser:changeme@localhost:5432/tododb")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal()


def get_models():
    """Import and return models."""
    try:
        from api.models import Base, Todo, User
        return Base, Todo, User
    except ImportError as e:
        logger.error(f"Failed to import models: {e}")
        logger.info("Trying to import from parent directory...")
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from api.models import Base, Todo, User
        return Base, Todo, User


def create_tables(db) -> bool:
    """Create database tables if they don't exist."""
    try:
        Base, _, _ = get_models()
        Base.metadata.create_all(bind=db.bind)
        logger.info("Database tables created/verified")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False


def clear_database(db) -> bool:
    """Clear all data from database tables."""
    try:
        Base, Todo, User = get_models()
        
        # Delete all data (in reverse order of dependencies)
        db.query(Todo).delete()
        db.query(User).delete()
        db.commit()
        
        logger.info("Database cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        db.rollback()
        return False


def generate_random_date() -> datetime:
    """Generate a random date within the last 30 days."""
    now = datetime.utcnow()
    start_date = now - timedelta(days=30)
    random_days = random.randint(0, 30)
    return start_date + timedelta(days=random_days)


def generate_random_due_date() -> Optional[datetime]:
    """Generate a random due date (50% chance of being None)."""
    if random.random() < 0.5:
        return None
    now = datetime.utcnow()
    future_date = now + timedelta(days=random.randint(1, 90))
    return future_date


def create_sample_users(db, count: int = 5) -> List:
    """Create sample users."""
    _, _, User = get_models()
    users = []
    
    for i in range(min(count, len(SAMPLE_USERS))):
        user_data = SAMPLE_USERS[i]
        
        # Check if user already exists
        existing = db.query(User).filter_by(username=user_data["username"]).first()
        if existing:
            users.append(existing)
            continue
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password" hashed
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        users.append(user)
        logger.info(f"Created user: {user.username}")
    
    return users


def create_sample_todos(db, user: any, count: int = 5) -> List:
    """Create sample todos for a user."""
    _, Todo, _ = get_models()
    todos = []
    
    for i in range(count):
        title = random.choice(SAMPLE_TODO_TITLES)
        description = random.choice(SAMPLE_TODO_DESCRIPTIONS)
        
        todo = Todo(
            title=title,
            description=description,
            completed=random.random() < 0.3,  # 30% chance of being completed
            due_date=generate_random_due_date(),
            priority=random.choice(["low", "medium", "high"]),
            user_id=user.id,
            created_at=generate_random_date(),
            updated_at=datetime.utcnow(),
        )
        db.add(todo)
        db.commit()
        db.refresh(todo)
        todos.append(todo)
        logger.info(f"Created todo: {todo.title} (User: {user.username})")
    
    return todos


def seed_database(
    users_count: int = 5,
    todos_per_user: int = 5,
    clear_first: bool = True,
) -> dict:
    """
    Seed the database with sample data.
    
    Args:
        users_count: Number of users to create
        todos_per_user: Number of todos to create per user
        clear_first: Whether to clear existing data first
        
    Returns:
        Dictionary with counts of created items
    """
    db = get_db_session()
    
    try:
        # Create tables
        if not create_tables(db):
            return {"success": False, "error": "Failed to create tables"}
        
        # Clear existing data if requested
        if clear_first:
            if not clear_database(db):
                return {"success": False, "error": "Failed to clear database"}
        
        # Create users
        users = create_sample_users(db, users_count)
        
        # Create todos for each user
        total_todos = 0
        for user in users:
            todos = create_sample_todos(db, user, todos_per_user)
            total_todos += len(todos)
        
        db.commit()
        
        logger.info(f"Seeding completed: {len(users)} users, {total_todos} todos")
        
        return {
            "success": True,
            "users_created": len(users),
            "todos_created": total_todos,
        }
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def seed_test_database() -> dict:
    """
    Seed a test database with minimal data.
    
    Returns:
        Dictionary with counts of created items
    """
    return seed_database(users_count=2, todos_per_user=3, clear_first=True)


def seed_development_database() -> dict:
    """
    Seed a development database with more data.
    
    Returns:
        Dictionary with counts of created items
    """
    return seed_database(users_count=10, todos_per_user=10, clear_first=True)


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Seed the To-Do App database with sample data"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=5,
        help="Number of users to create (default: 5)",
    )
    parser.add_argument(
        "--todos-per-user",
        type=int,
        default=5,
        help="Number of todos per user (default: 5)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        default=True,
        help="Clear existing data before seeding (default: True)",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Do not clear existing data before seeding",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Seed with test data (2 users, 3 todos each)",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Seed with development data (10 users, 10 todos each)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine which seed function to use
    if args.test:
        result = seed_test_database()
    elif args.dev:
        result = seed_development_database()
    else:
        result = seed_database(
            users_count=args.users,
            todos_per_user=args.todos_per_user,
            clear_first=args.clear and not args.no_clear,
        )
    
    # Print result
    if result.get("success"):
        print(f"\n✅ Seeding completed successfully!")
        print(f"   Users created: {result.get('users_created', 0)}")
        print(f"   Todos created: {result.get('todos_created', 0)}")
    else:
        print(f"\n❌ Seeding failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
