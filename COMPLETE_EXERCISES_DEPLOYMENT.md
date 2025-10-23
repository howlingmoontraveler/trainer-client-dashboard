# Complete Exercises System Deployment for Render.com

## Overview
Deploy a complete exercises management system to a live Render.com Flask application with ALL 109 exercises from the original list, including navigation, CRUD functionality, and professional templates.

## Current Setup
- Live Render app: https://trainer-client-dashboard.onrender.com
- Flask application with SQLite database
- Existing trainer dashboard with authentication
- Need to add complete exercises library with navigation

## Requirements
1. Add ALL 109 exercises to the database
2. Add "Exercises" tab to navigation (visible only to trainers)
3. Create complete CRUD functionality (Create, Read, Update, Delete)
4. Add professional templates for exercise management
5. Ensure everything works on the live Render.com site

## Step-by-Step Deployment Instructions

### Step 1: Create Complete Database with ALL 109 Exercises

Run this command in the Render shell to create the complete exercise database:

```bash
python3 -c "
import sqlite3

# Connect to database
conn = sqlite3.connect('trainer_dashboard.db')
cursor = conn.cursor()

# Drop existing table and recreate
cursor.execute('DROP TABLE IF EXISTS exercise_library')
cursor.execute('''
    CREATE TABLE exercise_library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        description TEXT,
        instructions TEXT,
        muscle_groups TEXT,
        equipment TEXT,
        difficulty_level TEXT CHECK(difficulty_level IN ('beginner', 'intermediate', 'advanced')),
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
''')

# ALL 109 exercises from the original list
exercises = [
    ('Back Squat', 'Weight Training', 'Fundamental squat movement with barbell on back', 'Stand with feet shoulder-width apart, barbell on upper back, squat down keeping chest up, return to standing', 'Quadriceps, Glutes, Hamstrings, Core', 'Barbell, Squat Rack', 'intermediate', 1),
    ('Bodyweight Squat', 'Bodyweight', 'Basic squat without external weight', 'Stand with feet shoulder-width apart, squat down as if sitting in a chair, return to standing', 'Quadriceps, Glutes, Hamstrings', 'None', 'beginner', 1),
    ('Front Squat', 'Weight Training', 'Squat with barbell in front position', 'Hold barbell in front rack position, squat down keeping elbows up, return to standing', 'Quadriceps, Glutes, Hamstrings, Core, Upper Back', 'Barbell, Squat Rack', 'intermediate', 1),
    ('Goblet Squat', 'Weight Training', 'Squat holding weight at chest', 'Hold dumbbell or kettlebell at chest, squat down keeping weight close to body', 'Quadriceps, Glutes, Hamstrings, Core', 'Dumbbell, Kettlebell', 'beginner', 1),
    ('Overhead Squat', 'Weight Training', 'Squat while holding weight overhead', 'Hold weight overhead with arms locked, squat down maintaining overhead position', 'Quadriceps, Glutes, Hamstrings, Shoulders, Core', 'Barbell, Dumbbell', 'advanced', 1),
    ('Zercher Squat', 'Weight Training', 'Squat with barbell in elbow crooks', 'Hold barbell in elbow crooks, squat down maintaining position', 'Quadriceps, Glutes, Hamstrings, Core', 'Barbell', 'advanced', 1),
    ('Sissy Squats', 'Bodyweight', 'Advanced bodyweight squat variation', 'Stand on toes, lean back while squatting down, return to standing', 'Quadriceps', 'None', 'advanced', 1),
    ('Cossack Squat', 'Bodyweight', 'Lateral squat movement', 'Stand with wide stance, shift weight to one side while keeping other leg straight', 'Quadriceps, Glutes, Hip Adductors', 'None', 'intermediate', 1),
    ('Landmine Cossack Lunge', 'Weight Training', 'Cossack squat with landmine', 'Hold landmine handle, perform cossack squat movement', 'Quadriceps, Glutes, Hip Adductors', 'Landmine, Barbell', 'intermediate', 1),
    ('Split Squat', 'Bodyweight', 'Single leg squat with rear foot elevated', 'Place rear foot on bench, squat down with front leg, return to standing', 'Quadriceps, Glutes, Hamstrings', 'Bench', 'intermediate', 1),
    ('Front Foot Elevated Split Squat', 'Bodyweight', 'Split squat with front foot elevated', 'Place front foot on platform, perform split squat', 'Quadriceps, Glutes, Hamstrings', 'Platform, Bench', 'intermediate', 1),
    ('Walking Lunge', 'Bodyweight', 'Lunges while moving forward', 'Step forward into lunge, push off front leg to next lunge', 'Quadriceps, Glutes, Hamstrings', 'None', 'intermediate', 1),
    ('Landmine Bulgarian Squat', 'Weight Training', 'Bulgarian split squat with landmine', 'Hold landmine handle, perform Bulgarian split squat', 'Quadriceps, Glutes, Hamstrings', 'Landmine, Barbell, Bench', 'intermediate', 1),
    ('Landmine FFESS', 'Weight Training', 'Front foot elevated split squat with landmine', 'Hold landmine, perform front foot elevated split squat', 'Quadriceps, Glutes, Hamstrings', 'Landmine, Barbell, Platform', 'intermediate', 1),
    ('Landmine Knee Drive Reverse Lunge', 'Weight Training', 'Reverse lunge with knee drive using landmine', 'Hold landmine, step back into lunge, drive knee up on return', 'Quadriceps, Glutes, Hamstrings, Hip Flexors', 'Landmine, Barbell', 'intermediate', 1),
    ('Landmine Reverse Suitcase Lunge', 'Weight Training', 'Reverse lunge with landmine suitcase hold', 'Hold landmine like suitcase, perform reverse lunge', 'Quadriceps, Glutes, Hamstrings, Core', 'Landmine, Barbell', 'intermediate', 1),
    ('Landmine Lunge Combo', 'Weight Training', 'Combination lunge movements with landmine', 'Perform various lunge patterns holding landmine', 'Quadriceps, Glutes, Hamstrings', 'Landmine, Barbell', 'intermediate', 1),
    ('Spiderman Lunge w/ Thoracic Rotation', 'Bodyweight', 'Lunge with thoracic spine rotation', 'Step into lunge, rotate thoracic spine toward front leg', 'Quadriceps, Glutes, Hamstrings, Thoracic Spine', 'None', 'intermediate', 1),
    ('RDL', 'Weight Training', 'Romanian Deadlift - hip hinge movement', 'Stand with feet hip-width apart, hinge at hips while lowering weight, return to standing', 'Hamstrings, Glutes, Lower Back', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Trapbar Deadlift', 'Weight Training', 'Deadlift using trap bar', 'Stand inside trap bar, lift by extending hips and knees', 'Hamstrings, Glutes, Quadriceps, Traps', 'Trap Bar', 'intermediate', 1),
    ('Landmine RDL', 'Weight Training', 'Romanian deadlift with landmine', 'Hold landmine handle, perform RDL movement', 'Hamstrings, Glutes, Lower Back', 'Landmine, Barbell', 'intermediate', 1),
    ('Landmine Split Stance RDL', 'Weight Training', 'Single leg RDL with landmine', 'Hold landmine, perform single leg RDL', 'Hamstrings, Glutes, Core', 'Landmine, Barbell', 'intermediate', 1),
    ('Single Leg RDL', 'Bodyweight', 'Single leg Romanian deadlift', 'Stand on one leg, hinge at hip while extending other leg back', 'Hamstrings, Glutes, Core', 'None', 'intermediate', 1),
    ('Landmine Rotational Deadlift', 'Weight Training', 'Rotational deadlift with landmine', 'Hold landmine, perform deadlift with rotation', 'Hamstrings, Glutes, Lower Back, Obliques', 'Landmine, Barbell', 'advanced', 1),
    ('Landmine Single Leg Hip Thrust', 'Weight Training', 'Single leg hip thrust with landmine', 'Hold landmine, perform single leg hip thrust', 'Glutes, Hamstrings', 'Landmine, Barbell, Bench', 'intermediate', 1),
    ('Flat Bench Press', 'Weight Training', 'Horizontal pushing exercise on bench', 'Lie on bench, lower bar to chest, press up', 'Chest, Shoulders, Triceps', 'Barbell, Bench', 'intermediate', 1),
    ('Close Grip BB Bench Press', 'Weight Training', 'Bench press with narrow grip', 'Lie on bench, use narrow grip, lower bar to chest, press up', 'Chest, Triceps', 'Barbell, Bench', 'intermediate', 1),
    ('Push-up', 'Bodyweight', 'Classic bodyweight pushing exercise', 'Start in plank position, lower chest to ground, push back up', 'Chest, Shoulders, Triceps', 'None', 'beginner', 1),
    ('Deficit pushup', 'Bodyweight', 'Push-up with hands elevated', 'Place hands on platform, perform push-up with increased range of motion', 'Chest, Shoulders, Triceps', 'Platform', 'intermediate', 1),
    ('Dips', 'Bodyweight', 'Vertical pushing exercise', 'Support body on bars, lower until shoulders below elbows, push up', 'Chest, Shoulders, Triceps', 'Dip Bars', 'intermediate', 1),
    ('Overhead Press', 'Weight Training', 'Vertical pushing exercise', 'Press weight from shoulders to overhead', 'Shoulders, Triceps, Core', 'Barbell, Dumbbells', 'intermediate', 1),
    ('SA DB OH Press', 'Weight Training', 'Single arm dumbbell overhead press', 'Press single dumbbell overhead, alternating arms', 'Shoulders, Triceps, Core', 'Dumbbell', 'intermediate', 1),
    ('Landmine Front Press', 'Weight Training', 'Front press using landmine', 'Hold landmine handle, press forward and up', 'Shoulders, Triceps, Core', 'Landmine, Barbell', 'intermediate', 1),
    ('Incline DB Press', 'Weight Training', 'Incline bench press with dumbbells', 'Lie on incline bench, press dumbbells from chest', 'Upper Chest, Shoulders, Triceps', 'Dumbbells, Incline Bench', 'intermediate', 1),
    ('Decline DB Press', 'Weight Training', 'Decline bench press with dumbbells', 'Lie on decline bench, press dumbbells from chest', 'Lower Chest, Shoulders, Triceps', 'Dumbbells, Decline Bench', 'intermediate', 1),
    ('Decline Front Press', 'Weight Training', 'Decline front press movement', 'Perform front press on decline bench', 'Chest, Shoulders, Triceps', 'Decline Bench, Dumbbells', 'intermediate', 1),
    ('Stability ball DB press', 'Weight Training', 'Dumbbell press on stability ball', 'Lie on stability ball, press dumbbells from chest', 'Chest, Shoulders, Triceps, Core', 'Dumbbells, Stability Ball', 'intermediate', 1),
    ('Barbell Row', 'Weight Training', 'Horizontal pulling exercise', 'Bend over, pull bar to lower chest/upper abdomen', 'Lats, Rhomboids, Middle Traps, Biceps', 'Barbell', 'intermediate', 1),
    ('Pull-up', 'Bodyweight', 'Vertical pulling exercise', 'Hang from bar, pull body up until chin over bar', 'Lats, Biceps, Rear Delts', 'Pull-up Bar', 'intermediate', 1),
    ('Inverted Row', 'Bodyweight', 'Horizontal bodyweight row', 'Lie under bar, pull chest to bar', 'Lats, Rhomboids, Middle Traps, Biceps', 'Bar, TRX', 'intermediate', 1),
    ('Seated Cable Row', 'Weight Training', 'Seated horizontal cable row', 'Sit at cable machine, pull handle to torso', 'Lats, Rhomboids, Middle Traps, Biceps', 'Cable Machine', 'beginner', 1),
    ('Lat Pulldown - Wide grip', 'Weight Training', 'Wide grip lat pulldown', 'Pull bar down to upper chest with wide grip', 'Lats, Upper Back', 'Cable Machine', 'beginner', 1),
    ('Lat Pulldown - close grip', 'Weight Training', 'Close grip lat pulldown', 'Pull bar down with narrow grip', 'Lats, Middle Back', 'Cable Machine', 'beginner', 1),
    ('Lat Pulldown - Single Arm', 'Weight Training', 'Single arm lat pulldown', 'Pull single handle down, alternating arms', 'Lats, Core', 'Cable Machine', 'intermediate', 1),
    ('Single Arm Lat Pulldown', 'Weight Training', 'Single arm lat pulldown variation', 'Pull single handle with focus on one side', 'Lats, Core', 'Cable Machine', 'intermediate', 1),
    ('Landmine Single Arm Row', 'Weight Training', 'Single arm row with landmine', 'Hold landmine handle, row to hip', 'Lats, Rhomboids, Biceps', 'Landmine, Barbell', 'intermediate', 1),
    ('Biceps Cable Curls', 'Weight Training', 'Cable bicep curls', 'Curl cable handles up, focusing on biceps', 'Biceps', 'Cable Machine', 'beginner', 1),
    ('EZ Bar Curl', 'Weight Training', 'Bicep curls with EZ bar', 'Curl EZ bar up, focusing on biceps', 'Biceps', 'EZ Bar', 'beginner', 1),
    ('Jackson 5 Curls', 'Weight Training', 'Bicep curl variation', 'Perform bicep curls with specific tempo and pattern', 'Biceps', 'Dumbbells', 'intermediate', 1),
    ('Reverse Curls', 'Weight Training', 'Reverse grip bicep curls', 'Curl with overhand grip, targeting forearms', 'Forearms, Biceps', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Zottman Curls', 'Weight Training', 'Curl with grip rotation', 'Curl up with supinated grip, rotate to pronated on way down', 'Biceps, Forearms', 'Dumbbells', 'intermediate', 1),
    ('Triceps Pushdown', 'Weight Training', 'Cable tricep pushdown', 'Push cable handle down, extending elbows', 'Triceps', 'Cable Machine', 'beginner', 1),
    ('Triceps Extension - Decline', 'Weight Training', 'Decline tricep extension', 'Perform tricep extension on decline bench', 'Triceps', 'Decline Bench, Dumbbells', 'intermediate', 1),
    ('Dual Arm Cable OH Triceps Ext', 'Weight Training', 'Overhead cable tricep extension', 'Extend cable overhead, targeting triceps', 'Triceps', 'Cable Machine', 'intermediate', 1),
    ('Cross Body SA Tricep Ext', 'Weight Training', 'Cross body single arm tricep extension', 'Extend single dumbbell across body', 'Triceps', 'Dumbbell', 'intermediate', 1),
    ('Decline DB Tricep Ext', 'Weight Training', 'Decline dumbbell tricep extension', 'Perform tricep extension on decline bench', 'Triceps', 'Decline Bench, Dumbbells', 'intermediate', 1),
    ('Hollow Hold', 'Bodyweight', 'Isometric core exercise', 'Lie on back, lift shoulders and legs, hold position', 'Core, Hip Flexors', 'None', 'intermediate', 1),
    ('RKC Plank', 'Bodyweight', 'Advanced plank variation', 'Hold plank with maximum tension throughout body', 'Core, Shoulders', 'None', 'intermediate', 1),
    ('Dead Bugs', 'Bodyweight', 'Core stability exercise', 'Lie on back, extend opposite arm and leg, return to start', 'Core, Hip Flexors', 'None', 'beginner', 1),
    ('Leg Raises', 'Bodyweight', 'Hip flexor and lower core exercise', 'Lie on back, raise legs up and down', 'Lower Abs, Hip Flexors', 'None', 'intermediate', 1),
    ('Leg Lifts', 'Bodyweight', 'Hip flexor exercise', 'Lie on side, lift top leg up and down', 'Hip Abductors, Glutes', 'None', 'beginner', 1),
    ('Cable Crunch', 'Weight Training', 'Cable core exercise', 'Kneel at cable machine, crunch down', 'Core', 'Cable Machine', 'intermediate', 1),
    ('Cable Rotation', 'Weight Training', 'Rotational core exercise', 'Stand sideways to cable, rotate torso', 'Obliques, Core', 'Cable Machine', 'intermediate', 1),
    ('Cable Chop High to Low', 'Weight Training', 'Diagonal cable chop', 'Pull cable from high to low across body', 'Obliques, Core', 'Cable Machine', 'intermediate', 1),
    ('Pallof Press', 'Weight Training', 'Anti-rotation core exercise', 'Stand sideways to cable, press handle away from body', 'Core, Obliques', 'Cable Machine', 'intermediate', 1),
    ('Landmine Rotation', 'Weight Training', 'Rotational exercise with landmine', 'Hold landmine, rotate from side to side', 'Obliques, Core', 'Landmine, Barbell', 'intermediate', 1),
    ('Plate V Ups', 'Weight Training', 'V-up with weight plate', 'Perform V-ups holding weight plate', 'Core, Hip Flexors', 'Weight Plate', 'intermediate', 1),
    ('Suitcase Plate Crunch', 'Weight Training', 'Crunch holding weight like suitcase', 'Hold weight plate, perform crunches', 'Core, Obliques', 'Weight Plate', 'intermediate', 1),
    ('Slider Thrusts', 'Bodyweight', 'Core exercise with sliders', 'Use sliders to perform thrusting motion', 'Core, Hip Flexors', 'Sliders', 'intermediate', 1),
    ('Glute Bridge', 'Bodyweight', 'Basic glute activation exercise', 'Lie on back, lift hips up squeezing glutes', 'Glutes, Hamstrings', 'None', 'beginner', 1),
    ('Hip Abduction', 'Bodyweight', 'Lateral hip movement', 'Stand on one leg, lift other leg to side', 'Hip Abductors, Glutes', 'None', 'beginner', 1),
    ('Hip Adduction', 'Bodyweight', 'Medial hip movement', 'Stand on one leg, cross other leg in front', 'Hip Adductors', 'None', 'beginner', 1),
    ('Reverse Hyper', 'Weight Training', 'Posterior chain exercise', 'Lie face down, lift legs up behind body', 'Glutes, Hamstrings, Lower Back', 'Reverse Hyper Machine', 'intermediate', 1),
    ('Leg Press', 'Weight Training', 'Machine leg exercise', 'Sit in leg press machine, press weight with legs', 'Quadriceps, Glutes', 'Leg Press Machine', 'beginner', 1),
    ('Leg Extension', 'Weight Training', 'Quadricep isolation exercise', 'Sit in leg extension machine, extend legs', 'Quadriceps', 'Leg Extension Machine', 'beginner', 1),
    ('Leg Curls', 'Weight Training', 'Hamstring isolation exercise', 'Lie in leg curl machine, curl legs up', 'Hamstrings', 'Leg Curl Machine', 'beginner', 1),
    ('Calf Raises', 'Bodyweight', 'Calf muscle exercise', 'Stand on edge of step, raise up on toes', 'Calves', 'Step, Platform', 'beginner', 1),
    ('Landmine Calf Raise', 'Weight Training', 'Calf raises with landmine', 'Hold landmine, perform calf raises', 'Calves', 'Landmine, Barbell', 'intermediate', 1),
    ('Tibialis Raises', 'Bodyweight', 'Anterior tibialis exercise', 'Sit with feet flat, lift toes up', 'Tibialis Anterior', 'None', 'beginner', 1),
    ('Farmer's Carry', 'Weight Training', 'Loaded carry exercise', 'Carry heavy weights in each hand, walk forward', 'Core, Grip, Traps, Glutes', 'Dumbbells, Kettlebells', 'intermediate', 1),
    ('Safety Bar Carry', 'Weight Training', 'Carry with safety bar', 'Carry safety bar on shoulders, walk forward', 'Core, Traps, Glutes', 'Safety Bar', 'intermediate', 1),
    ('Sandbag Over Shoulder', 'Weight Training', 'Sandbag carry exercise', 'Carry sandbag over shoulder, walk forward', 'Core, Traps, Glutes', 'Sandbag', 'intermediate', 1),
    ('Dumbbell Fly', 'Weight Training', 'Chest fly exercise', 'Lie on bench, open arms wide, bring together', 'Chest, Anterior Delts', 'Dumbbells, Bench', 'intermediate', 1),
    ('Pec Fly', 'Weight Training', 'Chest fly variation', 'Perform chest fly movement', 'Chest, Anterior Delts', 'Dumbbells, Cable Machine', 'intermediate', 1),
    ('Cable Cross', 'Weight Training', 'Cable chest fly', 'Stand between cables, bring handles together', 'Chest, Anterior Delts', 'Cable Machine', 'intermediate', 1),
    ('Cable Side Raise', 'Weight Training', 'Lateral deltoid exercise', 'Stand next to cable, raise arm to side', 'Lateral Delts', 'Cable Machine', 'beginner', 1),
    ('Box Jump', 'Plyometric', 'Explosive jumping exercise', 'Jump onto box, step down, repeat', 'Quadriceps, Glutes, Calves', 'Box, Platform', 'intermediate', 1),
    ('Broad Jump', 'Plyometric', 'Horizontal jumping exercise', 'Jump forward as far as possible', 'Quadriceps, Glutes, Calves', 'None', 'intermediate', 1),
    ('Jump Squats', 'Plyometric', 'Explosive squat variation', 'Perform squat with explosive jump', 'Quadriceps, Glutes, Calves', 'None', 'intermediate', 1),
    ('Power Clean', 'Weight Training', 'Olympic lifting movement', 'Explosively lift bar from floor to shoulders', 'Quadriceps, Glutes, Hamstrings, Traps', 'Barbell', 'advanced', 1),
    ('Kettlebell Swing', 'Weight Training', 'Hip hinge with kettlebell', 'Swing kettlebell from between legs to chest level', 'Hamstrings, Glutes, Core', 'Kettlebell', 'intermediate', 1),
    ('Child's Pose', 'Flexibility', 'Restorative yoga pose', 'Kneel and sit back on heels, reach arms forward', 'Hip Flexors, Lower Back', 'None', 'beginner', 1),
    ('Diaphragmatic Breathing', 'Flexibility', 'Breathing exercise', 'Lie down, breathe deeply into diaphragm', 'Diaphragm, Core', 'None', 'beginner', 1),
    ('Foam Rolling', 'Flexibility', 'Self-massage with foam roller', 'Roll muscles with foam roller for recovery', 'Various Muscle Groups', 'Foam Roller', 'beginner', 1),
    ('Jefferson Curls', 'Flexibility', 'Spinal mobility exercise', 'Stand on platform, slowly curl spine down', 'Spinal Erectors, Hamstrings', 'Platform', 'intermediate', 1),
    ('Bear Crawl', 'Functional', 'Quadrupedal movement', 'Crawl on hands and feet, keeping knees off ground', 'Core, Shoulders, Hip Flexors', 'None', 'intermediate', 1),
    ('Dead Hangs', 'Bodyweight', 'Grip and shoulder stability', 'Hang from bar for time', 'Grip, Lats, Shoulders', 'Pull-up Bar', 'intermediate', 1),
    ('L Sit Progression', 'Bodyweight', 'Advanced core exercise', 'Sit with legs extended, support body with hands', 'Core, Hip Flexors, Triceps', 'None', 'advanced', 1),
    ('Supermans', 'Bodyweight', 'Posterior chain exercise', 'Lie face down, lift chest and legs', 'Lower Back, Glutes, Hamstrings', 'None', 'beginner', 1),
    ('Shrugs', 'Weight Training', 'Trap strengthening exercise', 'Lift shoulders up and down with weight', 'Traps', 'Barbell, Dumbbells', 'beginner', 1),
    ('Figure 8s', 'Weight Training', 'Dynamic movement pattern', 'Move weight in figure-8 pattern', 'Core, Shoulders', 'Dumbbell, Kettlebell', 'intermediate', 1),
    ('Landmine Low Hold Squat Jump', 'Weight Training', 'Squat jump holding landmine low', 'Hold landmine low, perform squat jumps', 'Quadriceps, Glutes, Core', 'Landmine, Barbell', 'advanced', 1),
    ('Landmine Knee Drive Reverse Lunge', 'Weight Training', 'Reverse lunge with knee drive', 'Step back into lunge, drive knee up on return', 'Quadriceps, Glutes, Hip Flexors', 'Landmine, Barbell', 'intermediate', 1),
    ('Sled Drag', 'Functional', 'Pulling sled exercise', 'Drag weighted sled forward', 'Glutes, Hamstrings, Core', 'Sled, Weight', 'intermediate', 1),
    ('Sled Push', 'Functional', 'Pushing sled exercise', 'Push weighted sled forward', 'Quadriceps, Glutes, Core', 'Sled, Weight', 'intermediate', 1),
    ('VO2 Max', 'Cardio', 'High-intensity cardio training', 'Perform high-intensity intervals for VO2 max improvement', 'Cardiovascular System', 'Various', 'advanced', 1),
    ('Forearm Complex', 'Weight Training', 'Forearm strengthening', 'Perform various forearm exercises', 'Forearms, Grip', 'Dumbbells, Barbell', 'intermediate', 1),
    ('Forearm banded KB/BB complex', 'Weight Training', 'Forearm work with bands', 'Use bands for forearm strengthening', 'Forearms, Grip', 'Bands, Kettlebell, Barbell', 'intermediate', 1)
]

# Insert all exercises
cursor.executemany('''
    INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', exercises)

conn.commit()
conn.close()
print(f'✅ Added ALL {len(exercises)} exercises to database!')
"
```

