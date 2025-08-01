from sqlmodel import SQLModel, create_engine, Session, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine
from typing import Generator
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

# Import ALL models to register them with SQLModel for complete schema creation


def create_optimized_engine(database_url: str = None) -> Engine:
    """Create database engine with optimal configuration"""
    if database_url is None:
        database_url = settings.get_database_url()

    if database_url.startswith("sqlite"):
        # SQLite-specific optimizations
        connect_args = {
            "check_same_thread": False,
            # SQLite performance optimizations
            "timeout": 20,  # Connection timeout
            "isolation_level": None,  # Autocommit mode for better performance
        }

        # Connection pooling for SQLite
        engine = create_engine(
            database_url,
            echo=False,  # Set to True only for debugging
            connect_args=connect_args,
            poolclass=StaticPool,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=-1,  # No connection recycling for SQLite
            future=True,  # Use SQLAlchemy 2.0 style
        )

        # Apply SQLite pragma settings for better performance
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # Performance optimizations
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-ahead logging
            cursor.execute(
                "PRAGMA synchronous=NORMAL"
            )  # Balanced durability/performance
            cursor.execute("PRAGMA cache_size=10000")  # 10MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp storage
            cursor.execute("PRAGMA mmap_size=134217728")  # 128MB memory mapping
            # Foreign key support
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    elif database_url.startswith("postgresql"):
        # PostgreSQL-specific optimizations
        engine = create_engine(
            database_url,
            echo=False,
            pool_size=10,  # Number of permanent connections
            max_overflow=20,  # Additional connections allowed
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            future=True,
        )
        return engine

    else:
        # Default configuration
        logger.warning(
            f"Using default engine configuration for database: {database_url}"
        )
        return create_engine(database_url, echo=False, pool_pre_ping=True, future=True)


# Import event listener for SQLite optimizations
from sqlalchemy import event

# Create optimized engine
engine = create_optimized_engine()


def create_db_and_tables():
    """Create database tables with error handling"""
    try:
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")

        # Run initial optimizations
        try:
            from database.optimization import get_db_optimizer

            logger.info("Running initial database optimizations...")
            optimizer = get_db_optimizer()
            result = optimizer.create_performance_indexes()
            logger.info(f"Created {result['total_created']} performance indexes")
        except Exception as e:
            logger.warning(f"Could not run initial optimizations: {e}")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """Get database session with proper error handling"""
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def get_session_context():
    """Get session for use in context managers"""
    return Session(engine)


def test_database_connection() -> bool:
    """Test database connectivity"""
    try:
        with Session(engine) as session:
            session.execute(text("SELECT 1")).scalar()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
