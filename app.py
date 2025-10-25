from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Check if running on Render with PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

# Try importing psycopg, gracefully fall back to SQLite if not available
if USE_POSTGRES:
    try:
        import psycopg
        from psycopg.rows import dict_row
        app.config['DATABASE_URL'] = DATABASE_URL.replace('postgres://', 'postgresql://', 1) if DATABASE_URL.startswith('postgres://') else DATABASE_URL
        print("Using PostgreSQL database with psycopg3")
    except ImportError as e:
        print("=" * 60)
        print("WARNING: PostgreSQL configured but psycopg not available")
        print(f"Error: {e}")
        print("FALLING BACK TO SQLITE - Data will NOT persist across restarts!")
        print("=" * 60)
        USE_POSTGRES = False
        app.config['DATABASE'] = 'trainer_dashboard.db'
else:
    app.config['DATABASE'] = 'trainer_dashboard.db'
    print("Using SQLite database (data will not persist on Render)")

# Database helper functions
def get_db():
    if USE_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row
        conn = psycopg.connect(app.config['DATABASE_URL'], row_factory=dict_row)
        return PostgresDB(conn)
    else:
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        return db

# Simple wrapper to make PostgreSQL work like SQLite
class PostgresDB:
    def __init__(self, conn):
        self.conn = conn
        self._cursor = None

    def execute(self, query, params=()):
        # Convert SQLite ? to PostgreSQL %s
        query = query.replace('?', '%s')
        # Create a new cursor for each execute to avoid reuse issues
        self._cursor = self.conn.cursor()
        self._cursor.execute(query, params)
        return self._cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        if self._cursor:
            self._cursor.close()
        self.conn.close()

