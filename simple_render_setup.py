#!/usr/bin/env python3
"""
Simple setup script for Render - just run this one file
"""
import sqlite3
import os

print("🚀 Setting up exercises feature...")

# Step 1: Create database and add exercises
print("📊 Creating exercise database...")
conn = sqlite3.connect('trainer_dashboard.db')
cursor = conn.cursor()

# Create table
cursor.execute("DROP TABLE IF EXISTS exercise_library")
cursor.execute('''
    CREATE TABLE exercise_library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        description TEXT,
        instructions TEXT,
        muscle_groups TEXT,
        equipment TEXT,
        difficulty_level TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Add exercises
exercises = [
    ('Back Squat', 'Weight Training', 'Fundamental squat movement with barbell on back', 'Stand with feet shoulder-width apart, barbell on upper back, squat down keeping chest up, return to standing', 'Quadriceps, Glutes, Hamstrings, Core', 'Barbell, Squat Rack', 'intermediate', 1),
    ('Bodyweight Squat', 'Bodyweight', 'Basic squat without external weight', 'Stand with feet shoulder-width apart, squat down as if sitting in a chair, return to standing', 'Quadriceps, Glutes, Hamstrings', 'None', 'beginner', 1),
    ('Push-up', 'Bodyweight', 'Classic bodyweight pushing exercise', 'Start in plank position, lower chest to ground, push back up', 'Chest, Shoulders, Triceps', 'None', 'beginner', 1),
    ('Pull-up', 'Bodyweight', 'Vertical pulling exercise', 'Hang from bar, pull body up until chin over bar', 'Lats, Biceps, Rear Delts', 'Pull-up Bar', 'intermediate', 1),
    ('Deadlift', 'Weight Training', 'Hip hinge movement with weights', 'Stand with feet hip-width apart, hinge at hips while lowering weight, return to standing', 'Hamstrings, Glutes, Lower Back', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Bench Press', 'Weight Training', 'Horizontal pushing exercise', 'Lie on bench, lower bar to chest, press up', 'Chest, Shoulders, Triceps', 'Barbell, Bench', 'intermediate', 1),
    ('Overhead Press', 'Weight Training', 'Vertical pushing exercise', 'Press weight from shoulders to overhead', 'Shoulders, Triceps, Core', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Barbell Row', 'Weight Training', 'Horizontal pulling exercise', 'Bend over, pull bar to lower chest/upper abdomen', 'Lats, Rhomboids, Middle Traps, Biceps', 'Barbell', 'intermediate', 1),
    ('Dips', 'Bodyweight', 'Vertical pushing exercise', 'Support body on bars, lower until shoulders below elbows, push up', 'Chest, Shoulders, Triceps', 'Dip Bars', 'intermediate', 1),
    ('Hollow Hold', 'Bodyweight', 'Isometric core exercise', 'Lie on back, lift shoulders and legs, hold position', 'Core, Hip Flexors', 'None', 'intermediate', 1)
]

cursor.executemany('''
    INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', exercises)

conn.commit()
conn.close()
print(f"✅ Added {len(exercises)} exercises to database!")

# Step 2: Add routes to app.py
print("🔧 Adding exercises routes to app.py...")

# Read current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Check if routes already exist
if 'exercises_list' in content:
    print("⚠️  Exercises routes already exist in app.py")
else:
    # Add routes before the if __name__ == '__main__' line
    routes = '''

# Exercise Library Routes
@app.route('/trainer/exercises')
@login_required
@trainer_required
def exercises_list():
    db = get_db()
    exercises = db.execute('SELECT * FROM exercise_library ORDER BY name').fetchall()
    return render_template('simple_exercises_list.html', exercises=exercises, categories=[], current_category='', current_difficulty='', current_search='')

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
    
    return render_template('simple_create_exercise.html')

@app.route('/trainer/exercises/<int:exercise_id>')
@login_required
@trainer_required
def view_exercise(exercise_id):
    db = get_db()
    exercise = db.execute('SELECT * FROM exercise_library WHERE id = ?', (exercise_id,)).fetchone()
    
    if not exercise:
        flash('Exercise not found.', 'error')
        return redirect(url_for('exercises_list'))
    
    return render_template('simple_view_exercise.html', exercise=exercise)

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
    
    return render_template('simple_edit_exercise.html', exercise=exercise)
'''

    # Find the right place to insert
    if 'if __name__ == \'__main__\':' in content:
        content = content.replace('if __name__ == \'__main__\':', routes + '\nif __name__ == \'__main__\':')
        
        # Write back to app.py
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Added exercises routes to app.py!")
    else:
        print("❌ Could not find the right place to add routes in app.py")

# Step 3: Create templates directory
print("📁 Creating templates directory...")
os.makedirs('templates', exist_ok=True)

# Create simple exercises list template
exercises_list_template = '''{% extends "base.html" %}
{% block title %}Exercise Library{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Exercise Library</h1>
    <a href="{{ url_for('create_exercise') }}" class="btn btn-primary">Add New Exercise</a>
</div>
<div class="exercises-list">
    {% for exercise in exercises %}
    <div class="exercise-item">
        <h3>{{ exercise.name }}</h3>
        <div class="exercise-info">
            <span class="category">{{ exercise.category or 'Uncategorized' }}</span>
            <span class="difficulty">{{ exercise.difficulty_level.title() }}</span>
        </div>
        {% if exercise.description %}
        <p>{{ exercise.description }}</p>
        {% endif %}
        <div class="exercise-actions">
            <a href="{{ url_for('view_exercise', exercise_id=exercise.id) }}" class="btn btn-sm">View</a>
            <a href="{{ url_for('edit_exercise', exercise_id=exercise.id) }}" class="btn btn-sm">Edit</a>
        </div>
    </div>
    {% endfor %}
</div>
<style>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.exercises-list { display: grid; gap: 1rem; }
.exercise-item { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.exercise-item h3 { margin: 0 0 1rem 0; color: #333; }
.exercise-info { display: flex; gap: 1rem; margin-bottom: 1rem; }
.category, .difficulty { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; font-weight: 600; }
.category { background: #e3f2fd; color: #1976d2; }
.difficulty { background: #f3e5f5; color: #7b1fa2; }
.exercise-actions { display: flex; gap: 0.5rem; margin-top: 1rem; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; text-decoration: none; font-weight: 600; cursor: pointer; }
.btn-primary { background: #007bff; color: white; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.875rem; background: #6c757d; color: white; }
</style>
{% endblock %}'''

with open('templates/simple_exercises_list.html', 'w') as f:
    f.write(exercises_list_template)

# Create simple create exercise template
create_template = '''{% extends "base.html" %}
{% block title %}Create Exercise{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Create New Exercise</h1>
    <a href="{{ url_for('exercises_list') }}" class="btn btn-outline">Back to Exercises</a>
</div>
<form method="POST" class="exercise-form">
    <div class="form-group">
        <label for="name">Exercise Name *</label>
        <input type="text" id="name" name="name" required placeholder="e.g., Push-ups">
    </div>
    <div class="form-row">
        <div class="form-group">
            <label for="category">Category</label>
            <select id="category" name="category">
                <option value="">Select Category</option>
                <option value="Bodyweight">Bodyweight</option>
                <option value="Weight Training">Weight Training</option>
                <option value="Cardio">Cardio</option>
                <option value="Flexibility">Flexibility</option>
            </select>
        </div>
        <div class="form-group">
            <label for="difficulty_level">Difficulty Level *</label>
            <select id="difficulty_level" name="difficulty_level" required>
                <option value="">Select Difficulty</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
            </select>
        </div>
    </div>
    <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" name="description" rows="3" placeholder="Brief description of the exercise"></textarea>
    </div>
    <div class="form-group">
        <label for="instructions">Instructions</label>
        <textarea id="instructions" name="instructions" rows="4" placeholder="Step-by-step instructions for performing the exercise"></textarea>
    </div>
    <div class="form-row">
        <div class="form-group">
            <label for="muscle_groups">Muscle Groups</label>
            <input type="text" id="muscle_groups" name="muscle_groups" placeholder="e.g., Chest, Shoulders, Triceps">
        </div>
        <div class="form-group">
            <label for="equipment">Equipment</label>
            <input type="text" id="equipment" name="equipment" placeholder="e.g., Barbell, Dumbbells, None">
        </div>
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Create Exercise</button>
        <a href="{{ url_for('exercises_list') }}" class="btn btn-outline">Cancel</a>
    </div>
</form>
<style>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.exercise-form { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 800px; }
.form-group { margin-bottom: 1.5rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.5rem; color: #495057; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ced4da; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e9ecef; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 4px; text-decoration: none; font-weight: 600; cursor: pointer; display: inline-block; }
.btn-primary { background: #007bff; color: white; }
.btn-outline { background: transparent; color: #6c757d; border: 1px solid #6c757d; }
</style>
{% endblock %}'''

with open('templates/simple_create_exercise.html', 'w') as f:
    f.write(create_template)

# Create simple view exercise template
view_template = '''{% extends "base.html" %}
{% block title %}{{ exercise.name }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>{{ exercise.name }}</h1>
    <div class="header-actions">
        <a href="{{ url_for('edit_exercise', exercise_id=exercise.id) }}" class="btn btn-secondary">Edit</a>
        <a href="{{ url_for('exercises_list') }}" class="btn btn-outline">Back to Exercises</a>
    </div>
</div>
<div class="exercise-detail">
    <div class="exercise-badges">
        {% if exercise.category %}
        <span class="badge category">{{ exercise.category }}</span>
        {% endif %}
        <span class="badge difficulty">{{ exercise.difficulty_level.title() }}</span>
    </div>
    {% if exercise.description %}
    <div class="info-section">
        <h3>Description</h3>
        <p>{{ exercise.description }}</p>
    </div>
    {% endif %}
    {% if exercise.instructions %}
    <div class="info-section">
        <h3>Instructions</h3>
        <div class="instructions">{{ exercise.instructions | replace('\n', '<br>') | safe }}</div>
    </div>
    {% endif %}
    <div class="exercise-details">
        {% if exercise.muscle_groups %}
        <div class="detail-item">
            <h4>Muscle Groups</h4>
            <p>{{ exercise.muscle_groups }}</p>
        </div>
        {% endif %}
        {% if exercise.equipment %}
        <div class="detail-item">
            <h4>Equipment</h4>
            <p>{{ exercise.equipment }}</p>
        </div>
        {% endif %}
    </div>
</div>
<style>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.header-actions { display: flex; gap: 1rem; }
.exercise-detail { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 2rem; }
.exercise-badges { display: flex; gap: 0.75rem; margin-bottom: 2rem; }
.badge { padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.875rem; font-weight: 600; }
.badge.category { background: #e3f2fd; color: #1976d2; }
.badge.difficulty { background: #f3e5f5; color: #7b1fa2; }
.info-section { margin-bottom: 2rem; }
.info-section h3 { color: #495057; margin-bottom: 1rem; }
.instructions { background: #f8f9fa; padding: 1.5rem; border-radius: 6px; border-left: 4px solid #007bff; line-height: 1.6; }
.exercise-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
.detail-item { background: #f8f9fa; padding: 1.5rem; border-radius: 6px; }
.detail-item h4 { color: #495057; margin-bottom: 0.75rem; font-size: 1rem; font-weight: 600; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 4px; text-decoration: none; font-weight: 600; cursor: pointer; display: inline-block; }
.btn-secondary { background: #6c757d; color: white; }
.btn-outline { background: transparent; color: #6c757d; border: 1px solid #6c757d; }
</style>
{% endblock %}'''

with open('templates/simple_view_exercise.html', 'w') as f:
    f.write(view_template)

# Create simple edit exercise template
edit_template = '''{% extends "base.html" %}
{% block title %}Edit {{ exercise.name }}{% endblock %}
{% block content %}
<div class="page-header">
    <h1>Edit Exercise</h1>
    <div class="header-actions">
        <a href="{{ url_for('view_exercise', exercise_id=exercise.id) }}" class="btn btn-outline">View Exercise</a>
        <a href="{{ url_for('exercises_list') }}" class="btn btn-outline">Back to Exercises</a>
    </div>
</div>
<form method="POST" class="exercise-form">
    <div class="form-group">
        <label for="name">Exercise Name *</label>
        <input type="text" id="name" name="name" required value="{{ exercise.name }}" placeholder="e.g., Push-ups">
    </div>
    <div class="form-row">
        <div class="form-group">
            <label for="category">Category</label>
            <select id="category" name="category">
                <option value="">Select Category</option>
                <option value="Bodyweight" {% if exercise.category == 'Bodyweight' %}selected{% endif %}>Bodyweight</option>
                <option value="Weight Training" {% if exercise.category == 'Weight Training' %}selected{% endif %}>Weight Training</option>
                <option value="Cardio" {% if exercise.category == 'Cardio' %}selected{% endif %}>Cardio</option>
                <option value="Flexibility" {% if exercise.category == 'Flexibility' %}selected{% endif %}>Flexibility</option>
            </select>
        </div>
        <div class="form-group">
            <label for="difficulty_level">Difficulty Level *</label>
            <select id="difficulty_level" name="difficulty_level" required>
                <option value="">Select Difficulty</option>
                <option value="beginner" {% if exercise.difficulty_level == 'beginner' %}selected{% endif %}>Beginner</option>
                <option value="intermediate" {% if exercise.difficulty_level == 'intermediate' %}selected{% endif %}>Intermediate</option>
                <option value="advanced" {% if exercise.difficulty_level == 'advanced' %}selected{% endif %}>Advanced</option>
            </select>
        </div>
    </div>
    <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" name="description" rows="3" placeholder="Brief description of the exercise">{{ exercise.description or '' }}</textarea>
    </div>
    <div class="form-group">
        <label for="instructions">Instructions</label>
        <textarea id="instructions" name="instructions" rows="4" placeholder="Step-by-step instructions for performing the exercise">{{ exercise.instructions or '' }}</textarea>
    </div>
    <div class="form-row">
        <div class="form-group">
            <label for="muscle_groups">Muscle Groups</label>
            <input type="text" id="muscle_groups" name="muscle_groups" value="{{ exercise.muscle_groups or '' }}" placeholder="e.g., Chest, Shoulders, Triceps">
        </div>
        <div class="form-group">
            <label for="equipment">Equipment</label>
            <input type="text" id="equipment" name="equipment" value="{{ exercise.equipment or '' }}" placeholder="e.g., Barbell, Dumbbells, None">
        </div>
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Update Exercise</button>
        <a href="{{ url_for('view_exercise', exercise_id=exercise.id) }}" class="btn btn-outline">Cancel</a>
    </div>
</form>
<style>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.header-actions { display: flex; gap: 1rem; }
.exercise-form { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 800px; }
.form-group { margin-bottom: 1.5rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.5rem; color: #495057; }
.form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ced4da; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e9ecef; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 4px; text-decoration: none; font-weight: 600; cursor: pointer; display: inline-block; }
.btn-primary { background: #007bff; color: white; }
.btn-outline { background: transparent; color: #6c757d; border: 1px solid #6c757d; }
</style>
{% endblock %}'''

with open('templates/simple_edit_exercise.html', 'w') as f:
    f.write(edit_template)

print("✅ Created all template files!")
print("🎯 Exercises feature setup complete!")
print("🚀 Your exercises should now be available at /trainer/exercises")
print("💡 Make sure to restart your app if needed")

