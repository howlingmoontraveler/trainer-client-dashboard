-- Delete old sample templates first
DELETE FROM program_template_exercises WHERE template_id IN (1, 2);
DELETE FROM program_templates WHERE id IN (1, 2);

-- Create 10 comprehensive program templates for easy client onboarding

-- 1. Complete Beginner - Bodyweight Basics (3 days/week)
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Complete Beginner - Bodyweight Basics', 'Perfect for absolute beginners. No equipment needed. 3 days per week full-body routine focusing on fundamental movement patterns.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(1, 'Bodyweight Squat', '3', '10-15', 'Focus on depth and control', 1),
(1, 'Push-up', '3', '8-12', 'Modify on knees if needed', 2),
(1, 'Glute Bridge', '3', '12-15', 'Squeeze at the top', 3),
(1, 'Dead Bugs', '3', '10 each side', 'Keep lower back pressed down', 4),
(1, 'Supermans', '3', '10-12', 'Hold for 2 seconds at top', 5),
(1, 'Walking Lunge', '2', '10 each leg', 'Keep torso upright', 6);

-- 2. Upper/Lower Split - Beginner
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Upper/Lower Split - Beginner', '4-day split alternating upper and lower body. Great for building strength foundation with gym equipment.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
-- Upper Day
(2, 'Flat DB Press', '3', '8-12', 'Control the descent', 1),
(2, 'Lat Pulldowns', '3', '10-12', 'Full stretch at top', 2),
(2, 'Seated DB Press', '3', '8-10', 'Press straight up', 3),
(2, 'DB Row', '3', '10-12 each', 'Pull elbow back', 4),
(2, 'Biceps Cable Curls', '3', '12-15', 'Keep elbows stable', 5),
(2, 'Triceps Pushdown', '3', '12-15', 'Full extension', 6),
-- Lower Day (add these to a second program or note alternate days)
(2, 'Back Squat', '4', '8-10', 'Depth to parallel or below', 7),
(2, 'Romanian Deadlift', '3', '10-12', 'Feel hamstring stretch', 8),
(2, 'Leg Press', '3', '12-15', 'Full range of motion', 9),
(2, 'Hamstring Curls', '3', '12-15', 'Control the negative', 10),
(2, 'Calf Raises', '4', '15-20', 'Full stretch and contraction', 11);

-- 3. Push/Pull/Legs Split
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Push/Pull/Legs Split', 'Classic 3-day or 6-day split. Push (chest/shoulders/triceps), Pull (back/biceps), Legs. Ideal for intermediate lifters.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
-- Push
(3, 'Flat BB Bench Press', '4', '6-8', 'Progressive overload focus', 1),
(3, 'Incline DB Press', '3', '8-10', 'Upper chest emphasis', 2),
(3, 'Standing DB Press', '3', '8-10', 'Shoulder development', 3),
(3, 'Lateral Raises', '3', '12-15', 'Controlled motion', 4),
(3, 'Triceps Pushdown', '3', '12-15', 'Lockout at bottom', 5),
-- Pull
(3, 'Deadlift', '4', '5-8', 'Maintain neutral spine', 6),
(3, 'Pull-up', '3', '6-10', 'Full range of motion', 7),
(3, 'Barbell Row', '3', '8-10', 'Pull to lower chest', 8),
(3, 'DB Row', '3', '10-12 each', 'Squeeze at top', 9),
(3, 'DB Bicep Curls', '3', '10-12', 'No momentum', 10),
-- Legs
(3, 'Back Squat', '4', '6-8', 'Below parallel depth', 11),
(3, 'Romanian Deadlift', '3', '8-10', 'Hinge at hips', 12),
(3, 'Walking Lunge', '3', '10 each leg', 'Long stride', 13),
(3, 'Leg Extensions', '3', '12-15', 'Squeeze at top', 14),
(3, 'Hamstring Curls', '3', '12-15', 'Control eccentric', 15);

-- 4. Home Workout - No Equipment
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Home Workout - No Equipment', 'Complete bodyweight program for home training. No equipment required. Build strength and endurance anywhere.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(4, 'Bodyweight Squat', '4', '15-20', 'Slow tempo', 1),
(4, 'Push-up', '4', '10-15', 'Chest to ground', 2),
(4, 'Split Squat', '3', '12 each leg', 'Back knee to ground', 3),
(4, 'Walking Lunge', '3', '12 each leg', 'Full range', 4),
(4, 'Dead Bugs', '3', '12 each side', 'Core engaged', 5),
(4, 'Glute Bridge', '3', '15-20', '2 second hold at top', 6),
(4, 'Hollow Hold', '3', '30-45 sec', 'Lower back down', 7),
(4, 'Supermans', '3', '15-20', 'Controlled reps', 8);