def init_db():
    """Initialize database schema"""
    with app.open_resource('schema.sql', mode='r') as f:
        schema = f.read()

    if USE_POSTGRES:
        # Adapt schema for PostgreSQL
        schema = schema.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
        schema = schema.replace('AUTOINCREMENT', '')
        schema = schema.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT FALSE')
        schema = schema.replace('DATETIME', 'TIMESTAMP')

        import psycopg
        from psycopg.rows import dict_row
        conn = psycopg.connect(app.config['DATABASE_URL'], row_factory=dict_row)
        cursor = conn.cursor()

        # Execute statements individually
        # Remove comment lines from each statement block, but keep the SQL
        raw_statements = schema.split(';')
        statements = []
        for stmt in raw_statements:
            # Remove comment lines but keep SQL
            lines = [line for line in stmt.split('\n') if not line.strip().startswith('--')]
            clean_stmt = '\n'.join(lines).strip()
            if clean_stmt:
                statements.append(clean_stmt)

        errors = []
        for i, stmt in enumerate(statements):
            try:
                # Convert ? to %s for PostgreSQL
                stmt = stmt.replace('?', '%s')
                # Add ON CONFLICT for PostgreSQL inserts to handle duplicates
                if 'INSERT INTO exercise_library' in stmt:
                    stmt = stmt.rstrip(';') + ' ON CONFLICT (name) DO NOTHING'
                elif 'INSERT INTO users' in stmt:
                    stmt = stmt.rstrip(';') + ' ON CONFLICT (username) DO NOTHING'
                elif 'INSERT INTO clients' in stmt:
                    stmt = stmt.rstrip(';') + ' ON CONFLICT (trainer_id, client_id) DO NOTHING'
                cursor.execute(stmt)
            except Exception as e:
                # Ignore duplicate key errors, collect others
                error_msg = str(e).lower()
                if 'duplicate' not in error_msg and 'unique' not in error_msg and 'already exists' not in error_msg:
                    error_detail = f"Statement {i+1}: {str(e)}"
                    print(f"Error executing statement {i+1}: {e}")
                    print(f"Statement was: {stmt[:200]}")
                    errors.append(error_detail)

        # If there were critical errors, raise them
        if errors:
            cursor.close()
            conn.close()
            raise Exception(f"Database initialization failed with {len(errors)} error(s): " + "; ".join(errors[:3]))

        conn.commit()
        cursor.close()
        conn.close()
    else:
        db = get_db()
        try:
            db.cursor().executescript(schema)
            db.commit()
        except Exception as e:
            # Ignore duplicate errors in SQLite
            if 'UNIQUE constraint' not in str(e):
                print(f"Error: {e}")
                raise
        finally:
            db.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def trainer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'trainer':
            flash('Access denied. Trainer account required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            print(f"Login attempt for username: {username}")
            db = get_db()
            print(f"Database connection established, USE_POSTGRES={USE_POSTGRES}")
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            print(f"User query result: {user}")
            db.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                print(f"Login failed - user exists: {user is not None}")
                flash('Invalid username or password.', 'error')
        except Exception as e:
            # Database not initialized or connection error
            import traceback
            print("=" * 60)
            print(f"LOGIN ERROR: {e}")
            print(traceback.format_exc())
            print("=" * 60)
            error_msg = str(e).lower()
            if 'no such table' in error_msg or 'does not exist' in error_msg:
                flash('Database not initialized. Please contact administrator.', 'error')
            else:
                flash(f'Database error: {str(e)}', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow users to change their own password"""
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('change_password.html')

        # Verify current password
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

        if not user or not check_password_hash(user['password_hash'], current_password):
            flash('Current password is incorrect.', 'error')
            db.close()
            return render_template('change_password.html')

        # Update password
        new_password_hash = generate_password_hash(new_password)
        db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, session['user_id']))
        db.commit()
        db.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initialize database - one-time setup"""
    if request.method == 'POST':
        try:
            print("=" * 60)
            print("Starting database initialization...")
            print(f"USE_POSTGRES: {USE_POSTGRES}")
            if USE_POSTGRES:
                print(f"DATABASE_URL configured: {app.config.get('DATABASE_URL', 'NOT SET')[:50]}...")
            init_db()
            print("Database initialization completed successfully!")
            print("=" * 60)
            flash('Database initialized successfully! You can now log in with username: trainer1, password: password123', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print("=" * 60)
            print("ERROR during database initialization:")
            print(error_detail)
            print("=" * 60)
            flash(f'Error initializing database: {str(e)}', 'error')
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Setup Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                    h1 {{ color: #ef4444; }}
                    .error {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 12px; margin: 20px 0; }}
                    pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <h1>Database Initialization Failed</h1>
                <div class="error">
                    <strong>Error:</strong> {str(e)}
                </div>
                <h3>Full Error Details:</h3>
                <pre>{error_detail}</pre>
                <a href="/setup">Try Again</a>
            </body>
            </html>
            '''

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Setup</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            h1 { color: #1e293b; }
            .btn { background: #0d9488; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #0f766e; }
            .warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Database Setup Required</h1>
        <p>The database needs to be initialized before you can use the application.</p>
        <div class="warning">
            <strong>Warning:</strong> This will create all database tables and add demo data. Only run this once!
        </div>
        <form method="POST">
            <button type="submit" class="btn">Initialize Database</button>
        </form>
        <p style="margin-top: 20px;"><small>After setup, login with:<br>Username: <code>trainer1</code><br>Password: <code>password123</code></small></p>
        <p style="margin-top: 20px;"><a href="/diagnostic">Check Database Status</a></p>
    </body>
    </html>
    '''

@app.route('/migrate', methods=['GET', 'POST'])
def migrate():
    """Run database migrations for Phase 1 enhancements"""
    if request.method == 'POST':
        try:
            with app.open_resource('migrate_phase1.sql', mode='r') as f:
                migration = f.read()

            if USE_POSTGRES:
                import psycopg
                from psycopg.rows import dict_row
                conn = psycopg.connect(app.config['DATABASE_URL'], row_factory=dict_row)
                cursor = conn.cursor()

                # Split by semicolon and execute each statement
                statements = [s.strip() for s in migration.split(';') if s.strip()]
                errors = []

                for i, stmt in enumerate(statements):
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        error_msg = str(e).lower()
                        # Ignore "column already exists" errors
                        if 'already exists' not in error_msg and 'duplicate column' not in error_msg:
                            errors.append(f"Statement {i+1}: {str(e)}")

                conn.commit()
                cursor.close()
                conn.close()

                if errors:
                    return f"<h1>Migration completed with warnings</h1><pre>{chr(10).join(errors)}</pre><p><a href='/'>Back to Home</a></p>"
                else:
                    return "<h1>Migration successful!</h1><p>All database changes applied successfully.</p><p><a href='/'>Back to Home</a></p>"
            else:
                # SQLite
                db = get_db()
                statements = [s.strip() for s in migration.split(';') if s.strip()]
                for stmt in statements:
                    try:
                        db.execute(stmt, ())
                    except Exception as e:
                        if 'duplicate column' not in str(e).lower():
                            pass  # Ignore duplicate column errors
                db.commit()
                db.close()
                return "<h1>Migration successful!</h1><p>All database changes applied successfully.</p><p><a href='/'>Back to Home</a></p>"

        except Exception as e:
            import traceback
            return f"<h1>Migration failed</h1><pre>{traceback.format_exc()}</pre><p><a href='/migrate'>Try Again</a></p>"

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Migration</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            h1 { color: #1e293b; }
            .warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }
            .btn { background: #0d9488; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #0f766e; }
        </style>
    </head>
    <body>
        <h1>Database Migration - Phase 1</h1>
        <p>This will add new fields to support enhanced features:</p>
        <ul>
            <li>Extended client profiles (phone, goals, fitness level, medical notes)</li>
            <li>Exercise library enhancements (demo videos, instructions, muscle groups)</li>
            <li>Workout template fields (tempo, rest periods)</li>
            <li>Program templates for cloning</li>
        </ul>
        <div class="warning">
            <strong>Note:</strong> This migration is safe to run multiple times. Existing data will not be affected.
        </div>
        <form method="POST">
            <button type="submit" class="btn">Run Migration</button>
        </form>
        <p style="margin-top: 20px;"><a href="/">Back to Home</a></p>
    </body>
    </html>
    '''

@app.route('/diagnostic')
def diagnostic():
    """Diagnostic page to check database status"""
    info = []
    info.append(f"USE_POSTGRES: {USE_POSTGRES}")

    if USE_POSTGRES:
        info.append(f"DATABASE_URL set: Yes (first 50 chars: {app.config.get('DATABASE_URL', 'NOT SET')[:50]}...)")
    else:
        info.append(f"Using SQLite: {app.config.get('DATABASE', 'NOT SET')}")

    # Try to check if tables exist
    try:
        info.append("Attempting to connect to database...")

        if USE_POSTGRES:
            # Direct connection without wrapper for diagnostic
            import psycopg
            from psycopg.rows import dict_row
            info.append("Creating PostgreSQL connection...")
            conn = psycopg.connect(app.config['DATABASE_URL'], row_factory=dict_row)
            cursor = conn.cursor()
            info.append("Connection successful!")

            # Check PostgreSQL tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            result = cursor.fetchall()
            tables = [row['table_name'] for row in result] if result else []

            if tables:
                info.append(f"Tables found ({len(tables)}): {', '.join(tables)}")

                # Try to count users
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM users")
                    user_count = cursor.fetchone()
                    info.append(f"Users in database: {user_count['count'] if user_count else 0}")

                    # List usernames
                    cursor.execute("SELECT username, role FROM users")
                    users = cursor.fetchall()
                    if users:
                        user_list = ', '.join([f"{u['username']} ({u['role']})" for u in users])
                        info.append(f"User list: {user_list}")
                except Exception as e:
                    info.append(f"Error counting users: {str(e)}")
            else:
                info.append("NO TABLES FOUND - Database not initialized!")

            cursor.close()
            conn.close()
        else:
            # SQLite
            db = get_db()
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", ()).fetchall()
            tables = [row['name'] for row in result] if result else []

            if tables:
                info.append(f"Tables found: {', '.join(tables)}")
                user_count = db.execute("SELECT COUNT(*) as count FROM users", ()).fetchone()
                info.append(f"Users in database: {user_count['count'] if user_count else 0}")
            else:
                info.append("NO TABLES FOUND - Database not initialized!")

            db.close()

    except Exception as e:
        info.append(f"ERROR: {str(e)}")
        import traceback
        info.append(f"Full traceback:\n{traceback.format_exc()}")

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Diagnostic</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }}
            h1 {{ color: #1e293b; }}
            .info {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 12px; margin: 10px 0; white-space: pre-wrap; }}
            .error {{ background: #fee2e2; border-left: 4px solid #ef4444; }}
        </style>
    </head>
    <body>
        <h1>Database Diagnostic</h1>
        {"".join([f'<div class="info {("error" if "ERROR" in item or "Traceback" in item else "")}">{item}</div>' for item in info])}
        <p style="margin-top: 20px;"><a href="/setup">Go to Setup</a> | <a href="/">Go to Login</a></p>
    </body>
    </html>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'trainer':
        return redirect(url_for('trainer_dashboard'))
    else:
        return redirect(url_for('client_dashboard'))

@app.route('/trainer/dashboard')
@login_required
@trainer_required
def trainer_dashboard():
    db = get_db()

    # Get all clients for this trainer with extended profile info
    clients = db.execute('''
        SELECT u.id, u.username, u.full_name, u.email, u.phone, u.fitness_level, u.goals, u.medical_notes, c.created_at
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ?
        ORDER BY u.full_name
    ''', (session['user_id'],)).fetchall()

    # Get upcoming sessions
    sessions_list = db.execute('''
        SELECT ts.id, ts.session_date, ts.duration, ts.status, u.full_name as client_name
        FROM training_sessions ts
        JOIN users u ON ts.client_id = u.id
        WHERE ts.trainer_id = ? AND ts.session_date >= date('now')
        ORDER BY ts.session_date
        LIMIT 10
    ''', (session['user_id'],)).fetchall()

    # Get total programs count
    total_programs = db.execute('''
        SELECT COUNT(*) as count
        FROM programs p
        WHERE p.created_by = ?
    ''', (session['user_id'],)).fetchone()['count']

    db.close()

    return render_template('trainer_dashboard.html',
                         clients=clients,
                         sessions=sessions_list,
                         total_programs=total_programs)

@app.route('/client/dashboard')
@login_required
def client_dashboard():
    db = get_db()

    # Get client's programs (both trainer-assigned and self-created)
    programs = db.execute('''
        SELECT p.id, p.name, p.description, p.created_at, p.created_by, u.full_name as trainer_name,
               CASE WHEN p.created_by = p.client_id THEN 1 ELSE 0 END as is_self_created
        FROM programs p
        JOIN users u ON p.created_by = u.id
        WHERE p.client_id = ?
        ORDER BY p.created_at DESC
    ''', (session['user_id'],)).fetchall()

    # Get upcoming sessions
    sessions_list = db.execute('''
        SELECT ts.id, ts.session_date, ts.duration, ts.status, ts.notes, u.full_name as trainer_name
        FROM training_sessions ts
        JOIN users u ON ts.trainer_id = u.id
        WHERE ts.client_id = ? AND ts.session_date >= date('now')
        ORDER BY ts.session_date
        LIMIT 10
    ''', (session['user_id'],)).fetchall()

    return render_template('client_dashboard.html', programs=programs, sessions=sessions_list)

@app.route('/trainer/clients/add', methods=['GET', 'POST'])
@login_required
@trainer_required
def add_client():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']

        db = get_db()

        # Check if username exists
        existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists.', 'error')
            return render_template('add_client.html')

        # Create client user
        password_hash = generate_password_hash(password)
        if USE_POSTGRES:
            cursor = db.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, 'client', ?, ?)
                RETURNING id
            ''', (username, password_hash, full_name, email))
            client_id = cursor.fetchone()['id']
        else:
            cursor = db.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, 'client', ?, ?)
            ''', (username, password_hash, full_name, email))
            client_id = cursor.lastrowid

        # Link client to trainer
        db.execute('''
            INSERT INTO clients (trainer_id, client_id)
            VALUES (?, ?)
        ''', (session['user_id'], client_id))

        db.commit()
        flash(f'Client {full_name} added successfully!', 'success')
        return redirect(url_for('trainer_dashboard'))

    return render_template('add_client.html')

@app.route('/trainer/client/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_client(client_id):
    """Edit client profile"""
    db = get_db()

    # Verify client belongs to this trainer
    client = db.execute('''
        SELECT u.*
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        goals = request.form.get('goals', '')
        fitness_level = request.form.get('fitness_level', '')
        medical_notes = request.form.get('medical_notes', '')

        db.execute('''
            UPDATE users
            SET full_name = ?, email = ?, phone = ?, goals = ?, fitness_level = ?, medical_notes = ?
            WHERE id = ?
        ''', (full_name, email, phone, goals, fitness_level, medical_notes, client_id))
        db.commit()
        db.close()

        flash(f'Profile updated successfully for {full_name}!', 'success')
        return redirect(url_for('view_client', client_id=client_id))

    return render_template('edit_client.html', client=client)

@app.route('/trainer/exercises', methods=['GET'])
@login_required
@trainer_required
def exercise_library():
    """View and manage exercise library"""
    db = get_db()

    # Get all exercises
    exercises = db.execute('''
        SELECT e.*, u.full_name as created_by_name
        FROM exercise_library e
        LEFT JOIN users u ON e.created_by = u.id
        ORDER BY e.category, e.name
    ''').fetchall()

    # Get unique categories
    categories = db.execute('''
        SELECT DISTINCT category
        FROM exercise_library
        WHERE category IS NOT NULL
        ORDER BY category
    ''').fetchall()

    db.close()

    return render_template('exercise_library.html', exercises=exercises, categories=categories)

@app.route('/trainer/exercises/add', methods=['GET', 'POST'])
@login_required
@trainer_required
def add_exercise():
    """Add custom exercise to library"""
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        equipment = request.form.get('equipment', '')
        description = request.form.get('description', '')
        instructions = request.form.get('instructions', '')
        demo_url = request.form.get('demo_url', '')
        muscle_groups = request.form.get('muscle_groups', '')

        db = get_db()

        # Check if exercise name already exists
        existing = db.execute('SELECT id FROM exercise_library WHERE name = ?', (name,)).fetchone()
        if existing:
            flash('An exercise with this name already exists.', 'error')
            return render_template('add_exercise.html')

        db.execute('''
            INSERT INTO exercise_library
            (name, category, equipment, description, instructions, demo_url, muscle_groups, is_custom, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        ''', (name, category, equipment, description, instructions, demo_url, muscle_groups, session['user_id']))

        db.commit()
        db.close()

        flash(f'Exercise "{name}" added successfully!', 'success')
        return redirect(url_for('exercise_library'))

    return render_template('add_exercise.html')

@app.route('/trainer/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_exercise(exercise_id):
    """Edit exercise in library"""
    db = get_db()

    exercise = db.execute('SELECT * FROM exercise_library WHERE id = ?', (exercise_id,)).fetchone()

    if not exercise:
        flash('Exercise not found.', 'error')
        return redirect(url_for('exercise_library'))

    # Only allow editing custom exercises created by this trainer
    if not exercise['is_custom'] or exercise['created_by'] != session['user_id']:
        flash('You can only edit exercises you created.', 'error')
        return redirect(url_for('exercise_library'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        equipment = request.form.get('equipment', '')
        description = request.form.get('description', '')
        instructions = request.form.get('instructions', '')
        demo_url = request.form.get('demo_url', '')
        muscle_groups = request.form.get('muscle_groups', '')

        db.execute('''
            UPDATE exercise_library
            SET name = ?, category = ?, equipment = ?, description = ?,
                instructions = ?, demo_url = ?, muscle_groups = ?
            WHERE id = ?
        ''', (name, category, equipment, description, instructions, demo_url, muscle_groups, exercise_id))

        db.commit()
        db.close()

        flash(f'Exercise "{name}" updated successfully!', 'success')
        return redirect(url_for('exercise_library'))

    return render_template('edit_exercise.html', exercise=exercise)

@app.route('/trainer/programs/create/<int:client_id>', methods=['GET', 'POST'])
@login_required
@trainer_required
def create_program(client_id):
    db = get_db()

    # Verify client belongs to this trainer
    client = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if USE_POSTGRES:
            cursor = db.execute('''
                INSERT INTO programs (client_id, created_by, name, description)
                VALUES (?, ?, ?, ?)
                RETURNING id
            ''', (client_id, session['user_id'], name, description))
            program_id = cursor.fetchone()['id']
        else:
            cursor = db.execute('''
                INSERT INTO programs (client_id, created_by, name, description)
                VALUES (?, ?, ?, ?)
            ''', (client_id, session['user_id'], name, description))
            program_id = cursor.lastrowid

        # Add exercises with all new fields
        exercise_library_ids = request.form.getlist('exercise_library_id[]')
        exercise_names = request.form.getlist('exercise_name[]')
        exercise_sets = request.form.getlist('exercise_sets[]')
        exercise_reps = request.form.getlist('exercise_reps[]')
        exercise_weights = request.form.getlist('exercise_weight[]')
        exercise_durations = request.form.getlist('exercise_duration[]')
        exercise_rests = request.form.getlist('exercise_rest[]')
        exercise_tempos = request.form.getlist('exercise_tempo[]')
        exercise_notes = request.form.getlist('exercise_notes[]')

        for i, name in enumerate(exercise_names):
            if name.strip():
                library_id = exercise_library_ids[i] if i < len(exercise_library_ids) and exercise_library_ids[i] else None
                weight = exercise_weights[i] if i < len(exercise_weights) else ''
                duration = exercise_durations[i] if i < len(exercise_durations) else ''
                rest_period = exercise_rests[i] if i < len(exercise_rests) else ''
                tempo = exercise_tempos[i] if i < len(exercise_tempos) else ''

                db.execute('''
                    INSERT INTO exercises (program_id, exercise_library_id, name, sets, reps, weight, notes, exercise_order, tempo, rest_period)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (program_id, library_id, name, exercise_sets[i], exercise_reps[i], weight, exercise_notes[i], i + 1, tempo, rest_period))

        db.commit()
        flash('Program created successfully!', 'success')
        return redirect(url_for('view_client', client_id=client_id))

    # Get all exercises from library for dropdown
    exercises_library = db.execute('''
        SELECT id, name, category, equipment, description
        FROM exercise_library
        ORDER BY category, name
    ''').fetchall()

    return render_template('create_program.html', client=client, exercises_library=exercises_library)

@app.route('/client/programs/create', methods=['GET', 'POST'])
@login_required
def create_own_program():
    """Allow clients to create their own workout programs"""
    if session['role'] != 'client':
        flash('Only clients can create their own programs.', 'error')
        return redirect(url_for('dashboard'))

    db = get_db()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if USE_POSTGRES:
            cursor = db.execute('''
                INSERT INTO programs (client_id, created_by, name, description)
                VALUES (?, ?, ?, ?)
                RETURNING id
            ''', (session['user_id'], session['user_id'], name, description))
            program_id = cursor.fetchone()['id']
        else:
            cursor = db.execute('''
                INSERT INTO programs (client_id, created_by, name, description)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], session['user_id'], name, description))
            program_id = cursor.lastrowid

        # Add exercises with all new fields
        exercise_library_ids = request.form.getlist('exercise_library_id[]')
        exercise_names = request.form.getlist('exercise_name[]')
        exercise_sets = request.form.getlist('exercise_sets[]')
        exercise_reps = request.form.getlist('exercise_reps[]')
        exercise_weights = request.form.getlist('exercise_weight[]')
        exercise_durations = request.form.getlist('exercise_duration[]')
        exercise_rests = request.form.getlist('exercise_rest[]')
        exercise_tempos = request.form.getlist('exercise_tempo[]')
        exercise_notes = request.form.getlist('exercise_notes[]')

        for i, name in enumerate(exercise_names):
            if name.strip():
                library_id = exercise_library_ids[i] if i < len(exercise_library_ids) and exercise_library_ids[i] else None
                weight = exercise_weights[i] if i < len(exercise_weights) else ''
                duration = exercise_durations[i] if i < len(exercise_durations) else ''
                rest_period = exercise_rests[i] if i < len(exercise_rests) else ''
                tempo = exercise_tempos[i] if i < len(exercise_tempos) else ''

                db.execute('''
                    INSERT INTO exercises (program_id, exercise_library_id, name, sets, reps, weight, notes, exercise_order, tempo, rest_period)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (program_id, library_id, name, exercise_sets[i], exercise_reps[i], weight, exercise_notes[i], i + 1, tempo, rest_period))

        db.commit()
        db.close()
        flash('Program created successfully!', 'success')
        return redirect(url_for('client_dashboard'))

    # Get all exercises from library for dropdown
    exercises_library = db.execute('''
        SELECT id, name, category, equipment, description
        FROM exercise_library
        ORDER BY category, name
    ''').fetchall()

    db.close()

    return render_template('create_own_program.html', exercises_library=exercises_library)


@app.route('/client/exercises', methods=['GET'])
@login_required
def client_exercise_library():
    """View exercise library (client version)"""
    if session['role'] != 'client':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    db = get_db()

    # Get all exercises
    exercises = db.execute('''
        SELECT e.*, u.full_name as created_by_name
        FROM exercise_library e
        LEFT JOIN users u ON e.created_by = u.id
        ORDER BY e.category, e.name
    ''').fetchall()

    # Get unique categories
    categories = db.execute('''
        SELECT DISTINCT category
        FROM exercise_library
        WHERE category IS NOT NULL
        ORDER BY category
    ''').fetchall()

    db.close()

    return render_template('client_exercise_library.html', exercises=exercises, categories=categories)


@app.route('/client/exercises/add', methods=['GET', 'POST'])
@login_required
def client_add_exercise():
    """Add custom exercise to library (client version)"""
    if session['role'] != 'client':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        equipment = request.form.get('equipment', '')
        description = request.form.get('description', '')
        instructions = request.form.get('instructions', '')
        demo_url = request.form.get('demo_url', '')
        muscle_groups = request.form.get('muscle_groups', '')

        db = get_db()

        # Check if exercise name already exists
        existing = db.execute('SELECT id FROM exercise_library WHERE name = ?', (name,)).fetchone()
        if existing:
            flash('An exercise with this name already exists.', 'error')
            return render_template('client_add_exercise.html')

        db.execute('''
            INSERT INTO exercise_library
            (name, category, equipment, description, instructions, demo_url, muscle_groups, is_custom, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        ''', (name, category, equipment, description, instructions, demo_url, muscle_groups, session['user_id']))

        db.commit()
        db.close()

        flash(f'Exercise "{name}" added successfully!', 'success')
        return redirect(url_for('client_exercise_library'))

    return render_template('client_add_exercise.html')


@app.route('/client/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def client_edit_exercise(exercise_id):
    """Edit exercise in library (client version)"""
    if session['role'] != 'client':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    db = get_db()

    exercise = db.execute('SELECT * FROM exercise_library WHERE id = ?', (exercise_id,)).fetchone()

    if not exercise:
        flash('Exercise not found.', 'error')
        return redirect(url_for('client_exercise_library'))

    # Only allow editing custom exercises created by this client
    if not exercise['is_custom'] or exercise['created_by'] != session['user_id']:
        flash('You can only edit exercises you created.', 'error')
        return redirect(url_for('client_exercise_library'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        equipment = request.form.get('equipment', '')
        description = request.form.get('description', '')
        instructions = request.form.get('instructions', '')
        demo_url = request.form.get('demo_url', '')
        muscle_groups = request.form.get('muscle_groups', '')

        db.execute('''
            UPDATE exercise_library
            SET name = ?, category = ?, equipment = ?, description = ?,
                instructions = ?, demo_url = ?, muscle_groups = ?
            WHERE id = ?
        ''', (name, category, equipment, description, instructions, demo_url, muscle_groups, exercise_id))

        db.commit()
        db.close()

        flash(f'Exercise "{name}" updated successfully!', 'success')
        return redirect(url_for('client_exercise_library'))

    db.close()
    return render_template('client_edit_exercise.html', exercise=exercise)


@app.route('/trainer/client/<int:client_id>')
@login_required
@trainer_required
def view_client(client_id):
    db = get_db()

    # Get client info
    client = db.execute('''
        SELECT u.id, u.username, u.full_name, u.email, c.created_at
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    # Get programs
    programs = db.execute('''
        SELECT * FROM programs
        WHERE client_id = ?
        ORDER BY created_at DESC
    ''', (client_id,)).fetchall()

    # Get sessions
    sessions_list = db.execute('''
        SELECT * FROM training_sessions
        WHERE client_id = ?
        ORDER BY session_date DESC
    ''', (client_id,)).fetchall()

    return render_template('view_client.html', client=client, programs=programs, sessions=sessions_list)

@app.route('/program/<int:program_id>')
@login_required
def view_program(program_id):
    db = get_db()

    # Get program
    program = db.execute('SELECT * FROM programs WHERE id = ?', (program_id,)).fetchone()

    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('dashboard'))

    # Check access
    if session['role'] == 'client' and program['client_id'] != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    # Get exercises
    exercises = db.execute('''
        SELECT * FROM exercises
        WHERE program_id = ?
        ORDER BY exercise_order
    ''', (program_id,)).fetchall()

    return render_template('view_program.html', program=program, exercises=exercises)

@app.route('/trainer/program/edit/<int:program_id>', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_program(program_id):
    db = get_db()

    # Get program and verify trainer has access to it
    program = db.execute('''
        SELECT p.*, u.full_name as client_name
        FROM programs p
        JOIN users u ON p.client_id = u.id
        WHERE p.id = ?
    ''', (program_id,)).fetchone()

    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    # Verify the client belongs to this trainer
    client_check = db.execute('''
        SELECT 1 FROM clients
        WHERE trainer_id = ? AND client_id = ?
    ''', (session['user_id'], program['client_id'])).fetchone()

    if not client_check:
        flash('Access denied.', 'error')
        return redirect(url_for('trainer_dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Update program
        db.execute('''
            UPDATE programs
            SET name = ?, description = ?
            WHERE id = ?
        ''', (name, description, program_id))

        # Delete existing exercises
        db.execute('DELETE FROM exercises WHERE program_id = ?', (program_id,))

        # Add updated exercises
        exercise_library_ids = request.form.getlist('exercise_library_id[]')
        exercise_names = request.form.getlist('exercise_name[]')
        exercise_sets = request.form.getlist('exercise_sets[]')
        exercise_reps = request.form.getlist('exercise_reps[]')
        exercise_notes = request.form.getlist('exercise_notes[]')

        for i, name in enumerate(exercise_names):
            if name.strip():
                library_id = exercise_library_ids[i] if i < len(exercise_library_ids) and exercise_library_ids[i] else None
                db.execute('''
                    INSERT INTO exercises (program_id, exercise_library_id, name, sets, reps, notes, exercise_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (program_id, library_id, name, exercise_sets[i], exercise_reps[i], exercise_notes[i], i + 1))

        db.commit()
        flash('Program updated successfully!', 'success')
        return redirect(url_for('view_program', program_id=program_id))

    # Get existing exercises
    exercises = db.execute('''
        SELECT * FROM exercises
        WHERE program_id = ?
        ORDER BY exercise_order
    ''', (program_id,)).fetchall()

    # Get all exercises from library for dropdown
    exercises_library = db.execute('''
        SELECT id, name, category, equipment, description
        FROM exercise_library
        ORDER BY category, name
    ''').fetchall()

    return render_template('edit_program.html', program=program, exercises=exercises, exercises_library=exercises_library)

@app.route('/trainer/session/schedule/<int:client_id>', methods=['GET', 'POST'])
@login_required
@trainer_required
def schedule_session(client_id):
    db = get_db()

    client = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    if request.method == 'POST':
        session_date = request.form['session_date']
        duration = request.form['duration']
        notes = request.form['notes']

        db.execute('''
            INSERT INTO training_sessions (trainer_id, client_id, session_date, duration, notes, status)
            VALUES (?, ?, ?, ?, ?, 'scheduled')
        ''', (session['user_id'], client_id, session_date, duration, notes))
        db.commit()

        flash('Session scheduled successfully!', 'success')
        return redirect(url_for('view_client', client_id=client_id))

    return render_template('schedule_session.html', client=client)

@app.route('/trainer/client/<int:client_id>/reset-password', methods=['POST'])
@login_required
@trainer_required
def reset_client_password(client_id):
    db = get_db()

    # Verify client belongs to this trainer
    client = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    new_password = request.form['new_password']
    password_hash = generate_password_hash(new_password)

    db.execute('''
        UPDATE users
        SET password_hash = ?
        WHERE id = ?
    ''', (password_hash, client_id))
    db.commit()

    flash(f'Password reset successfully for {client["full_name"]}. New password: {new_password}', 'success')
    return redirect(url_for('view_client', client_id=client_id))

@app.route('/trainer/client/<int:client_id>/delete', methods=['POST'])
@login_required
@trainer_required
def delete_client(client_id):
    """Delete a client and all associated data"""
    db = get_db()

    # Verify client belongs to this trainer
    client = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    client_name = client['full_name']

    try:
        # Delete all related data in correct order (respecting foreign key constraints)

        # 1. Get all program IDs for this client
        programs = db.execute('SELECT id FROM programs WHERE client_id = ?', (client_id,)).fetchall()
        program_ids = [p['id'] for p in programs]

        if program_ids:
            # 2. Delete workout logs (references exercises)
            placeholders = ','.join(['?' for _ in program_ids])
            db.execute(f'''
                DELETE FROM workout_logs
                WHERE exercise_id IN (
                    SELECT id FROM exercises WHERE program_id IN ({placeholders})
                )
            ''', program_ids)

            # 3. Delete exercises (references programs)
            db.execute(f'DELETE FROM exercises WHERE program_id IN ({placeholders})', program_ids)

        # 4. Delete programs
        db.execute('DELETE FROM programs WHERE client_id = ?', (client_id,))

        # 5. Delete training sessions
        db.execute('DELETE FROM training_sessions WHERE client_id = ?', (client_id,))

        # 6. Delete client-trainer relationship
        db.execute('DELETE FROM clients WHERE client_id = ?', (client_id,))

        # 7. Delete user account
        db.execute('DELETE FROM users WHERE id = ?', (client_id,))

        db.commit()
        db.close()

        flash(f'Client {client_name} and all associated data have been permanently deleted.', 'success')
        return redirect(url_for('trainer_dashboard'))

    except Exception as e:
        db.close()
        flash(f'Error deleting client: {str(e)}', 'error')
        return redirect(url_for('view_client', client_id=client_id))

@app.route('/api/log_workout', methods=['POST'])
@login_required
def log_workout():
    data = request.json
    exercise_id = data.get('exercise_id')
    sets_completed = data.get('sets_completed')
    reps_completed = data.get('reps_completed')
    weight_used = data.get('weight_used')
    notes = data.get('notes', '')

    db = get_db()
    db.execute('''
        INSERT INTO workout_logs (client_id, exercise_id, log_date, sets_completed, reps_completed, weight_used, notes)
        VALUES (?, ?, date('now'), ?, ?, ?, ?)
    ''', (session['user_id'], exercise_id, sets_completed, reps_completed, weight_used, notes))
    db.commit()

    return jsonify({'success': True, 'message': 'Workout logged successfully!'})

@app.route('/api/exercises', methods=['GET'])
@login_required
@trainer_required
def get_exercises():
    """Get exercises from library with optional filtering"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')

    db = get_db()
    query = 'SELECT id, name, category, equipment, description FROM exercise_library WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)

    if search:
        query += ' AND name LIKE ?'
        params.append(f'%{search}%')

    query += ' ORDER BY category, name'

    exercises = db.execute(query, params).fetchall()

    return jsonify([{
        'id': ex['id'],
        'name': ex['name'],
        'category': ex['category'],
        'equipment': ex['equipment'],
        'description': ex['description']
    } for ex in exercises])

@app.route('/api/exercises/custom', methods=['POST'])
@login_required
@trainer_required
def add_custom_exercise():
    """Add a custom exercise to the library"""
    data = request.json
    name = data.get('name')
    category = data.get('category', 'Custom')
    equipment = data.get('equipment', '')
    description = data.get('description', '')

    if not name:
        return jsonify({'success': False, 'message': 'Exercise name is required'}), 400

    db = get_db()
    try:
        if USE_POSTGRES:
            cursor = db.execute('''
                INSERT INTO exercise_library (name, category, equipment, description, is_custom, created_by)
                VALUES (?, ?, ?, ?, 1, ?)
                RETURNING id
            ''', (name, category, equipment, description, session['user_id']))
            exercise_id = cursor.fetchone()['id']
        else:
            cursor = db.execute('''
                INSERT INTO exercise_library (name, category, equipment, description, is_custom, created_by)
                VALUES (?, ?, ?, ?, 1, ?)
            ''', (name, category, equipment, description, session['user_id']))
            exercise_id = cursor.lastrowid

        db.commit()

        return jsonify({
            'success': True,
            'exercise': {
                'id': exercise_id,
                'name': name,
                'category': category,
                'equipment': equipment,
                'description': description
            }
        })
    except Exception as e:
        error_msg = str(e).lower()
        if 'unique' in error_msg or 'duplicate' in error_msg:
            return jsonify({'success': False, 'message': 'Exercise already exists'}), 400
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    # Only auto-initialize SQLite database if it doesn't exist
    # PostgreSQL should be initialized manually via Shell
    if not USE_POSTGRES and not os.path.exists(app.config['DATABASE']):
        init_db()
    # Use PORT from environment (for Render) or default to 5000 for local
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
