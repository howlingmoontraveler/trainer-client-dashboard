#!/usr/bin/env python3
"""
Complete deployment script for exercises functionality
Run this in the Render shell to add all exercises features
"""
import sqlite3
import os

def deploy_exercises_complete():
    print("🚀 Deploying complete exercises functionality to live app...")
    
    # Step 1: Set up database
    print("📊 Setting up exercise database...")
    conn = sqlite3.connect('trainer_dashboard.db')
    cursor = conn.cursor()
    
    # Create exercise_library table
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
    
    # Add comprehensive exercise list
    exercises = [
        # SQUATS & LOWER BODY
        ("Back Squat", "Weight Training", "Fundamental squat movement with barbell on back", "Stand with feet shoulder-width apart, barbell on upper back, squat down keeping chest up, return to standing", "Quadriceps, Glutes, Hamstrings, Core", "Barbell, Squat Rack", "intermediate", 1),
        ("Bodyweight Squat", "Bodyweight", "Basic squat without external weight", "Stand with feet shoulder-width apart, squat down as if sitting in a chair, return to standing", "Quadriceps, Glutes, Hamstrings", "None", "beginner", 1),
        ("Front Squat", "Weight Training", "Squat with barbell in front position", "Hold barbell in front rack position, squat down keeping elbows up, return to standing", "Quadriceps, Glutes, Hamstrings, Core, Upper Back", "Barbell, Squat Rack", "intermediate", 1),
        ("Goblet Squat", "Weight Training", "Squat holding weight at chest", "Hold dumbbell or kettlebell at chest, squat down keeping weight close to body", "Quadriceps, Glutes, Hamstrings, Core", "Dumbbell, Kettlebell", "beginner", 1),
        ("Overhead Squat", "Weight Training", "Squat while holding weight overhead", "Hold weight overhead with arms locked, squat down maintaining overhead position", "Quadriceps, Glutes, Hamstrings, Shoulders, Core", "Barbell, Dumbbell", "advanced", 1),
        ("Zercher Squat", "Weight Training", "Squat with barbell in elbow crooks", "Hold barbell in elbow crooks, squat down maintaining position", "Quadriceps, Glutes, Hamstrings, Core", "Barbell", "advanced", 1),
        ("Sissy Squats", "Bodyweight", "Advanced bodyweight squat variation", "Stand on toes, lean back while squatting down, return to standing", "Quadriceps", "None", "advanced", 1),
        ("Cossack Squat", "Bodyweight", "Lateral squat movement", "Stand with wide stance, shift weight to one side while keeping other leg straight", "Quadriceps, Glutes, Hip Adductors", "None", "intermediate", 1),
        
        # LUNGES & SPLIT STANCE
        ("Split Squat", "Bodyweight", "Single leg squat with rear foot elevated", "Place rear foot on bench, squat down with front leg, return to standing", "Quadriceps, Glutes, Hamstrings", "Bench", "intermediate", 1),
        ("Front Foot Elevated Split Squat", "Bodyweight", "Split squat with front foot elevated", "Place front foot on platform, perform split squat", "Quadriceps, Glutes, Hamstrings", "Platform, Bench", "intermediate", 1),
        ("Walking Lunge", "Bodyweight", "Lunges while moving forward", "Step forward into lunge, push off front leg to next lunge", "Quadriceps, Glutes, Hamstrings", "None", "intermediate", 1),
        
        # DEADLIFTS & HIP HINGE
        ("RDL", "Weight Training", "Romanian Deadlift - hip hinge movement", "Stand with feet hip-width apart, hinge at hips while lowering weight, return to standing", "Hamstrings, Glutes, Lower Back", "Barbell, Dumbbells", "intermediate", 1),
        ("Trapbar Deadlift", "Weight Training", "Deadlift using trap bar", "Stand inside trap bar, lift by extending hips and knees", "Hamstrings, Glutes, Quadriceps, Traps", "Trap Bar", "intermediate", 1),
        ("Single Leg RDL", "Bodyweight", "Single leg Romanian deadlift", "Stand on one leg, hinge at hip while extending other leg back", "Hamstrings, Glutes, Core", "None", "intermediate", 1),
        
        # PUSHING EXERCISES
        ("Flat Bench Press", "Weight Training", "Horizontal pushing exercise on bench", "Lie on bench, lower bar to chest, press up", "Chest, Shoulders, Triceps", "Barbell, Bench", "intermediate", 1),
        ("Close Grip BB Bench Press", "Weight Training", "Bench press with narrow grip", "Lie on bench, use narrow grip, lower bar to chest, press up", "Chest, Triceps", "Barbell, Bench", "intermediate", 1),
        ("Push-up", "Bodyweight", "Classic bodyweight pushing exercise", "Start in plank position, lower chest to ground, push back up", "Chest, Shoulders, Triceps", "None", "beginner", 1),
        ("Deficit pushup", "Bodyweight", "Push-up with hands elevated", "Place hands on platform, perform push-up with increased range of motion", "Chest, Shoulders, Triceps", "Platform", "intermediate", 1),
        ("Dips", "Bodyweight", "Vertical pushing exercise", "Support body on bars, lower until shoulders below elbows, push up", "Chest, Shoulders, Triceps", "Dip Bars", "intermediate", 1),
        ("Overhead Press", "Weight Training", "Vertical pushing exercise", "Press weight from shoulders to overhead", "Shoulders, Triceps, Core", "Barbell, Dumbbells", "intermediate", 1),
        ("SA DB OH Press", "Weight Training", "Single arm dumbbell overhead press", "Press single dumbbell overhead, alternating arms", "Shoulders, Triceps, Core", "Dumbbell", "intermediate", 1),
        ("Incline DB Press", "Weight Training", "Incline bench press with dumbbells", "Lie on incline bench, press dumbbells from chest", "Upper Chest, Shoulders, Triceps", "Dumbbells, Incline Bench", "intermediate", 1),
        ("Decline DB Press", "Weight Training", "Decline bench press with dumbbells", "Lie on decline bench, press dumbbells from chest", "Lower Chest, Shoulders, Triceps", "Dumbbells, Decline Bench", "intermediate", 1),
        
        # PULLING EXERCISES
        ("Barbell Row", "Weight Training", "Horizontal pulling exercise", "Bend over, pull bar to lower chest/upper abdomen", "Lats, Rhomboids, Middle Traps, Biceps", "Barbell", "intermediate", 1),
        ("Pull-up", "Bodyweight", "Vertical pulling exercise", "Hang from bar, pull body up until chin over bar", "Lats, Biceps, Rear Delts", "Pull-up Bar", "intermediate", 1),
        ("Inverted Row", "Bodyweight", "Horizontal bodyweight row", "Lie under bar, pull chest to bar", "Lats, Rhomboids, Middle Traps, Biceps", "Bar, TRX", "intermediate", 1),
        ("Seated Cable Row", "Weight Training", "Seated horizontal cable row", "Sit at cable machine, pull handle to torso", "Lats, Rhomboids, Middle Traps, Biceps", "Cable Machine", "beginner", 1),
        ("Lat Pulldown - Wide grip", "Weight Training", "Wide grip lat pulldown", "Pull bar down to upper chest with wide grip", "Lats, Upper Back", "Cable Machine", "beginner", 1),
        ("Lat Pulldown - close grip", "Weight Training", "Close grip lat pulldown", "Pull bar down with narrow grip", "Lats, Middle Back", "Cable Machine", "beginner", 1),
        ("Lat Pulldown - Single Arm", "Weight Training", "Single arm lat pulldown", "Pull single handle down, alternating arms", "Lats, Core", "Cable Machine", "intermediate", 1),
        
        # ARM EXERCISES
        ("Biceps Cable Curls", "Weight Training", "Cable bicep curls", "Curl cable handles up, focusing on biceps", "Biceps", "Cable Machine", "beginner", 1),
        ("EZ Bar Curl", "Weight Training", "Bicep curls with EZ bar", "Curl EZ bar up, focusing on biceps", "Biceps", "EZ Bar", "beginner", 1),
        ("Jackson 5 Curls", "Weight Training", "Bicep curl variation", "Perform bicep curls with specific tempo and pattern", "Biceps", "Dumbbells", "intermediate", 1),
        ("Reverse Curls", "Weight Training", "Reverse grip bicep curls", "Curl with overhand grip, targeting forearms", "Forearms, Biceps", "Barbell, Dumbbells", "intermediate", 1),
        ("Zottman Curls", "Weight Training", "Curl with grip rotation", "Curl up with supinated grip, rotate to pronated on way down", "Biceps, Forearms", "Dumbbells", "intermediate", 1),
        ("Triceps Pushdown", "Weight Training", "Cable tricep pushdown", "Push cable handle down, extending elbows", "Triceps", "Cable Machine", "beginner", 1),
        ("Triceps Extension - Decline", "Weight Training", "Decline tricep extension", "Perform tricep extension on decline bench", "Triceps", "Decline Bench, Dumbbells", "intermediate", 1),
        ("Dual Arm Cable OH Triceps Ext", "Weight Training", "Overhead cable tricep extension", "Extend cable overhead, targeting triceps", "Triceps", "Cable Machine", "intermediate", 1),
        ("Cross Body SA Tricep Ext", "Weight Training", "Cross body single arm tricep extension", "Extend single dumbbell across body", "Triceps", "Dumbbell", "intermediate", 1),
        ("Decline DB Tricep Ext", "Weight Training", "Decline dumbbell tricep extension", "Perform tricep extension on decline bench", "Triceps", "Decline Bench, Dumbbells", "intermediate", 1),
        
        # CORE EXERCISES
        ("Hollow Hold", "Bodyweight", "Isometric core exercise", "Lie on back, lift shoulders and legs, hold position", "Core, Hip Flexors", "None", "intermediate", 1),
        ("RKC Plank", "Bodyweight", "Advanced plank variation", "Hold plank with maximum tension throughout body", "Core, Shoulders", "None", "intermediate", 1),
        ("Dead Bugs", "Bodyweight", "Core stability exercise", "Lie on back, extend opposite arm and leg, return to start", "Core, Hip Flexors", "None", "beginner", 1),
        ("Leg Raises", "Bodyweight", "Hip flexor and lower core exercise", "Lie on back, raise legs up and down", "Lower Abs, Hip Flexors", "None", "intermediate", 1),
        ("Leg Lifts", "Bodyweight", "Hip flexor exercise", "Lie on side, lift top leg up and down", "Hip Abductors, Glutes", "None", "beginner", 1),
        ("Cable Crunch", "Weight Training", "Cable core exercise", "Kneel at cable machine, crunch down", "Core", "Cable Machine", "intermediate", 1),
        ("Cable Rotation", "Weight Training", "Rotational core exercise", "Stand sideways to cable, rotate torso", "Obliques, Core", "Cable Machine", "intermediate", 1),
        ("Cable Chop High to Low", "Weight Training", "Diagonal cable chop", "Pull cable from high to low across body", "Obliques, Core", "Cable Machine", "intermediate", 1),
        ("Pallof Press", "Weight Training", "Anti-rotation core exercise", "Stand sideways to cable, press handle away from body", "Core, Obliques", "Cable Machine", "intermediate", 1),
        ("Plate V Ups", "Weight Training", "V-up with weight plate", "Perform V-ups holding weight plate", "Core, Hip Flexors", "Weight Plate", "intermediate", 1),
        ("Suitcase Plate Crunch", "Weight Training", "Crunch holding weight like suitcase", "Hold weight plate, perform crunches", "Core, Obliques", "Weight Plate", "intermediate", 1),
        ("Slider Thrusts", "Bodyweight", "Core exercise with sliders", "Use sliders to perform thrusting motion", "Core, Hip Flexors", "Sliders", "intermediate", 1),
        
        # GLUTE & HIP EXERCISES
        ("Glute Bridge", "Bodyweight", "Basic glute activation exercise", "Lie on back, lift hips up squeezing glutes", "Glutes, Hamstrings", "None", "beginner", 1),
        ("Hip Abduction", "Bodyweight", "Lateral hip movement", "Stand on one leg, lift other leg to side", "Hip Abductors, Glutes", "None", "beginner", 1),
        ("Hip Adduction", "Bodyweight", "Medial hip movement", "Stand on one leg, cross other leg in front", "Hip Adductors", "None", "beginner", 1),
        ("Reverse Hyper", "Weight Training", "Posterior chain exercise", "Lie face down, lift legs up behind body", "Glutes, Hamstrings, Lower Back", "Reverse Hyper Machine", "intermediate", 1),
        
        # LEG EXERCISES
        ("Leg Press", "Weight Training", "Machine leg exercise", "Sit in leg press machine, press weight with legs", "Quadriceps, Glutes", "Leg Press Machine", "beginner", 1),
        ("Leg Extension", "Weight Training", "Quadricep isolation exercise", "Sit in leg extension machine, extend legs", "Quadriceps", "Leg Extension Machine", "beginner", 1),
        ("Leg Curls", "Weight Training", "Hamstring isolation exercise", "Lie in leg curl machine, curl legs up", "Hamstrings", "Leg Curl Machine", "beginner", 1),
        ("Calf Raises", "Bodyweight", "Calf muscle exercise", "Stand on edge of step, raise up on toes", "Calves", "Step, Platform", "beginner", 1),
        ("Tibialis Raises", "Bodyweight", "Anterior tibialis exercise", "Sit with feet flat, lift toes up", "Tibialis Anterior", "None", "beginner", 1),
        
        # CARRY EXERCISES
        ("Farmer's Carry", "Weight Training", "Loaded carry exercise", "Carry heavy weights in each hand, walk forward", "Core, Grip, Traps, Glutes", "Dumbbells, Kettlebells", "intermediate", 1),
        ("Safety Bar Carry", "Weight Training", "Carry with safety bar", "Carry safety bar on shoulders, walk forward", "Core, Traps, Glutes", "Safety Bar", "intermediate", 1),
        ("Sandbag Over Shoulder", "Weight Training", "Sandbag carry exercise", "Carry sandbag over shoulder, walk forward", "Core, Traps, Glutes", "Sandbag", "intermediate", 1),
        
        # PUSHING VARIATIONS
        ("Dumbbell Fly", "Weight Training", "Chest fly exercise", "Lie on bench, open arms wide, bring together", "Chest, Anterior Delts", "Dumbbells, Bench", "intermediate", 1),
        ("Pec Fly", "Weight Training", "Chest fly variation", "Perform chest fly movement", "Chest, Anterior Delts", "Dumbbells, Cable Machine", "intermediate", 1),
        ("Cable Cross", "Weight Training", "Cable chest fly", "Stand between cables, bring handles together", "Chest, Anterior Delts", "Cable Machine", "intermediate", 1),
        ("Cable Side Raise", "Weight Training", "Lateral deltoid exercise", "Stand next to cable, raise arm to side", "Lateral Delts", "Cable Machine", "beginner", 1),
        
        # FUNCTIONAL & PLYOMETRIC
        ("Box Jump", "Plyometric", "Explosive jumping exercise", "Jump onto box, step down, repeat", "Quadriceps, Glutes, Calves", "Box, Platform", "intermediate", 1),
        ("Broad Jump", "Plyometric", "Horizontal jumping exercise", "Jump forward as far as possible", "Quadriceps, Glutes, Calves", "None", "intermediate", 1),
        ("Jump Squats", "Plyometric", "Explosive squat variation", "Perform squat with explosive jump", "Quadriceps, Glutes, Calves", "None", "intermediate", 1),
        ("Power Clean", "Weight Training", "Olympic lifting movement", "Explosively lift bar from floor to shoulders", "Quadriceps, Glutes, Hamstrings, Traps", "Barbell", "advanced", 1),
        ("Kettlebell Swing", "Weight Training", "Hip hinge with kettlebell", "Swing kettlebell from between legs to chest level", "Hamstrings, Glutes, Core", "Kettlebell", "intermediate", 1),
        
        # MOBILITY & RECOVERY
        ("Child's Pose", "Flexibility", "Restorative yoga pose", "Kneel and sit back on heels, reach arms forward", "Hip Flexors, Lower Back", "None", "beginner", 1),
        ("Diaphragmatic Breathing", "Flexibility", "Breathing exercise", "Lie down, breathe deeply into diaphragm", "Diaphragm, Core", "None", "beginner", 1),
        ("Foam Rolling", "Flexibility", "Self-massage with foam roller", "Roll muscles with foam roller for recovery", "Various Muscle Groups", "Foam Roller", "beginner", 1),
        ("Jefferson Curls", "Flexibility", "Spinal mobility exercise", "Stand on platform, slowly curl spine down", "Spinal Erectors, Hamstrings", "Platform", "intermediate", 1),
        
        # SPECIALIZED EXERCISES
        ("Bear Crawl", "Functional", "Quadrupedal movement", "Crawl on hands and feet, keeping knees off ground", "Core, Shoulders, Hip Flexors", "None", "intermediate", 1),
        ("Dead Hangs", "Bodyweight", "Grip and shoulder stability", "Hang from bar for time", "Grip, Lats, Shoulders", "Pull-up Bar", "intermediate", 1),
        ("L Sit Progression", "Bodyweight", "Advanced core exercise", "Sit with legs extended, support body with hands", "Core, Hip Flexors, Triceps", "None", "advanced", 1),
        ("Supermans", "Bodyweight", "Posterior chain exercise", "Lie face down, lift chest and legs", "Lower Back, Glutes, Hamstrings", "None", "beginner", 1),
        ("Shrugs", "Weight Training", "Trap strengthening exercise", "Lift shoulders up and down with weight", "Traps", "Barbell, Dumbbells", "beginner", 1),
        ("Figure 8s", "Weight Training", "Dynamic movement pattern", "Move weight in figure-8 pattern", "Core, Shoulders", "Dumbbell, Kettlebell", "intermediate", 1),
        ("Sled Drag", "Functional", "Pulling sled exercise", "Drag weighted sled forward", "Glutes, Hamstrings, Core", "Sled, Weight", "intermediate", 1),
        ("Sled Push", "Functional", "Pushing sled exercise", "Push weighted sled forward", "Quadriceps, Glutes, Core", "Sled, Weight", "intermediate", 1),
        ("VO2 Max", "Cardio", "High-intensity cardio training", "Perform high-intensity intervals for VO2 max improvement", "Cardiovascular System", "Various", "advanced", 1),
        
        # FOREARM & GRIP
        ("Forearm Complex", "Weight Training", "Forearm strengthening", "Perform various forearm exercises", "Forearms, Grip", "Dumbbells, Barbell", "intermediate", 1),
        ("Forearm banded KB/BB complex", "Weight Training", "Forearm work with bands", "Use bands for forearm strengthening", "Forearms, Grip", "Bands, Kettlebell, Barbell", "intermediate", 1),
    ]
    
    cursor.executemany('''
        INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', exercises)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {len(exercises)} exercises to database!")
    print("🎯 Exercise database is ready!")
    print("📝 Next: Add the exercises routes to app.py and templates")
    print("🚀 Your exercises feature will be live!")
    
    return True

if __name__ == "__main__":
    deploy_exercises_complete()