-- 5. Strength Builder - Compound Focus
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Strength Builder - Compound Focus', 'Heavy compound movements for maximum strength gains. 3-4 days per week. Intermediate to advanced.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(5, 'Back Squat', '5', '5', 'Heavy weight, perfect form', 1),
(5, 'Flat BB Bench Press', '5', '5', '2-3 min rest between sets', 2),
(5, 'Deadlift', '5', '5', 'Reset each rep', 3),
(5, 'Front Squat', '4', '6-8', 'Upright torso', 4),
(5, 'Barbell Row', '4', '6-8', 'Explosive pull', 5),
(5, 'Standing BB Press', '4', '6-8', 'Full lockout', 6),
(5, 'Romanian Deadlift', '3', '8-10', 'Hamstring focus', 7);

-- 6. Upper Body Hypertrophy
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Upper Body Hypertrophy', 'Muscle building program for upper body. Higher volume, moderate weight. Perfect for upper body development days.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(6, 'Flat BB Bench Press', '4', '8-10', '60-90s rest', 1),
(6, 'Incline DB Press', '3', '10-12', 'Stretch at bottom', 2),
(6, 'Cable Cross', '3', '12-15', 'Chest squeeze', 3),
(6, 'Lat Pulldowns', '4', '10-12', 'Wide grip', 4),
(6, 'Seated Cable Row', '3', '10-12', 'Retract scapula', 5),
(6, 'DB Row', '3', '10-12 each', 'Control movement', 6),
(6, 'Seated DB Press', '3', '10-12', 'Shoulder focus', 7),
(6, 'Lateral Raises', '3', '15-20', 'Time under tension', 8),
(6, 'DB Bicep Curls', '3', '12-15', 'Alternating', 9),
(6, 'Triceps Pushdown', '3', '12-15', 'Rope attachment', 10);

-- 7. Lower Body & Core Blast
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Lower Body & Core Blast', 'Comprehensive leg and core workout. Build powerful legs and a stable core. 1-2x per week.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(7, 'Back Squat', '4', '8-10', 'Progressive weight', 1),
(7, 'Romanian Deadlift', '4', '10-12', 'Feel the stretch', 2),
(7, 'Walking Lunge', '3', '12 each leg', 'Long stride length', 3),
(7, 'Leg Press', '3', '12-15', 'Full depth', 4),
(7, 'Hamstring Curls', '3', '12-15', 'Slow eccentric', 5),
(7, 'Leg Extensions', '3', '12-15', 'Quad squeeze', 6),
(7, 'Cable Crunch', '3', '15-20', 'Flex abs hard', 7),
(7, 'Dead Bugs', '3', '12 each side', 'Anti-rotation focus', 8),
(7, 'RKC Plank', '3', '30-45 sec', 'Maximum tension', 9);

-- 8. Athletic Performance
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Athletic Performance', 'Develop power, speed, and functional strength. Plyometrics and compound movements. For active individuals.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(8, 'Box Jump', '4', '5-8', 'Explosive', 1),
(8, 'Broad Jump', '4', '5', 'Maximum distance', 2),
(8, 'Back Squat', '4', '6-8', 'Explosive concentric', 3),
(8, 'Romanian Deadlift', '3', '8-10', 'Hip power', 4),
(8, 'Sled Push', '4', '20-30m', 'Drive through legs', 5),
(8, 'Bear Crawl', '3', '30 sec', 'Core stability', 6),
(8, 'Jump Squats', '3', '8-10', 'Land softly', 7),
(8, 'Slider Thrusts', '3', '12-15', 'Hip extension power', 8);

-- 9. Active Recovery & Mobility
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Active Recovery & Mobility', 'Light movement, stretching, and mobility work. Perfect for rest days or recovery sessions.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(9, 'Foam Rolling', '1', '5 min', 'All major muscle groups', 1),
(9, 'Diaphragmatic Breathing', '3', '10 breaths', 'Deep belly breathing', 2),
(9, 'Childs Pose', '3', '60 sec', 'Relax into stretch', 3),
(9, 'Dead Hangs', '3', '20-30 sec', 'Shoulder decompression', 4),
(9, 'Glute Bridge', '3', '15', 'Activation only', 5),
(9, 'Bodyweight Squat', '3', '15', 'Movement quality', 6),
(9, 'Cossack Squat', '3', '8 each side', 'Hip mobility', 7),
(9, 'Spiderman Lunge w/ Thoracic Rotation', '3', '8 each side', 'Full body mobility', 8);

-- 10. Time-Efficient Full Body
INSERT INTO program_templates (created_by, name, description) VALUES
(1, 'Time-Efficient Full Body', 'Complete workout in 45 minutes. Compound movements only. Perfect for busy schedules. 3x per week.');

INSERT INTO program_template_exercises (template_id, name, sets, reps, notes, exercise_order) VALUES
(10, 'Back Squat', '3', '8-10', '90s rest', 1),
(10, 'Flat BB Bench Press', '3', '8-10', '90s rest', 2),
(10, 'Deadlift', '3', '8-10', '2 min rest', 3),
(10, 'Barbell Row', '3', '8-10', '90s rest', 4),
(10, 'Standing BB Press', '3', '8-10', '90s rest', 5),
(10, 'Romanian Deadlift', '3', '10-12', '60s rest', 6),
(10, 'Pull-up', '3', '6-10', 'Assisted if needed', 7);
