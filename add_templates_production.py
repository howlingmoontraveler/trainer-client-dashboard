#!/usr/bin/env python3
"""
Add program templates directly to production database
Works with both SQLite (local) and PostgreSQL (Render)
"""
from app import get_db

def add_templates():
    """Add all 10 program templates to the database"""
    db = get_db()
    cursor = db.cursor()

    # Check if templates already exist
    existing = cursor.execute('SELECT COUNT(*) as count FROM program_templates').fetchone()
    if existing['count'] > 0:
        print(f"⚠️  Found {existing['count']} existing templates. Skipping to avoid duplicates.")
        print("If you want to re-add templates, delete them first from the database.")
        return

    print("Adding 10 program templates...")

    templates = [
        {
            'name': 'Complete Beginner - Bodyweight Basics',
            'description': 'Perfect for absolute beginners. No equipment needed. 3 days per week full-body routine focusing on fundamental movement patterns.',
            'exercises': [
                ('Bodyweight Squat', '3', '10-15', 'Focus on depth and control', 1),
                ('Push-up', '3', '8-12', 'Modify on knees if needed', 2),
                ('Glute Bridge', '3', '12-15', 'Squeeze at the top', 3),
                ('Dead Bugs', '3', '10 each side', 'Keep lower back pressed down', 4),
                ('Supermans', '3', '10-12', 'Hold for 2 seconds at top', 5),
                ('Walking Lunge', '2', '10 each leg', 'Keep torso upright', 6),
            ]
        },
        {
            'name': 'Upper/Lower Split - Beginner',
            'description': '4-day split alternating upper and lower body. Great for building strength foundation with gym equipment.',
            'exercises': [
                ('Flat DB Press', '3', '8-12', 'Control the descent', 1),
                ('Lat Pulldowns', '3', '10-12', 'Full stretch at top', 2),
                ('Seated DB Press', '3', '8-10', 'Press straight up', 3),
                ('DB Row', '3', '10-12 each', 'Pull elbow back', 4),
                ('Biceps Cable Curls', '3', '12-15', 'Keep elbows stable', 5),
                ('Triceps Pushdown', '3', '12-15', 'Full extension', 6),
                ('Back Squat', '4', '8-10', 'Depth to parallel or below', 7),
                ('Romanian Deadlift', '3', '10-12', 'Feel hamstring stretch', 8),
                ('Leg Press', '3', '12-15', 'Full range of motion', 9),
                ('Hamstring Curls', '3', '12-15', 'Control the negative', 10),
                ('Calf Raises', '4', '15-20', 'Full stretch and contraction', 11),
            ]
        },
        {
            'name': 'Push/Pull/Legs Split',
            'description': 'Classic 3-day or 6-day split. Push (chest/shoulders/triceps), Pull (back/biceps), Legs. Ideal for intermediate lifters.',
            'exercises': [
                ('Flat BB Bench Press', '4', '6-8', 'Progressive overload focus', 1),
                ('Incline DB Press', '3', '8-10', 'Upper chest emphasis', 2),
                ('Standing DB Press', '3', '8-10', 'Shoulder development', 3),
                ('Lateral Raises', '3', '12-15', 'Controlled motion', 4),
                ('Triceps Pushdown', '3', '12-15', 'Lockout at bottom', 5),
                ('Deadlift', '4', '5-8', 'Maintain neutral spine', 6),
                ('Pull-up', '3', '6-10', 'Full range of motion', 7),
                ('Barbell Row', '3', '8-10', 'Pull to lower chest', 8),
                ('DB Row', '3', '10-12 each', 'Squeeze at top', 9),
                ('DB Bicep Curls', '3', '10-12', 'No momentum', 10),
                ('Back Squat', '4', '6-8', 'Below parallel depth', 11),
                ('Romanian Deadlift', '3', '8-10', 'Hinge at hips', 12),
                ('Walking Lunge', '3', '10 each leg', 'Long stride', 13),
                ('Leg Extensions', '3', '12-15', 'Squeeze at top', 14),
                ('Hamstring Curls', '3', '12-15', 'Control eccentric', 15),
            ]
        },
        {
            'name': 'Home Workout - No Equipment',
            'description': 'Complete bodyweight program for home training. No equipment required. Build strength and endurance anywhere.',
            'exercises': [
                ('Bodyweight Squat', '4', '15-20', 'Slow tempo', 1),
                ('Push-up', '4', '10-15', 'Chest to ground', 2),
                ('Split Squat', '3', '12 each leg', 'Back knee to ground', 3),
                ('Walking Lunge', '3', '12 each leg', 'Full range', 4),
                ('Dead Bugs', '3', '12 each side', 'Core engaged', 5),
                ('Glute Bridge', '3', '15-20', '2 second hold at top', 6),
                ('Hollow Hold', '3', '30-45 sec', 'Lower back down', 7),
                ('Supermans', '3', '15-20', 'Controlled reps', 8),
            ]
        },
        {
            'name': 'Strength Builder - Compound Focus',
            'description': 'Heavy compound movements for maximum strength gains. 3-4 days per week. Intermediate to advanced.',
            'exercises': [
                ('Back Squat', '5', '5', 'Heavy weight, perfect form', 1),
                ('Flat BB Bench Press', '5', '5', '2-3 min rest between sets', 2),
                ('Deadlift', '5', '5', 'Reset each rep', 3),
                ('Front Squat', '4', '6-8', 'Upright torso', 4),
                ('Barbell Row', '4', '6-8', 'Explosive pull', 5),
                ('Standing BB Press', '4', '6-8', 'Full lockout', 6),
                ('Romanian Deadlift', '3', '8-10', 'Hamstring focus', 7),
            ]
        },
        {
            'name': 'Upper Body Hypertrophy',
            'description': 'Muscle building program for upper body. Higher volume, moderate weight. Perfect for upper body development days.',
            'exercises': [
                ('Flat BB Bench Press', '4', '8-10', '60-90s rest', 1),
                ('Incline DB Press', '3', '10-12', 'Stretch at bottom', 2),
                ('Cable Cross', '3', '12-15', 'Chest squeeze', 3),
                ('Lat Pulldowns', '4', '10-12', 'Wide grip', 4),
                ('Seated Cable Row', '3', '10-12', 'Retract scapula', 5),
                ('DB Row', '3', '10-12 each', 'Control movement', 6),
                ('Seated DB Press', '3', '10-12', 'Shoulder focus', 7),
                ('Lateral Raises', '3', '15-20', 'Time under tension', 8),
                ('DB Bicep Curls', '3', '12-15', 'Alternating', 9),
                ('Triceps Pushdown', '3', '12-15', 'Rope attachment', 10),
            ]
        },
        {
            'name': 'Lower Body & Core Blast',
            'description': 'Comprehensive leg and core workout. Build powerful legs and a stable core. 1-2x per week.',
            'exercises': [
                ('Back Squat', '4', '8-10', 'Progressive weight', 1),
                ('Romanian Deadlift', '4', '10-12', 'Feel the stretch', 2),
                ('Walking Lunge', '3', '12 each leg', 'Long stride length', 3),
                ('Leg Press', '3', '12-15', 'Full depth', 4),
                ('Hamstring Curls', '3', '12-15', 'Slow eccentric', 5),
                ('Leg Extensions', '3', '12-15', 'Quad squeeze', 6),
                ('Cable Crunch', '3', '15-20', 'Flex abs hard', 7),
                ('Dead Bugs', '3', '12 each side', 'Anti-rotation focus', 8),
                ('RKC Plank', '3', '30-45 sec', 'Maximum tension', 9),
            ]
        },
        {
            'name': 'Athletic Performance',
            'description': 'Develop power, speed, and functional strength. Plyometrics and compound movements. For active individuals.',
            'exercises': [
                ('Box Jump', '4', '5-8', 'Explosive', 1),
                ('Broad Jump', '4', '5', 'Maximum distance', 2),
                ('Back Squat', '4', '6-8', 'Explosive concentric', 3),
                ('Romanian Deadlift', '3', '8-10', 'Hip power', 4),
                ('Sled Push', '4', '20-30m', 'Drive through legs', 5),
                ('Bear Crawl', '3', '30 sec', 'Core stability', 6),
                ('Jump Squats', '3', '8-10', 'Land softly', 7),
                ('Slider Thrusts', '3', '12-15', 'Hip extension power', 8),
            ]
        },
        {
            'name': 'Active Recovery & Mobility',
            'description': 'Light movement, stretching, and mobility work. Perfect for rest days or recovery sessions.',
            'exercises': [
                ('Foam Rolling', '1', '5 min', 'All major muscle groups', 1),
                ('Diaphragmatic Breathing', '3', '10 breaths', 'Deep belly breathing', 2),
                ('Childs Pose', '3', '60 sec', 'Relax into stretch', 3),
                ('Dead Hangs', '3', '20-30 sec', 'Shoulder decompression', 4),
                ('Glute Bridge', '3', '15', 'Activation only', 5),
                ('Bodyweight Squat', '3', '15', 'Movement quality', 6),
                ('Cossack Squat', '3', '8 each side', 'Hip mobility', 7),
                ('Spiderman Lunge w/ Thoracic Rotation', '3', '8 each side', 'Full body mobility', 8),
            ]
        },
        {
            'name': 'Time-Efficient Full Body',
            'description': 'Complete workout in 45 minutes. Compound movements only. Perfect for busy schedules. 3x per week.',
            'exercises': [
                ('Back Squat', '3', '8-10', '90s rest', 1),
                ('Flat BB Bench Press', '3', '8-10', '90s rest', 2),
                ('Deadlift', '3', '8-10', '2 min rest', 3),
                ('Barbell Row', '3', '8-10', '90s rest', 4),
                ('Standing BB Press', '3', '8-10', '90s rest', 5),
                ('Romanian Deadlift', '3', '10-12', '60s rest', 6),
                ('Pull-up', '3', '6-10', 'Assisted if needed', 7),
            ]
        },
    ]

    # Insert templates and exercises
    for template in templates:
        cursor.execute(
            'INSERT INTO program_templates (created_by, name, description) VALUES (?, ?, ?)',
            (1, template['name'], template['description'])
        )
        template_id = cursor.lastrowid

        for exercise in template['exercises']:
            cursor.execute(
                '''INSERT INTO program_template_exercises
                   (template_id, name, sets, reps, notes, exercise_order)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (template_id, *exercise)
            )

        print(f"  ✓ Added: {template['name']}")

    db.commit()

    # Verify
    count = cursor.execute('SELECT COUNT(*) as count FROM program_templates').fetchone()
    print(f"\n✅ Successfully added {count['count']} program templates!")
    print("\nTemplates are now available in your application!")
    print("Go to Templates → View all programs")

if __name__ == '__main__':
    add_templates()
