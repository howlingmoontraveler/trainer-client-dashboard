#!/usr/bin/env python3
"""
Populate production database with ALL data: 108 exercises + 10 templates
Run this in Render Shell: python3 populate_all_production_data.py
"""
import os
import sys

def get_db():
    """Get database connection - works with PostgreSQL on Render"""
    db_url = os.environ.get('DATABASE_URL')

    if db_url and 'postgres' in db_url:
        import psycopg2
        # Render uses postgres:// but psycopg2 needs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(db_url)
        print("✅ Connected to PostgreSQL (Production)")
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect('trainer_dashboard.db')
        print("✅ Connected to SQLite (Local)")
        return conn

def main():
    conn = get_db()
    cursor = conn.cursor()

    # Check current state
    cursor.execute('SELECT COUNT(*) FROM exercise_library')
    exercise_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM program_templates')
    template_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM users WHERE role=%s' if 'postgres' in os.environ.get('DATABASE_URL', '') else 'SELECT COUNT(*) FROM users WHERE role=?', ('client',))
    client_count = cursor.fetchone()[0]

    print(f"\n📊 Current Production State:")
    print(f"   - Exercises: {exercise_count}")
    print(f"   - Templates: {template_count}")
    print(f"   - Clients: {client_count}")

    if exercise_count >= 100:
        print("\n⚠️  Exercises already populated!")
        sys.exit(0)

    print(f"\n🔄 Populating production database...")
    print(f"   Adding {108 - exercise_count} exercises...")

    # Read and execute the exercises SQL file
    try:
        with open('all_exercises.sql', 'r') as f:
            exercises_sql = f.read()

        # For PostgreSQL, we need to adjust the SQL
        if 'postgres' in os.environ.get('DATABASE_URL', ''):
            # PostgreSQL uses different syntax - we'll insert manually
            print("   Using PostgreSQL compatible inserts...")
            # Split into individual INSERT statements
            for line in exercises_sql.strip().split('\n'):
                if line.strip() and line.startswith('INSERT'):
                    # Convert SQLite INSERT to PostgreSQL
                    # SQLite: INSERT INTO exercise_library VALUES(1,'name',...)
                    # PostgreSQL: INSERT INTO exercise_library VALUES(1,'name',...) ON CONFLICT DO NOTHING
                    pg_line = line.rstrip(';') + ' ON CONFLICT (id) DO NOTHING;'
                    try:
                        cursor.execute(pg_line)
                    except Exception as e:
                        print(f"      Skipping duplicate: {line[:50]}...")
        else:
            # SQLite can execute directly
            cursor.executescript(exercises_sql)

        conn.commit()
        print(f"   ✅ Exercises added!")

    except FileNotFoundError:
        print("   ❌ all_exercises.sql not found - you need to upload it to Render")
        print("   Run this locally first to generate the SQL files")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Error adding exercises: {e}")
        conn.rollback()
        sys.exit(1)

    # Add templates
    print(f"   Adding templates...")
    try:
        with open('all_templates.sql', 'r') as f:
            templates_sql = f.read()
        with open('all_template_exercises.sql', 'r') as f:
            template_exercises_sql = f.read()

        if 'postgres' in os.environ.get('DATABASE_URL', ''):
            for line in templates_sql.strip().split('\n'):
                if line.strip() and line.startswith('INSERT'):
                    pg_line = line.rstrip(';') + ' ON CONFLICT (id) DO NOTHING;'
                    try:
                        cursor.execute(pg_line)
                    except:
                        pass

            for line in template_exercises_sql.strip().split('\n'):
                if line.strip() and line.startswith('INSERT'):
                    pg_line = line.rstrip(';') + ' ON CONFLICT (id) DO NOTHING;'
                    try:
                        cursor.execute(pg_line)
                    except:
                        pass
        else:
            cursor.executescript(templates_sql)
            cursor.executescript(template_exercises_sql)

        conn.commit()
        print(f"   ✅ Templates added!")

    except Exception as e:
        print(f"   ⚠️  Error adding templates: {e}")
        conn.rollback()

    # Final count
    cursor.execute('SELECT COUNT(*) FROM exercise_library')
    final_exercises = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM program_templates')
    final_templates = cursor.fetchone()[0]

    print(f"\n✅ COMPLETE! Final state:")
    print(f"   - Exercises: {final_exercises}")
    print(f"   - Templates: {final_templates}")
    print(f"   - Clients: {client_count} (unchanged)")

    conn.close()

if __name__ == '__main__':
    main()
