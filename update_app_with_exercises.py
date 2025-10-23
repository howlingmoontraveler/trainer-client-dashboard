#!/usr/bin/env python3
"""
Update app.py with complete exercises system
"""
import re

print("🔧 Adding complete exercises system to app.py...")

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
    
    # Get filter parameters
    category = request.args.get('category', '')
    difficulty = request.args.get('difficulty', '')
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
    
    if search:
        query += ' AND (name LIKE ? OR description LIKE ? OR muscle_groups LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    query += ' ORDER BY name'
    
    exercises = db.execute(query, params).fetchall()
    
    # Get unique categories for filter
    categories = db.execute('SELECT DISTINCT category FROM exercise_library WHERE category IS NOT NULL ORDER BY category').fetchall()
    
    return render_template('exercises_list.html', exercises=exercises, categories=categories, 
                         current_category=category, current_difficulty=difficulty, current_search=search)

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

print("🎯 Exercises system added to app.py!")
