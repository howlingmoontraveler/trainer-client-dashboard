#!/usr/bin/env python3
"""
Simple script to run in Render shell - just copy and paste this entire file
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
    ('Hollow Hold', 'Bodyweight', 'Isometric core exercise', 'Lie on back, lift shoulders and legs, hold position', 'Core, Hip Flexors', 'None', 'intermediate', 1),
    ('RDL', 'Weight Training', 'Romanian Deadlift - hip hinge movement', 'Stand with feet hip-width apart, hinge at hips while lowering weight, return to standing', 'Hamstrings, Glutes, Lower Back', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Goblet Squat', 'Weight Training', 'Squat holding weight at chest', 'Hold dumbbell or kettlebell at chest, squat down keeping weight close to body', 'Quadriceps, Glutes, Hamstrings, Core', 'Dumbbell, Kettlebell', 'beginner', 1),
    ('Inverted Row', 'Bodyweight', 'Horizontal bodyweight row', 'Lie under bar, pull chest to bar', 'Lats, Rhomboids, Middle Traps, Biceps', 'Bar, TRX', 'intermediate', 1),
    ('Leg Press', 'Weight Training', 'Machine leg exercise', 'Sit in leg press machine, press weight with legs', 'Quadriceps, Glutes', 'Leg Press Machine', 'beginner', 1),
    ('Calf Raises', 'Bodyweight', 'Calf muscle exercise', 'Stand on edge of step, raise up on toes', 'Calves', 'Step, Platform', 'beginner', 1),
    ('Front Squat', 'Weight Training', 'Squat with barbell in front position', 'Hold barbell in front rack position, squat down keeping elbows up, return to standing', 'Quadriceps, Glutes, Hamstrings, Core, Upper Back', 'Barbell, Squat Rack', 'intermediate', 1),
    ('Split Squat', 'Bodyweight', 'Single leg squat with rear foot elevated', 'Place rear foot on bench, squat down with front leg, return to standing', 'Quadriceps, Glutes, Hamstrings', 'Bench', 'intermediate', 1),
    ('Walking Lunge', 'Bodyweight', 'Lunges while moving forward', 'Step forward into lunge, push off front leg to next lunge', 'Quadriceps, Glutes, Hamstrings', 'None', 'intermediate', 1),
    ('Box Jump', 'Plyometric', 'Explosive jumping exercise', 'Jump onto box, step down, repeat', 'Quadriceps, Glutes, Calves', 'Box, Platform', 'intermediate', 1),
    ('Kettlebell Swing', 'Weight Training', 'Hip hinge with kettlebell', 'Swing kettlebell from between legs to chest level', 'Hamstrings, Glutes, Core', 'Kettlebell', 'intermediate', 1)
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

routes_to_add = '''

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

# Read current app.py
with open('app.py', 'r') as f:
    app_content = f.read()

# Add routes before the if __name__ == '__main__' line
if 'if __name__ == \'__main__\':' in app_content:
    app_content = app_content.replace('if __name__ == \'__main__\':', routes_to_add + '\nif __name__ == \'__main__\':')
    
    # Write back to app.py
    with open('app.py', 'w') as f:
        f.write(app_content)
    
    print("✅ Added exercises routes to app.py!")
else:
    print("❌ Could not find the right place to add routes in app.py")

print("🎯 Exercises feature setup complete!")
print("🚀 Your exercises should now be available at /trainer/exercises")
print("💡 Make sure to restart your app if needed")
