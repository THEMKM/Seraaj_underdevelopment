"""
Database Package for Seraaj API
===============================

This package handles all database-related operations including:
- Database optimization and health monitoring
- Connection management
- Schema migrations
- Query optimization

Exports common database operations and utilities for use throughout the application.
"""

from typing import Dict, Any
from importlib import metadata

# Version information
try:
    __version__ = metadata.version("seraaj-api")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

# Core database components
from .optimization import (
    optimize_database,
    get_database_health,
    DatabaseOptimizer,
)

# Import core database functions from the database.py module
import importlib.util
import sys
import os

# Import from database.py module explicitly
database_py_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "database.py"
)
spec = importlib.util.spec_from_file_location("database_core", database_py_path)
database_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_core)

# Export all core functions and variables from database.py
create_db_and_tables = database_core.create_db_and_tables
create_optimized_engine = database_core.create_optimized_engine
get_session = database_core.get_session
get_session_context = database_core.get_session_context
test_database_connection = database_core.test_database_connection
engine = database_core.engine

# Type exports for better type hinting
from .optimization import (
    OptimizationResult,
    HealthReport,
)

__all__ = [
    # Core database functions
    "create_db_and_tables",
    "create_optimized_engine",
    "get_session",
    "get_session_context",
    "test_database_connection",
    # Core database variables
    "engine",
    # Optimization functions
    "optimize_database",
    "get_database_health",
    # Classes
    "DatabaseOptimizer",
    # Types
    "OptimizationResult",
    "HealthReport",
    # Version
    "__version__",
]


# Package level type hints for better IDE support
def get_database_version() -> str:
    """Return the current database package version."""
    return __version__