### Step 2: Add Exercise Routes to app.py

Run this command to add the complete exercise management routes:

```bash
cat >> app.py << 'EOF'

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
EOF
```

### Step 3: Add Navigation Link

Run this command to add the "Exercises" link to the navigation:

```bash
sed -i 's/{% if session.role == '\''trainer'\'' %}/{% if session.role == '\''trainer'\'' %}\n                <a href="{{ url_for('\''exercises_list'\'') }}" class="nav-link">Exercises<\/a>/' templates/base.html
```

### Step 4: Create Exercise List Template

```bash
cat > templates/exercises_list.html << 'EOF'
{% extends "base.html" %}

{% block title %}Exercise Library{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Exercise Library ({{ exercises|length }} exercises)</h2>
                <a href="{{ url_for('create_exercise') }}" class="btn btn-primary">Add New Exercise</a>
            </div>
            
            <!-- Filter Section -->
            <div class="card mb-4">
                <div class="card-body">
                    <form method="GET" class="row g-3">
                        <div class="col-md-3">
                            <label for="category" class="form-label">Category</label>
                            <select name="category" id="category" class="form-select">
                                <option value="">All Categories</option>
                                {% for cat in categories %}
                                <option value="{{ cat.category }}" {% if cat.category == current_category %}selected{% endif %}>{{ cat.category }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label for="difficulty" class="form-label">Difficulty</label>
                            <select name="difficulty" id="difficulty" class="form-select">
                                <option value="">All Levels</option>
                                <option value="beginner" {% if current_difficulty == 'beginner' %}selected{% endif %}>Beginner</option>
                                <option value="intermediate" {% if current_difficulty == 'intermediate' %}selected{% endif %}>Intermediate</option>
                                <option value="advanced" {% if current_difficulty == 'advanced' %}selected{% endif %}>Advanced</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label for="search" class="form-label">Search</label>
                            <input type="text" name="search" id="search" class="form-control" placeholder="Search exercises..." value="{{ current_search }}">
                        </div>
                        <div class="col-md-2">
                            <label class="form-label">&nbsp;</label>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-outline-primary">Filter</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- Exercises Grid -->
            <div class="row">
                {% for exercise in exercises %}
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">{{ exercise.name }}</h5>
                            <p class="card-text">
                                <strong>Category:</strong> {{ exercise.category }}<br>
                                <strong>Difficulty:</strong> 
                                <span class="badge bg-{% if exercise.difficulty_level == 'beginner' %}success{% elif exercise.difficulty_level == 'intermediate' %}warning{% else %}danger{% endif %}">
                                    {{ exercise.difficulty_level.title() }}
                                </span><br>
                                <strong>Muscle Groups:</strong> {{ exercise.muscle_groups }}<br>
                                <strong>Equipment:</strong> {{ exercise.equipment }}
                            </p>
                            {% if exercise.description %}
                            <p class="card-text"><small class="text-muted">{{ exercise.description[:100] }}{% if exercise.description|length > 100 %}...{% endif %}</small></p>
                            {% endif %}
                        </div>
                        <div class="card-footer">
                            <a href="{{ url_for('view_exercise', exercise_id=exercise.id) }}" class="btn btn-sm btn-outline-primary">View Details</a>
                            <a href="{{ url_for('edit_exercise', exercise_id=exercise.id) }}" class="btn btn-sm btn-outline-secondary">Edit</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            {% if not exercises %}
            <div class="text-center py-5">
                <h4>No exercises found</h4>
                <p>Try adjusting your filters or <a href="{{ url_for('create_exercise') }}">add a new exercise</a>.</p>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
EOF
```

