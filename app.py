from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'trainer_dashboard.db'

# Database helper functions
def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

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
        flash('Program created successfully!', 'success')
        return redirect(url_for('view_client', client_id=client_id))

    # Get all exercises from library for dropdown
    exercises_library = db.execute('''
        SELECT id, name, category, equipment, description
        FROM exercise_library
        ORDER BY category, name
    ''').fetchall()

    return render_template('create_program.html', client=client, exercises_library=exercises_library)

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
        cursor = db.execute('''
            INSERT INTO exercise_library (name, category, equipment, description, is_custom, created_by)
            VALUES (?, ?, ?, ?, 1, ?)
        ''', (name, category, equipment, description, session['user_id']))
        db.commit()

        return jsonify({
            'success': True,
            'exercise': {
                'id': cursor.lastrowid,
                'name': name,
                'category': category,
                'equipment': equipment,
                'description': description
            }
        })
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Exercise already exists'}), 400

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    # Use PORT from environment (for Render) or default to 5000 for local
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
