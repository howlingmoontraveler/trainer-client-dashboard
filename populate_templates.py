#!/usr/bin/env python3
"""
Populate program templates in production database
Run this after deployment to add the 10 starter templates
"""
import sqlite3
import os

def get_db():
    """Get database connection"""
    db_path = os.environ.get('DATABASE', 'trainer_dashboard.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db

def populate_templates():
    db = get_db()
    cursor = db.cursor()

    # Check if templates already exist
    existing = cursor.execute('SELECT COUNT(*) as count FROM program_templates').fetchone()
    if existing['count'] > 0:
        print(f"Found {existing['count']} existing templates. Skipping population.")
        return

    print("Populating program templates...")

    # Read and execute the SQL files
    with open('create_starter_templates.sql', 'r') as f:
        cursor.executescript(f.read())

    with open('fix_missing_templates.sql', 'r') as f:
        cursor.executescript(f.read())

    db.commit()

    # Verify
    count = cursor.execute('SELECT COUNT(*) as count FROM program_templates').fetchone()
    print(f"✓ Successfully created {count['count']} program templates!")

    db.close()

if __name__ == '__main__':
    populate_templates()