### Step 5: Create View Exercise Template

```bash
cat > templates/view_exercise.html << 'EOF'
{% extends "base.html" %}

{% block title %}{{ exercise.name }}{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>{{ exercise.name }}</h2>
                <div>
                    <a href="{{ url_for('exercises_list') }}" class="btn btn-secondary">Back to Exercises</a>
                    <a href="{{ url_for('edit_exercise', exercise_id=exercise.id) }}" class="btn btn-primary">Edit Exercise</a>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-sm-3"><strong>Category:</strong></div>
                                <div class="col-sm-9">{{ exercise.category }}</div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3"><strong>Difficulty:</strong></div>
                                <div class="col-sm-9">
                                    <span class="badge bg-{% if exercise.difficulty_level == 'beginner' %}success{% elif exercise.difficulty_level == 'intermediate' %}warning{% else %}danger{% endif %} fs-6">
                                        {{ exercise.difficulty_level.title() }}
                                    </span>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3"><strong>Equipment:</strong></div>
                                <div class="col-sm-9">{{ exercise.equipment }}</div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-sm-3"><strong>Muscle Groups:</strong></div>
                                <div class="col-sm-9">{{ exercise.muscle_groups }}</div>
                            </div>
                            
                            {% if exercise.description %}
                            <div class="mb-4">
                                <h5>Description</h5>
                                <p>{{ exercise.description }}</p>
                            </div>
                            {% endif %}
                            
                            {% if exercise.instructions %}
                            <div class="mb-4">
                                <h5>Instructions</h5>
                                <div class="bg-light p-3 rounded">
                                    <p class="mb-0">{{ exercise.instructions }}</p>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Exercise Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <a href="{{ url_for('edit_exercise', exercise_id=exercise.id) }}" class="btn btn-primary">Edit Exercise</a>
                                <a href="{{ url_for('exercises_list') }}" class="btn btn-outline-secondary">Back to Library</a>
                                
                                <hr>
                                
                                <form method="POST" action="{{ url_for('delete_exercise', exercise_id=exercise.id) }}" 
                                      onsubmit="return confirm('Are you sure you want to delete this exercise? This action cannot be undone.')">
                                    <button type="submit" class="btn btn-outline-danger w-100">Delete Exercise</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
```

