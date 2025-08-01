"""
Database Optimization Module for Seraaj API
Provides database indexing, query optimization, and performance monitoring
"""
import os
import logging
from typing import List, Dict, Any, TypedDict, Optional
from sqlmodel import Session, text, select, func
from sqlalchemy import Index, create_engine
from sqlalchemy.engine import Engine


class OptimizationResult(TypedDict):
    """Type definition for database optimization results"""
    success: bool
    indexes_created: List[str]
    tables_optimized: List[str]
    execution_time: float
    recommendations: Optional[List[str]]


class HealthReport(TypedDict):
    """Type definition for database health check results"""
    status: str
    connection_pool: Dict[str, Any]
    table_statistics: Dict[str, Any]
    performance_metrics: Dict[str, float]
    warnings: List[str]
# We'll import these when needed to avoid circular imports
from models import (
    User, Volunteer, Organisation, Opportunity, Application, Review,
    Message, Conversation, FileUpload
    # Payment model removed - not part of MVP
)

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database optimization and performance monitoring"""
    
    def __init__(self, engine: Engine = None):
        self.engine = engine
    
    def create_performance_indexes(self):
        """Create compound indexes for better query performance"""
        
        indexes_to_create = [
            # Opportunity search optimization
            {
                "table": "opportunities",
                "name": "idx_opportunities_search",
                "columns": ["state", "country", "remote_allowed", "created_at"]
            },
            {
                "table": "opportunities", 
                "name": "idx_opportunities_featured",
                "columns": ["featured", "state", "created_at"]
            },
            {
                "table": "opportunities",
                "name": "idx_opportunities_org_state",
                "columns": ["org_id", "state", "created_at"]
            },
            
            # Application workflow optimization
            {
                "table": "applications",
                "name": "idx_applications_volunteer_status",
                "columns": ["vol_id", "status", "created_at"]
            },
            {
                "table": "applications",
                "name": "idx_applications_opportunity_status",
                "columns": ["opp_id", "status", "created_at"]
            },
            {
                "table": "applications",
                "name": "idx_applications_review_workflow",
                "columns": ["status", "submitted_at", "reviewed_at"]
            },
            
            # User activity optimization
            {
                "table": "users",
                "name": "idx_users_role_status",
                "columns": ["role", "status", "created_at"]
            },
            {
                "table": "users",
                "name": "idx_users_email_status",
                "columns": ["email", "status"]
            },
            
            # Review system optimization
            {
                "table": "reviews",
                "name": "idx_reviews_entity_type",
                "columns": ["review_type", "status", "created_at"]
            },
            {
                "table": "reviews",
                "name": "idx_reviews_reviewer_entity",
                "columns": ["reviewer_id", "reviewed_organization_id", "reviewed_volunteer_id"]
            },
            
            # Message system optimization
            {
                "table": "messages",
                "name": "idx_messages_conversation_time",
                "columns": ["conversation_id", "created_at", "status"]
            },
            {
                "table": "conversations",
                "name": "idx_conversations_participants",
                "columns": ["status", "updated_at"]
            },
            
            # File management optimization
            {
                "table": "file_uploads",
                "name": "idx_files_user_status",
                "columns": ["uploaded_by", "status", "created_at"]
            },
            {
                "table": "file_uploads",
                "name": "idx_files_category_status",
                "columns": ["upload_category", "status", "created_at"],
                "optional": True  # Skip if column doesn't exist (schema migration issue)
            },
            
            # Payment system optimization - REMOVED: Payment system not part of MVP
            
            # Analytics optimization (if analytics tables exist)
            {
                "table": "user_activity_logs",
                "name": "idx_activity_user_time",
                "columns": ["user_id", "timestamp", "event_type"],
                "optional": True  # May not exist
            }
        ]
        
        created_indexes = []
        failed_indexes = []
        
        with self.engine.connect() as conn:
            for index_def in indexes_to_create:
                try:
                    # Check if table exists first
                    if index_def.get("optional", False):
                        result = conn.execute(text(
                            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{index_def['table']}'"
                        )).fetchone()
                        if not result:
                            logger.info(f"Skipping index {index_def['name']} - table {index_def['table']} does not exist")
                            continue
                            
                        # Also check if all required columns exist
                        table_info = conn.execute(text(f"PRAGMA table_info({index_def['table']})")).fetchall()
                        existing_columns = [col[1] for col in table_info]
                        missing_columns = [col for col in index_def['columns'] if col not in existing_columns]
                        if missing_columns:
                            logger.info(f"Skipping index {index_def['name']} - missing columns: {missing_columns}")
                            continue
                    
                    # Check if index already exists
                    result = conn.execute(text(
                        f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_def['name']}'"
                    )).fetchone()
                    
                    if result:
                        logger.info(f"Index {index_def['name']} already exists, skipping")
                        continue
                    
                    # Create the index
                    columns_str = ", ".join(index_def['columns'])
                    create_index_sql = f"""
                        CREATE INDEX {index_def['name']} 
                        ON {index_def['table']} ({columns_str})
                    """
                    
                    conn.execute(text(create_index_sql))
                    conn.commit()
                    
                    created_indexes.append(index_def['name'])
                    logger.info(f"Created index: {index_def['name']}")
                    
                except Exception as e:
                    failed_indexes.append({"name": index_def['name'], "error": str(e)})
                    logger.warning(f"Failed to create index {index_def['name']}: {e}")
        
        return {
            "created_indexes": created_indexes,
            "failed_indexes": failed_indexes,
            "total_created": len(created_indexes)
        }
    
    def analyze_query_performance(self, session: Session) -> Dict[str, Any]:
        """Analyze common query patterns for performance issues"""
        
        performance_analysis = {
            "slow_queries": [],
            "missing_indexes": [],
            "recommendations": []
        }
        
        # Test common query patterns
        test_queries = [
            {
                "name": "opportunities_search",
                "description": "Search active opportunities with filters",
                "query": select(Opportunity).where(
                    Opportunity.state == "active"
                ).order_by(Opportunity.created_at.desc()).limit(10)
            },
            {
                "name": "user_applications",
                "description": "Get applications for a user",
                "query": select(Application).where(
                    Application.vol_id == 1
                ).order_by(Application.created_at.desc())
            },
            {
                "name": "opportunity_applications",
                "description": "Get applications for an opportunity",
                "query": select(Application).where(
                    Application.opp_id == 1
                ).order_by(Application.created_at.desc())
            },
            {
                "name": "organization_opportunities",
                "description": "Get opportunities for an organization",
                "query": select(Opportunity).where(
                    Opportunity.org_id == 1
                ).order_by(Opportunity.created_at.desc())
            }
        ]
        
        for test in test_queries:
            try:
                import time
                start_time = time.time()
                
                # Execute query
                result = session.exec(test["query"]).all()
                
                execution_time = time.time() - start_time
                
                if execution_time > 0.1:  # More than 100ms
                    performance_analysis["slow_queries"].append({
                        "name": test["name"],
                        "description": test["description"],
                        "execution_time": round(execution_time, 4),
                        "result_count": len(result)
                    })
                
            except Exception as e:
                logger.warning(f"Query performance test failed for {test['name']}: {e}")
        
        # Add recommendations based on findings
        if performance_analysis["slow_queries"]:
            performance_analysis["recommendations"].extend([
                "Consider adding compound indexes for frequently filtered columns",
                "Implement query result caching for repeated searches",
                "Use pagination consistently to limit result sets"
            ])
        
        return performance_analysis
    
    def get_database_stats(self, session: Session) -> Dict[str, Any]:
        """Get database statistics and health metrics"""
        
        stats = {
            "tables": {},
            "indexes": {},
            "performance": {}
        }
        
        # Get table row counts
        tables_to_check = [
            ("users", User),
            ("volunteers", Volunteer), 
            ("organisations", Organisation),
            ("opportunities", Opportunity),
            ("applications", Application),
            ("reviews", Review),
            ("messages", Message),
            ("conversations", Conversation),
            ("file_uploads", FileUpload)
        ]
        
        for table_name, model_class in tables_to_check:
            try:
                count = session.exec(select(func.count(model_class.id))).first()
                stats["tables"][table_name] = {
                    "row_count": count,
                    "estimated_size": count * 1024 if count else 0  # Rough estimate
                }
            except Exception as e:
                logger.warning(f"Failed to get stats for {table_name}: {e}")
                stats["tables"][table_name] = {"error": str(e)}
        
        # Get index information
        with self.engine.connect() as conn:
            try:
                result = conn.execute(text("""
                    SELECT name, tbl_name, sql 
                    FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """))
                
                indexes = result.fetchall()
                stats["indexes"] = {
                    "total_indexes": len(indexes),
                    "index_list": [
                        {"name": idx[0], "table": idx[1], "definition": idx[2]}
                        for idx in indexes
                    ]
                }
            except Exception as e:
                logger.warning(f"Failed to get index stats: {e}")
                stats["indexes"] = {"error": str(e)}
        
        return stats
    
    def vacuum_database(self):
        """Optimize database by running VACUUM command"""
        
        try:
            with self.engine.connect() as conn:
                logger.info("Starting database VACUUM operation...")
                conn.execute(text("VACUUM"))
                conn.commit()
                logger.info("Database VACUUM completed successfully")
                return {"success": True, "message": "Database optimized successfully"}
        except Exception as e:
            logger.error(f"Database VACUUM failed: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_and_reindex(self):
        """Analyze database and update statistics"""
        
        try:
            with self.engine.connect() as conn:
                logger.info("Analyzing database statistics...")
                conn.execute(text("ANALYZE"))
                conn.commit()
                logger.info("Database analysis completed successfully")
                return {"success": True, "message": "Database statistics updated"}
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return {"success": False, "error": str(e)}


# Global optimizer instance - will be initialized when first used
db_optimizer = None

def get_db_optimizer():
    """Get or create database optimizer instance"""
    global db_optimizer
    if db_optimizer is None:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            from database import engine
            db_optimizer = DatabaseOptimizer(engine)
        except ImportError:
            # Fallback - create engine directly
            from sqlmodel import create_engine
            from config.settings import settings
            database_url = settings.get_database_url()
            engine = create_engine(database_url, connect_args={"check_same_thread": False})
            db_optimizer = DatabaseOptimizer(engine)
    return db_optimizer


def optimize_database() -> Dict[str, Any]:
    """Run full database optimization"""
    
    optimizer = get_db_optimizer()
    
    results = {
        "indexes": {},
        "vacuum": {},
        "analyze": {},
        "performance": {}
    }
    
    # Create performance indexes
    logger.info("Creating performance indexes...")
    results["indexes"] = optimizer.create_performance_indexes()
    
    # Vacuum database
    logger.info("Optimizing database storage...")
    results["vacuum"] = optimizer.vacuum_database()
    
    # Analyze and update statistics
    logger.info("Updating database statistics...")
    results["analyze"] = optimizer.analyze_and_reindex()
    
    # Test query performance
    logger.info("Analyzing query performance...")
    with Session(optimizer.engine) as session:
        results["performance"] = optimizer.analyze_query_performance(session)
    
    return results


def get_database_health() -> Dict[str, Any]:
    """Get comprehensive database health report"""
    
    optimizer = get_db_optimizer()
    
    with Session(optimizer.engine) as session:
        stats = optimizer.get_database_stats(session)
        performance = optimizer.analyze_query_performance(session)
        
        # Calculate health score
        health_score = 100
        
        # Deduct points for slow queries
        slow_query_count = len(performance.get("slow_queries", []))
        health_score -= min(slow_query_count * 10, 30)  # Max 30 points deduction
        
        # Deduct points for missing tables
        error_tables = [name for name, data in stats["tables"].items() if "error" in data]
        health_score -= len(error_tables) * 5
        
        health_status = "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy"
        
        return {
            "health_score": max(health_score, 0),
            "health_status": health_status,
            "statistics": stats,
            "performance": performance,
            "recommendations": performance.get("recommendations", [])
        }