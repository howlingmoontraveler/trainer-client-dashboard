from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'trainer_dashboard.db'

# Template filter for datetime formatting
@app.template_filter('format_date')
def format_date(value):
    """Format datetime or string to YYYY-MM-DD"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value[:10]
    # It's a datetime object
    return value.strftime('%Y-%m-%d')

# Database helper functions
class DatabaseWrapper:
    """Wrapper to make PostgreSQL and SQLite work the same way"""
    def __init__(self, conn, is_postgres=False):
        self.conn = conn
        self.is_postgres = is_postgres
        self._cursor = None

    def execute(self, query, params=()):
        """Execute a query with automatic parameter conversion"""
        cursor = self.conn.cursor()

        # Convert ? to %s for PostgreSQL
        if self.is_postgres and '?' in query:
            query = query.replace('?', '%s')

        cursor.execute(query, params)
        return cursor

    def executescript(self, script):
        """Execute a script (SQLite style)"""
        cursor = self.conn.cursor()
        if self.is_postgres:
            cursor.execute(script)
        else:
            cursor.executescript(script)
        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def cursor(self):
        return self.conn.cursor()

def get_db():
    """Get database connection - works with both SQLite (local) and PostgreSQL (Render)"""
    db_url = os.environ.get('DATABASE_URL')

    if db_url and 'postgres' in db_url:
        # Production: Use PostgreSQL
        import psycopg2
        from psycopg2.extras import RealDictConnection

        # Render uses postgres:// but psycopg2 needs postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)

        conn = psycopg2.connect(db_url, connection_factory=RealDictConnection)
        conn.autocommit = False
        return DatabaseWrapper(conn, is_postgres=True)
    else:
        # Local: Use SQLite
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        return DatabaseWrapper(db, is_postgres=False)

def init_db():
    db = get_db()
    cursor = db.cursor()
    is_postgres = os.environ.get('DATABASE_URL') and 'postgres' in os.environ.get('DATABASE_URL')

    # Use different schema files for PostgreSQL vs SQLite
    schema_file = 'schema_postgres.sql' if is_postgres else 'schema.sql'

    try:
        with app.open_resource(schema_file, mode='r') as f:
            schema_sql = f.read()
    except:
        # Fallback to regular schema.sql if postgres version doesn't exist
        with app.open_resource('schema.sql', mode='r') as f:
            schema_sql = f.read()

    # For PostgreSQL, execute as single statement
    if is_postgres:
        cursor.execute(schema_sql)
    else:
        # SQLite supports executescript
        cursor.executescript(schema_sql)

    db.commit()
    print(f"✅ Database initialized using {schema_file}")

def auto_populate_db():
    """Auto-populate database with exercises and templates if empty"""
    db = get_db()
    cursor = db.cursor()
    is_postgres = os.environ.get('DATABASE_URL') and 'postgres' in os.environ.get('DATABASE_URL')

    try:
        # Check if exercises need to be populated
        cursor.execute('SELECT COUNT(*) FROM exercise_library')
        result = cursor.fetchone()
        exercise_count = result['count'] if is_postgres else result[0]

        if exercise_count < 10:  # If less than 10 exercises, populate
            print(f"📊 Database has only {exercise_count} exercises. Auto-populating...")

            # Check if SQL files exist
            if os.path.exists('all_exercises.sql'):
                print("   Loading exercises from all_exercises.sql...")
                with open('all_exercises.sql', 'r') as f:
                    sql_content = f.read()

                if is_postgres:
                    # Execute each INSERT separately for PostgreSQL
                    for line in sql_content.strip().split('\n'):
                        if line.strip() and line.startswith('INSERT'):
                            try:
                                cursor.execute(line)
                            except:
                                pass  # Skip duplicates
                else:
                    cursor.executescript(sql_content)

                db.commit()
                print("   ✅ Exercises loaded!")

            # Load templates if file exists
            if os.path.exists('all_templates.sql') and os.path.exists('all_template_exercises.sql'):
                print("   Loading templates...")
                with open('all_templates.sql', 'r') as f:
                    sql_content = f.read()

                if is_postgres:
                    for line in sql_content.strip().split('\n'):
                        if line.strip() and line.startswith('INSERT'):
                            try:
                                cursor.execute(line)
                            except:
                                pass
                else:
                    cursor.executescript(sql_content)

                with open('all_template_exercises.sql', 'r') as f:
                    sql_content = f.read()

                if is_postgres:
                    for line in sql_content.strip().split('\n'):
                        if line.strip() and line.startswith('INSERT'):
                            try:
                                cursor.execute(line)
                            except:
                                pass
                else:
                    cursor.executescript(sql_content)

                db.commit()
                print("   ✅ Templates loaded!")

            # Final count
            cursor.execute('SELECT COUNT(*) FROM exercise_library')
            result = cursor.fetchone()
            final_count = result['count'] if is_postgres else result[0]

            cursor.execute('SELECT COUNT(*) FROM program_templates')
            result = cursor.fetchone()
            template_count = result['count'] if is_postgres else result[0]

            print(f"✅ Database populated: {final_count} exercises, {template_count} templates")
        else:
            print(f"✅ Database already populated ({exercise_count} exercises)")

    except Exception as e:
        print(f"⚠️  Auto-populate error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

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

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

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

    # Get all clients for this trainer
    clients = db.execute('''
        SELECT u.id, u.username, u.full_name, u.email, c.created_at
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

    return render_template('trainer_dashboard.html', clients=clients, sessions=sessions_list)

@app.route('/client/dashboard')
@login_required
def client_dashboard():
    db = get_db()

    # Get client's programs
    programs = db.execute('''
        SELECT p.id, p.name, p.description, p.created_at, u.full_name as trainer_name
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

        cursor = db.execute('''
            INSERT INTO programs (client_id, created_by, name, description)
            VALUES (?, ?, ?, ?)
        ''', (client_id, session['user_id'], name, description))
        program_id = cursor.lastrowid

        # Add exercises
        exercise_names = request.form.getlist('exercise_name[]')
        exercise_sets = request.form.getlist('exercise_sets[]')
        exercise_reps = request.form.getlist('exercise_reps[]')
        exercise_notes = request.form.getlist('exercise_notes[]')

        for i, name in enumerate(exercise_names):
            if name.strip():
                db.execute('''
                    INSERT INTO exercises (program_id, name, sets, reps, notes, exercise_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (program_id, name, exercise_sets[i], exercise_reps[i], exercise_notes[i], i + 1))

        db.commit()
        flash('Program created successfully!', 'success')
        return redirect(url_for('view_client', client_id=client_id))

    return render_template('create_program.html', client=client)

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

# Exercise Library Routes
@app.route('/trainer/exercises')
@login_required
@trainer_required
def exercises_list():
    db = get_db()

    # Get filter parameters
    category = request.args.get('category', '')
    difficulty = request.args.get('difficulty', '')
    equipment = request.args.get('equipment', '')
    muscle_group = request.args.get('muscle_group', '')
    search = request.args.get('search', '')

    # Build query
    query = 'SELECT * FROM exercise_library WHERE 1=1'
    params = []

    if category:
        query += ' AND category = ?'
        params.append(category)

    if difficulty:
        query += ' AND difficulty_level = ?'
        params.append(difficulty)

    if equipment:
        query += ' AND equipment LIKE ?'
        params.append(f'%{equipment}%')

    if muscle_group:
        query += ' AND muscle_groups LIKE ?'
        params.append(f'%{muscle_group}%')

    if search:
        query += ' AND (name LIKE ? OR description LIKE ? OR muscle_groups LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])

    query += ' ORDER BY name'

    exercises = db.execute(query, params).fetchall()

    # Get unique values for filters
    categories = db.execute('SELECT DISTINCT category FROM exercise_library WHERE category IS NOT NULL ORDER BY category').fetchall()
    equipment_list = db.execute('SELECT DISTINCT equipment FROM exercise_library WHERE equipment IS NOT NULL ORDER BY equipment').fetchall()

    # Extract unique muscle groups (they're stored as comma-separated strings)
    muscle_groups_raw = db.execute('SELECT DISTINCT muscle_groups FROM exercise_library WHERE muscle_groups IS NOT NULL').fetchall()
    muscle_groups_set = set()
    for row in muscle_groups_raw:
        if row['muscle_groups']:
            for mg in row['muscle_groups'].split(','):
                muscle_groups_set.add(mg.strip())
    muscle_groups = sorted(list(muscle_groups_set))

    return render_template('exercises_list.html', exercises=exercises, categories=categories,
                         equipment_list=equipment_list, muscle_groups=muscle_groups,
                         current_category=category, current_difficulty=difficulty,
                         current_equipment=equipment, current_muscle_group=muscle_group,
                         current_search=search)

@app.route('/trainer/exercises/create', methods=['GET', 'POST'])
@login_required
@trainer_required
def create_exercise():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        instructions = request.form['instructions']
        muscle_groups = request.form['muscle_groups']
        equipment = request.form['equipment']
        difficulty_level = request.form['difficulty_level']
        
        db = get_db()
        db.execute('''
            INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, description, instructions, muscle_groups, equipment, difficulty_level, session['user_id']))
        db.commit()
        
        flash('Exercise created successfully!', 'success')
        return redirect(url_for('exercises_list'))
    
    return render_template('create_exercise.html')

@app.route('/trainer/exercises/<int:exercise_id>')
@login_required
@trainer_required
def view_exercise(exercise_id):
    db = get_db()
    exercise = db.execute('SELECT * FROM exercise_library WHERE id = ?', (exercise_id,)).fetchone()
    
    if not exercise:
        flash('Exercise not found.', 'error')
        return redirect(url_for('exercises_list'))
    
    return render_template('view_exercise.html', exercise=exercise)

@app.route('/trainer/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def edit_exercise(exercise_id):
    db = get_db()
    exercise = db.execute('SELECT * FROM exercise_library WHERE id = ?', (exercise_id,)).fetchone()
    
    if not exercise:
        flash('Exercise not found.', 'error')
        return redirect(url_for('exercises_list'))
    
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        instructions = request.form['instructions']
        muscle_groups = request.form['muscle_groups']
        equipment = request.form['equipment']
        difficulty_level = request.form['difficulty_level']
        
        db.execute('''
            UPDATE exercise_library 
            SET name = ?, category = ?, description = ?, instructions = ?, muscle_groups = ?, equipment = ?, difficulty_level = ?
            WHERE id = ?
        ''', (name, category, description, instructions, muscle_groups, equipment, difficulty_level, exercise_id))
        db.commit()
        
        flash('Exercise updated successfully!', 'success')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
    
    return render_template('edit_exercise.html', exercise=exercise)

@app.route('/trainer/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
@trainer_required
def delete_exercise(exercise_id):
    db = get_db()

    # Check if exercise exists
    exercise = db.execute('SELECT * FROM exercise_library WHERE id = ?', (exercise_id,)).fetchone()
    if not exercise:
        flash('Exercise not found.', 'error')
        return redirect(url_for('exercises_list'))

    # Check if exercise is used in any programs
    programs_using = db.execute('''
        SELECT COUNT(*) as count FROM exercises e
        JOIN programs p ON e.program_id = p.id
        WHERE e.name = ?
    ''', (exercise['name'],)).fetchone()

    if programs_using['count'] > 0:
        flash('Cannot delete exercise - it is being used in existing programs.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))

    db.execute('DELETE FROM exercise_library WHERE id = ?', (exercise_id,))
    db.commit()

    flash('Exercise deleted successfully!', 'success')
    return redirect(url_for('exercises_list'))

# Analytics Routes
@app.route('/trainer/analytics')
@login_required
@trainer_required
def analytics_dashboard():
    db = get_db()
    trainer_id = session['user_id']

    # Total clients
    total_clients = db.execute('''
        SELECT COUNT(*) as count FROM clients WHERE trainer_id = ?
    ''', (trainer_id,)).fetchone()['count']

    # Total programs created
    total_programs = db.execute('''
        SELECT COUNT(*) as count FROM programs WHERE created_by = ?
    ''', (trainer_id,)).fetchone()['count']

    # Total workout logs across all clients
    total_workouts_logged = db.execute('''
        SELECT COUNT(*) as count FROM workout_logs wl
        JOIN clients c ON wl.client_id = c.client_id
        WHERE c.trainer_id = ?
    ''', (trainer_id,)).fetchone()['count']

    # Client engagement - clients with at least one workout log in last 30 days
    active_clients = db.execute('''
        SELECT COUNT(DISTINCT wl.client_id) as count
        FROM workout_logs wl
        JOIN clients c ON wl.client_id = c.client_id
        WHERE c.trainer_id = ? AND wl.log_date >= date('now', '-30 days')
    ''', (trainer_id,)).fetchone()['count']

    # Most active clients (top 10 by workout logs)
    most_active_clients = db.execute('''
        SELECT u.full_name, u.email, COUNT(wl.id) as workout_count,
               MAX(wl.log_date) as last_workout
        FROM users u
        JOIN clients c ON u.id = c.client_id
        LEFT JOIN workout_logs wl ON u.id = wl.client_id
        WHERE c.trainer_id = ?
        GROUP BY u.id, u.full_name, u.email
        ORDER BY workout_count DESC
        LIMIT 10
    ''', (trainer_id,)).fetchall()

    # Most popular exercises (top 10 by usage in workout logs)
    popular_exercises = db.execute('''
        SELECT e.name, COUNT(wl.id) as log_count
        FROM exercises e
        JOIN workout_logs wl ON e.id = wl.exercise_id
        JOIN programs p ON e.program_id = p.id
        WHERE p.created_by = ?
        GROUP BY e.name
        ORDER BY log_count DESC
        LIMIT 10
    ''', (trainer_id,)).fetchall()

    # Program completion rates (programs with at least one logged workout)
    program_engagement = db.execute('''
        SELECT p.name, p.client_id, u.full_name as client_name,
               COUNT(DISTINCT e.id) as total_exercises,
               COUNT(DISTINCT wl.exercise_id) as logged_exercises,
               CAST(COUNT(DISTINCT wl.exercise_id) AS FLOAT) / COUNT(DISTINCT e.id) * 100 as completion_rate
        FROM programs p
        JOIN users u ON p.client_id = u.id
        LEFT JOIN exercises e ON p.id = e.program_id
        LEFT JOIN workout_logs wl ON e.id = wl.exercise_id
        WHERE p.created_by = ? AND e.id IS NOT NULL
        GROUP BY p.id, p.name, p.client_id, u.full_name
        ORDER BY completion_rate DESC
        LIMIT 15
    ''', (trainer_id,)).fetchall()

    # Workout logs over time (last 30 days)
    workout_trend = db.execute('''
        SELECT DATE(wl.log_date) as log_date, COUNT(*) as count
        FROM workout_logs wl
        JOIN clients c ON wl.client_id = c.client_id
        WHERE c.trainer_id = ? AND wl.log_date >= date('now', '-30 days')
        GROUP BY DATE(wl.log_date)
        ORDER BY log_date
    ''', (trainer_id,)).fetchall()

    # Exercise category distribution in library
    category_distribution = db.execute('''
        SELECT category, COUNT(*) as count
        FROM exercise_library
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    ''').fetchall()

    return render_template('analytics_dashboard.html',
                         total_clients=total_clients,
                         total_programs=total_programs,
                         total_workouts_logged=total_workouts_logged,
                         active_clients=active_clients,
                         most_active_clients=most_active_clients,
                         popular_exercises=popular_exercises,
                         program_engagement=program_engagement,
                         workout_trend=workout_trend,
                         category_distribution=category_distribution)

# Program Templates Routes
@app.route('/trainer/program-templates')
@login_required
@trainer_required
def program_templates():
    db = get_db()

    # Get all templates created by this trainer
    templates = db.execute('''
        SELECT pt.id, pt.created_by, pt.name, pt.description, pt.created_at, COUNT(pte.id) as exercise_count
        FROM program_templates pt
        LEFT JOIN program_template_exercises pte ON pt.id = pte.template_id
        WHERE pt.created_by = ?
        GROUP BY pt.id, pt.created_by, pt.name, pt.description, pt.created_at
        ORDER BY pt.created_at DESC
    ''', (session['user_id'],)).fetchall()

    return render_template('program_templates.html', templates=templates)

@app.route('/trainer/program-templates/create', methods=['GET', 'POST'])
@login_required
@trainer_required
def create_program_template():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        db = get_db()
        cursor = db.execute('''
            INSERT INTO program_templates (created_by, name, description)
            VALUES (?, ?, ?)
        ''', (session['user_id'], name, description))
        template_id = cursor.lastrowid

        # Add exercises to template
        exercise_names = request.form.getlist('exercise_name[]')
        exercise_sets = request.form.getlist('exercise_sets[]')
        exercise_reps = request.form.getlist('exercise_reps[]')
        exercise_notes = request.form.getlist('exercise_notes[]')

        for i, name in enumerate(exercise_names):
            if name.strip():
                db.execute('''
                    INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (template_id, name, exercise_sets[i], exercise_reps[i], exercise_notes[i], i + 1))

        db.commit()
        flash('Program template created successfully!', 'success')
        return redirect(url_for('program_templates'))

    return render_template('create_program_template.html')

@app.route('/trainer/program-templates/<int:template_id>')
@login_required
@trainer_required
def view_program_template(template_id):
    db = get_db()

    template = db.execute('''
        SELECT * FROM program_templates WHERE id = ? AND created_by = ?
    ''', (template_id, session['user_id'])).fetchone()

    if not template:
        flash('Template not found.', 'error')
        return redirect(url_for('program_templates'))

    exercises = db.execute('''
        SELECT * FROM program_template_exercises
        WHERE template_id = ?
        ORDER BY exercise_order
    ''', (template_id,)).fetchall()

    return render_template('view_program_template.html', template=template, exercises=exercises)

@app.route('/trainer/program-templates/<int:template_id>/apply/<int:client_id>', methods=['POST'])
@login_required
@trainer_required
def apply_template_to_client(template_id, client_id):
    db = get_db()

    # Verify template belongs to trainer
    template = db.execute('''
        SELECT * FROM program_templates WHERE id = ? AND created_by = ?
    ''', (template_id, session['user_id'])).fetchone()

    if not template:
        flash('Template not found.', 'error')
        return redirect(url_for('program_templates'))

    # Verify client belongs to trainer
    client = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], client_id)).fetchone()

    if not client:
        flash('Client not found.', 'error')
        return redirect(url_for('program_templates'))

    # Create program from template
    cursor = db.execute('''
        INSERT INTO programs (client_id, created_by, name, description)
        VALUES (?, ?, ?, ?)
    ''', (client_id, session['user_id'], template['name'], template['description']))
    program_id = cursor.lastrowid

    # Copy exercises from template
    template_exercises = db.execute('''
        SELECT * FROM program_template_exercises
        WHERE template_id = ?
        ORDER BY exercise_order
    ''', (template_id,)).fetchall()

    for ex in template_exercises:
        db.execute('''
            INSERT INTO exercises (program_id, name, sets, reps, notes, exercise_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (program_id, ex['name'], ex['sets'], ex['reps'], ex['notes'], ex['exercise_order']))

    db.commit()
    flash(f'Template "{template["name"]}" applied to {client["full_name"]}!', 'success')
    return redirect(url_for('view_client', client_id=client_id))

@app.route('/trainer/programs/<int:program_id>/copy/<int:target_client_id>', methods=['POST'])
@login_required
@trainer_required
def copy_program(program_id, target_client_id):
    db = get_db()

    # Get original program
    program = db.execute('''
        SELECT p.* FROM programs p
        JOIN clients c ON p.client_id = c.client_id
        WHERE p.id = ? AND c.trainer_id = ?
    ''', (program_id, session['user_id'])).fetchone()

    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    # Verify target client belongs to trainer
    target_client = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ? AND u.id = ?
    ''', (session['user_id'], target_client_id)).fetchone()

    if not target_client:
        flash('Target client not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    # Create copy of program
    cursor = db.execute('''
        INSERT INTO programs (client_id, created_by, name, description)
        VALUES (?, ?, ?, ?)
    ''', (target_client_id, session['user_id'],
          f"{program['name']} (Copy)", program['description']))
    new_program_id = cursor.lastrowid

    # Copy exercises
    exercises = db.execute('''
        SELECT * FROM exercises
        WHERE program_id = ?
        ORDER BY exercise_order
    ''', (program_id,)).fetchall()

    for ex in exercises:
        db.execute('''
            INSERT INTO exercises (program_id, name, sets, reps, notes, exercise_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (new_program_id, ex['name'], ex['sets'], ex['reps'], ex['notes'], ex['exercise_order']))

    db.commit()
    flash(f'Program copied to {target_client["full_name"]}!', 'success')
    return redirect(url_for('view_client', client_id=target_client_id))

@app.route('/trainer/programs/<int:program_id>/bulk-edit', methods=['GET', 'POST'])
@login_required
@trainer_required
def bulk_edit_program(program_id):
    db = get_db()

    # Verify program belongs to trainer's client
    program = db.execute('''
        SELECT p.* FROM programs p
        JOIN clients c ON p.client_id = c.client_id
        WHERE p.id = ? AND c.trainer_id = ?
    ''', (program_id, session['user_id'])).fetchone()

    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('trainer_dashboard'))

    if request.method == 'POST':
        # Update program details
        program_name = request.form['name']
        program_description = request.form['description']

        db.execute('''
            UPDATE programs SET name = ?, description = ?
            WHERE id = ?
        ''', (program_name, program_description, program_id))

        # Delete all existing exercises
        db.execute('DELETE FROM exercises WHERE program_id = ?', (program_id,))

        # Add new exercises
        exercise_names = request.form.getlist('exercise_name[]')
        exercise_sets = request.form.getlist('exercise_sets[]')
        exercise_reps = request.form.getlist('exercise_reps[]')
        exercise_notes = request.form.getlist('exercise_notes[]')

        for i, name in enumerate(exercise_names):
            if name.strip():
                db.execute('''
                    INSERT INTO exercises (program_id, name, sets, reps, notes, exercise_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (program_id, name, exercise_sets[i], exercise_reps[i], exercise_notes[i], i + 1))

        db.commit()
        flash('Program updated successfully!', 'success')
        return redirect(url_for('view_program', program_id=program_id))

    # Get current exercises
    exercises = db.execute('''
        SELECT * FROM exercises
        WHERE program_id = ?
        ORDER BY exercise_order
    ''', (program_id,)).fetchall()

    return render_template('bulk_edit_program.html', program=program, exercises=exercises)

# API endpoint for getting clients
@app.route('/api/trainer/clients')
@login_required
@trainer_required
def get_trainer_clients():
    db = get_db()
    clients = db.execute('''
        SELECT u.id, u.full_name
        FROM users u
        JOIN clients c ON u.id = c.client_id
        WHERE c.trainer_id = ?
        ORDER BY u.full_name
    ''', (session['user_id'],)).fetchall()

    return jsonify([{'id': c['id'], 'name': c['full_name']} for c in clients])

# Initialize database on module load (works with both direct run and gunicorn)
def initialize_database():
    """Initialize database if needed - runs on module import"""
    try:
        db_url = os.environ.get('DATABASE_URL')

        if db_url and 'postgres' in db_url:
            # PostgreSQL: Check if ALL required tables exist
            try:
                db = get_db()
                cursor = db.cursor()
                # Check for a table that should exist if schema is complete
                cursor.execute("SELECT COUNT(*) FROM program_templates")
                print("✅ Database tables already exist (including program_templates)")
            except Exception as e:
                print(f"📊 Initializing PostgreSQL database... (error was: {str(e)[:100]})")
                # Drop all tables and recreate from scratch
                try:
                    print("🗑️  Dropping existing tables to start fresh...")
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("""
                        DROP SCHEMA public CASCADE;
                        CREATE SCHEMA public;
                        GRANT ALL ON SCHEMA public TO postgres;
                        GRANT ALL ON SCHEMA public TO public;
                    """)
                    db.commit()
                    print("✅ Schema reset complete")
                except Exception as drop_error:
                    print(f"⚠️  Schema reset failed (might be okay): {drop_error}")

                try:
                    init_db()
                    print("✅ Database initialized successfully!")
                except Exception as init_error:
                    print(f"❌ Database initialization failed: {init_error}")
                    raise
        else:
            # SQLite: Initialize if file doesn't exist
            if not os.path.exists(app.config['DATABASE']):
                print("📊 Initializing SQLite database...")
                init_db()
                print("✅ Database initialized")

        # Auto-populate database with exercises and templates if needed
        auto_populate_db()
    except Exception as e:
        print(f"❌ CRITICAL: Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise - let app start anyway so we can see error logs

# Run initialization when module is imported
print("🚀 Starting app initialization...")
initialize_database()
print("🚀 App initialization complete")

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    app.run(debug=debug, host='0.0.0.0', port=port)