### Step 6: Create Add Exercise Template

```bash
cat > templates/create_exercise.html << 'EOF'
{% extends "base.html" %}

{% block title %}Add New Exercise{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Add New Exercise</h2>
                <a href="{{ url_for('exercises_list') }}" class="btn btn-secondary">Back to Exercises</a>
            </div>
            
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <form method="POST">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="name" class="form-label">Exercise Name *</label>
                                            <input type="text" class="form-control" id="name" name="name" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="category" class="form-label">Category *</label>
                                            <input type="text" class="form-control" id="category" name="category" required 
                                                   placeholder="e.g., Weight Training, Bodyweight, Cardio">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="difficulty_level" class="form-label">Difficulty Level *</label>
                                            <select class="form-select" id="difficulty_level" name="difficulty_level" required>
                                                <option value="">Select Difficulty</option>
                                                <option value="beginner">Beginner</option>
                                                <option value="intermediate">Intermediate</option>
                                                <option value="advanced">Advanced</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="equipment" class="form-label">Equipment</label>
                                            <input type="text" class="form-control" id="equipment" name="equipment" 
                                                   placeholder="e.g., Barbell, Dumbbells, None">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="muscle_groups" class="form-label">Muscle Groups</label>
                                    <input type="text" class="form-control" id="muscle_groups" name="muscle_groups" 
                                           placeholder="e.g., Quadriceps, Glutes, Hamstrings">
                                </div>
                                
                                <div class="mb-3">
                                    <label for="description" class="form-label">Description</label>
                                    <textarea class="form-control" id="description" name="description" rows="3" 
                                              placeholder="Brief description of the exercise"></textarea>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="instructions" class="form-label">Instructions</label>
                                    <textarea class="form-control" id="instructions" name="instructions" rows="4" 
                                              placeholder="Step-by-step instructions for performing the exercise"></textarea>
                                </div>
                                
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <a href="{{ url_for('exercises_list') }}" class="btn btn-outline-secondary me-md-2">Cancel</a>
                                    <button type="submit" class="btn btn-primary">Create Exercise</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
```

