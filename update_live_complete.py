#!/usr/bin/env python3
"""
Complete script to update the live deployment with exercises functionality
"""
import sqlite3
import os

def update_live_deployment():
    print("🚀 Updating live deployment with complete exercises functionality...")
    
    # Step 1: Create exercise_library table and add exercises
    print("📊 Setting up exercise database...")
    
    conn = sqlite3.connect('trainer_dashboard.db')
    cursor = conn.cursor()
    
    # Drop and recreate table
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
            difficulty_level TEXT CHECK(difficulty_level IN ('beginner', 'intermediate', 'advanced')),
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Add key exercises to get started
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
        ('Calf Raises', 'Bodyweight', 'Calf muscle exercise', 'Stand on edge of step, raise up on toes', 'Calves', 'Step, Platform', 'beginner', 1)
    ]
    
    cursor.executemany('''
        INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', exercises)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {len(exercises)} exercises to database!")
    print("🎯 Exercise database is ready!")
    
    return True

if __name__ == "__main__":
    update_live_deployment()

