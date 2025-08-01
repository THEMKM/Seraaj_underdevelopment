#!/usr/bin/env python3
"""
Seraaj v2 Database Setup Script
Initializes database and populates with demo data for development
"""
import sys
import os
from pathlib import Path

# Add the API directory to Python path
api_dir = Path(__file__).parent / "apps" / "api"
sys.path.insert(0, str(api_dir))

try:
    from database import create_db_and_tables
    from services.unified_seeding_service import seed_database
    from config.settings import settings
    
    def main():
        print("Seraaj v2 Database Setup")
        print("=" * 40)
        print()
        
        print(f"Environment: {settings.environment}")
        print(f"Database URL: {settings.get_database_url()}")
        print()
        
        # Create database tables
        print("1. Creating database tables...")
        try:
            create_db_and_tables()
            print("   ✓ Database tables created successfully")
        except Exception as e:
            print(f"   ✗ Error creating tables: {e}")
            return False
        
        # Seed demo data
        print("\n2. Seeding demo data...")
        try:
            seed_database(clear_existing=True)
            print("   ✓ Demo data seeded successfully")
        except Exception as e:
            print(f"   ✗ Error seeding data: {e}")
            return False
        
        print("\n" + "=" * 40)
        print("Database setup completed successfully!")
        print()
        print("Demo Login Credentials (Password: Demo123!):")
        print()
        print("Volunteers:")
        print("  - layla@example.com (Layla Al-Mansouri)")
        print("  - omar@example.com (Omar Hassan)")
        print("  - fatima@example.com (Fatima Al-Zahra)")
        print()
        print("Organizations:")
        print("  - contact@hopeeducation.org (Hope Education Initiative)")
        print("  - info@cairohealthnetwork.org (Cairo Community Health Network)")
        print()
        print("Admin:")
        print("  - admin@seraaj.org (System Administrator)")
        print()
        print("You can now start the development servers!")
        return True
    
    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this from the project root directory")
    print("and that all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)