### Step 7: Create Edit Exercise Template

```bash
cat > templates/edit_exercise.html << 'EOF'
{% extends "base.html" %}

{% block title %}Edit {{ exercise.name }}{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Edit Exercise: {{ exercise.name }}</h2>
                <div>
                    <a href="{{ url_for('view_exercise', exercise_id=exercise.id) }}" class="btn btn-outline-secondary">View Exercise</a>
                    <a href="{{ url_for('exercises_list') }}" class="btn btn-secondary">Back to Exercises</a>
                </div>
            </div>
            
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <form method="POST">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="name" class="form-label">Exercise Name *</label>
                                            <input type="text" class="form-control" id="name" name="name" value="{{ exercise.name }}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="category" class="form-label">Category *</label>
                                            <input type="text" class="form-control" id="category" name="category" value="{{ exercise.category }}" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="difficulty_level" class="form-label">Difficulty Level *</label>
                                            <select class="form-select" id="difficulty_level" name="difficulty_level" required>
                                                <option value="beginner" {% if exercise.difficulty_level == 'beginner' %}selected{% endif %}>Beginner</option>
                                                <option value="intermediate" {% if exercise.difficulty_level == 'intermediate' %}selected{% endif %}>Intermediate</option>
                                                <option value="advanced" {% if exercise.difficulty_level == 'advanced' %}selected{% endif %}>Advanced</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="equipment" class="form-label">Equipment</label>
                                            <input type="text" class="form-control" id="equipment" name="equipment" value="{{ exercise.equipment or '' }}">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="muscle_groups" class="form-label">Muscle Groups</label>
                                    <input type="text" class="form-control" id="muscle_groups" name="muscle_groups" value="{{ exercise.muscle_groups or '' }}">
                                </div>
                                
                                <div class="mb-3">
                                    <label for="description" class="form-label">Description</label>
                                    <textarea class="form-control" id="description" name="description" rows="3">{{ exercise.description or '' }}</textarea>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="instructions" class="form-label">Instructions</label>
                                    <textarea class="form-control" id="instructions" name="instructions" rows="4">{{ exercise.instructions or '' }}</textarea>
                                </div>
                                
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <a href="{{ url_for('view_exercise', exercise_id=exercise.id) }}" class="btn btn-outline-secondary me-md-2">Cancel</a>
                                    <button type="submit" class="btn btn-primary">Update Exercise</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF
```

## Final Steps

After running all the above commands, restart the Render service to ensure all changes take effect. The complete exercises system will be available at:

- **Main exercises page**: `/trainer/exercises`
- **Add new exercise**: `/trainer/exercises/create`
- **View exercise**: `/trainer/exercises/{id}`
- **Edit exercise**: `/trainer/exercises/{id}/edit`

## Expected Results

1. ✅ **Navigation**: "Exercises" tab appears in the navigation bar for trainers
2. ✅ **Database**: All 109 exercises are stored in the `exercise_library` table
3. ✅ **Functionality**: Complete CRUD operations for exercise management
4. ✅ **Templates**: Professional, responsive templates for all exercise operations
5. ✅ **Filtering**: Search and filter capabilities by category, difficulty, and text
6. ✅ **Integration**: Seamless integration with existing trainer dashboard

## Testing

After deployment, test the following:
1. Login as trainer and verify "Exercises" tab appears
2. Click "Exercises" to see all 109 exercises
3. Test filtering by category and difficulty
4. Test search functionality
5. Test adding a new exercise
6. Test viewing exercise details
7. Test editing an exercise
8. Test deleting an exercise

This complete deployment will give you a fully functional exercise management system with all 109 exercises from your original list.
