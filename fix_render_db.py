#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('trainer_dashboard.db')
cursor = conn.cursor()

# First, let's check what columns exist in the table
cursor.execute("PRAGMA table_info(exercise_library)")
columns = cursor.fetchall()
print("Current table structure:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Drop the existing table and recreate it with the correct schema
cursor.execute("DROP TABLE IF EXISTS exercise_library")

# Create the table with the correct schema
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

# Add exercises with the correct column structure
exercises = [
    ('Back Squat', 'Weight Training', 'Fundamental squat movement', 'Stand with feet shoulder-width apart, barbell on upper back, squat down keeping chest up', 'Quadriceps, Glutes, Hamstrings', 'Barbell, Squat Rack', 'intermediate', 1),
    ('Push-up', 'Bodyweight', 'Classic bodyweight pushing exercise', 'Start in plank position, lower chest to ground, push back up', 'Chest, Shoulders, Triceps', 'None', 'beginner', 1),
    ('Pull-up', 'Bodyweight', 'Vertical pulling exercise', 'Hang from bar, pull body up until chin over bar', 'Lats, Biceps, Rear Delts', 'Pull-up Bar', 'intermediate', 1),
    ('Deadlift', 'Weight Training', 'Hip hinge movement with weights', 'Stand with feet hip-width apart, hinge at hips while lowering weight, return to standing', 'Hamstrings, Glutes, Lower Back', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Bench Press', 'Weight Training', 'Horizontal pushing exercise', 'Lie on bench, lower bar to chest, press up', 'Chest, Shoulders, Triceps', 'Barbell, Bench', 'intermediate', 1),
    ('Overhead Press', 'Weight Training', 'Vertical pushing exercise', 'Press weight from shoulders to overhead', 'Shoulders, Triceps, Core', 'Barbell, Dumbbells', 'intermediate', 1),
    ('Barbell Row', 'Weight Training', 'Horizontal pulling exercise', 'Bend over, pull bar to lower chest/upper abdomen', 'Lats, Rhomboids, Middle Traps, Biceps', 'Barbell', 'intermediate', 1),
    ('Dips', 'Bodyweight', 'Vertical pushing exercise', 'Support body on bars, lower until shoulders below elbows, push up', 'Chest, Shoulders, Triceps', 'Dip Bars', 'intermediate', 1),
    ('Hollow Hold', 'Bodyweight', 'Isometric core exercise', 'Lie on back, lift shoulders and legs, hold position', 'Core, Hip Flexors', 'None', 'intermediate', 1),
    ('RDL', 'Weight Training', 'Romanian Deadlift - hip hinge movement', 'Stand with feet hip-width apart, hinge at hips while lowering weight, return to standing', 'Hamstrings, Glutes, Lower Back', 'Barbell, Dumbbells', 'intermediate', 1)
]

cursor.executemany('''
    INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', exercises)

conn.commit()
conn.close()
print('✅ Exercise library table recreated and populated successfully!')
