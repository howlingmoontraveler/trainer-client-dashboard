#!/usr/bin/env python3
"""
Database initialization script for Render deployment
Run this via Render Shell: python3 init_database.py
"""

from app import init_db, USE_POSTGRES

print("=" * 60)
print("Database Initialization Script")
print("=" * 60)
print(f"Database Type: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
print("=" * 60)

try:
    init_db()
    print("\n✅ Database initialized successfully!")
    print("\nYou can now:")
    print("1. Log in with demo credentials:")
    print("   - Username: trainer1")
    print("   - Password: password123")
    print("2. Add your own clients and programs")
    print("=" * 60)
except Exception as e:
    print(f"\n❌ Error initializing database: {e}")
    print("\nTroubleshooting:")
    print("1. Check that DATABASE_URL environment variable is set")
    print("2. Verify PostgreSQL database is running")
    print("3. Check Render logs for detailed error messages")
    print("=" * 60)
    raise
