-- Users table (both trainers and clients)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('trainer', 'client')),
    full_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trainer-Client relationships
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES users(id),
    FOREIGN KEY (client_id) REFERENCES users(id),
    UNIQUE(trainer_id, client_id)
);

-- Workout programs
CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Exercise Library (master list of all available exercises)
CREATE TABLE IF NOT EXISTS exercise_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    equipment TEXT,
    description TEXT,
    is_custom BOOLEAN DEFAULT 0,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Exercises within programs (references exercise library)
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    exercise_library_id INTEGER,
    name TEXT NOT NULL,
    sets TEXT,
    reps TEXT,
    weight TEXT,
    notes TEXT,
    exercise_order INTEGER,
    FOREIGN KEY (program_id) REFERENCES programs(id),
    FOREIGN KEY (exercise_library_id) REFERENCES exercise_library(id)
);

-- Client workout logs
CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    sets_completed INTEGER,
    reps_completed INTEGER,
    weight_used REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);

-- Training sessions (in-person)
CREATE TABLE IF NOT EXISTS training_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    session_date DATETIME NOT NULL,
    duration INTEGER,
    notes TEXT,
    status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES users(id),
    FOREIGN KEY (client_id) REFERENCES users(id)
);

-- Insert demo data (only if not exists)
INSERT INTO users (username, password_hash, role, full_name, email)
VALUES ('trainer1', 'scrypt:32768:8:1$xqB1VzRnFpyUycY9$026e7ca159aede32212b0675768def409ea041148b7a95357fd936743d35042641a87ae8200d5c24435603f2957454c1c4b1399bff724df330a1b8c94b6011da', 'trainer', 'John Trainer', 'john@example.com');

INSERT INTO users (username, password_hash, role, full_name, email)
VALUES ('client1', 'scrypt:32768:8:1$br49hJ2xTt3N3OhS$85a9c62b271e6d1c8c05dd2457be3452ec2068f9904a61df9396e95953db2a6cc0ad6e77b70deba85f103068761411bd83a618e882f1be8254a78cbd8343a918', 'client', 'Jane Client', 'jane@example.com');

-- Link client to trainer (only if not exists)
INSERT INTO clients (trainer_id, client_id)
VALUES (1, 2);

-- Populate Exercise Library (only if empty)
INSERT INTO exercise_library (name, category, equipment, description) VALUES
-- Legs
('Back Squat', 'Legs', 'Barbell', 'Compound lower body exercise'),
('Bodyweight Squat', 'Legs', 'Bodyweight', 'Foundational squat pattern'),
('Box Jump', 'Legs', 'Plyometric', 'Explosive lower body power'),
('Broad Jump', 'Legs', 'Plyometric', 'Horizontal power development'),
('Cossack Squat', 'Legs', 'Bodyweight', 'Lateral movement pattern'),
('Front Foot Elevated Split Squat', 'Legs', 'Dumbbell', 'Single leg quad focus'),
('Front Squat', 'Legs', 'Barbell', 'Quad-dominant squat variation'),
('Glute Bridge', 'Legs', 'Bodyweight', 'Glute activation exercise'),
('Goblet Squat', 'Legs', 'Kettlebell', 'Beginner-friendly squat'),
('Hip Abduction', 'Legs', 'Machine', 'Lateral hip strengthening'),
('Hip Adduction', 'Legs', 'Machine', 'Inner thigh strengthening'),
('Jump Squats', 'Legs', 'Plyometric', 'Explosive squat variation'),
('Landmine Bulgarian Squat', 'Legs', 'Landmine', 'Single leg strength builder'),
('Landmine Calf Raise', 'Legs', 'Landmine', 'Calf development'),
('Landmine Cossack Lunge', 'Legs', 'Landmine', 'Lateral lunge pattern'),
('Landmine FFESS', 'Legs', 'Landmine', 'Front foot elevated split squat'),
('Landmine Knee Drive Reverse Lunge', 'Legs', 'Landmine', 'Dynamic reverse lunge'),
('Landmine Low Hold Squat Jump', 'Legs', 'Landmine', 'Explosive squat with load'),
('Landmine Lunge Combo', 'Legs', 'Landmine', 'Multi-directional lunge pattern'),
('Landmine Reverse Suitcase Lunge', 'Legs', 'Landmine', 'Unilateral lunge variation'),
('Landmine RDL', 'Legs', 'Landmine', 'Hamstring and glute focus'),
('Landmine Single Leg Hip Thrust', 'Legs', 'Landmine', 'Single leg glute builder'),
('Landmine Split Stance RDL', 'Legs', 'Landmine', 'Split stance hinge pattern'),
('Leg Curls', 'Legs', 'Machine', 'Hamstring isolation'),
('Leg Extension', 'Legs', 'Machine', 'Quad isolation'),
('Leg Press', 'Legs', 'Machine', 'Compound leg press'),
('Overhead Squat', 'Legs', 'Barbell', 'Full body mobility squat'),
('RDL', 'Legs', 'Barbell', 'Romanian deadlift'),
('Single Leg RDL', 'Legs', 'Dumbbell', 'Single leg balance and strength'),
('Sissy Squats', 'Legs', 'Bodyweight', 'Quad isolation exercise'),
('Sled Drag', 'Legs', 'Sled', 'Posterior chain conditioning'),
('Slider Thrusts', 'Legs', 'Sliders', 'Hamstring and glute activation'),
('Sled Push', 'Legs', 'Sled', 'Lower body power and conditioning'),
('Split Squat', 'Legs', 'Dumbbell', 'Unilateral leg exercise'),
('Tibialis Raises', 'Legs', 'Bodyweight', 'Shin strengthening'),
('Trapbar Deadlift', 'Legs', 'Trapbar', 'Back-friendly deadlift variation'),
('Walking Lunge', 'Legs', 'Dumbbell', 'Dynamic lunge pattern'),
('Zercher Squat', 'Legs', 'Barbell', 'Front-loaded squat variation'),
('Calf Raises', 'Legs', 'Machine', 'Calf isolation'),

-- Back
('Barbell Row', 'Back', 'Barbell', 'Horizontal pulling movement'),
('Dead Hangs', 'Back', 'Bodyweight', 'Grip and lat engagement'),
('Inverted Row', 'Back', 'Bodyweight', 'Horizontal bodyweight pull'),
('Landmine Single Arm Row', 'Back', 'Landmine', 'Unilateral rowing pattern'),
('Lat Pulldown - Single Arm', 'Back', 'Cable', 'Single arm lat isolation'),
('Lat Pulldown - Wide grip', 'Back', 'Cable', 'Wide grip lat development'),
('Lat Pulldown - close grip', 'Back', 'Cable', 'Close grip lat focus'),
('Pull-up', 'Back', 'Bodyweight', 'Vertical pulling exercise'),
('Reverse Hyper', 'Back', 'Machine', 'Lower back and glute strengthening'),
('Seated Cable Row', 'Back', 'Cable', 'Horizontal rowing'),
('Single Arm Lat Pulldown', 'Back', 'Cable', 'Unilateral lat work'),

-- Chest
('Close Grip BB Bench Press', 'Chest', 'Barbell', 'Tricep-focused bench press'),
('Decline DB Press', 'Chest', 'Dumbbell', 'Lower chest focus'),
('Decline Front Press', 'Chest', 'Barbell', 'Decline pressing movement'),
('Dips', 'Chest', 'Bodyweight', 'Chest and tricep compound'),
('Flat Bench Press', 'Chest', 'Barbell', 'Classic chest builder'),
('Incline DB Press', 'Chest', 'Dumbbell', 'Upper chest development'),
('Pec Fly', 'Chest', 'Machine', 'Chest isolation'),
('Push-up', 'Chest', 'Bodyweight', 'Basic pushing movement'),
('Stability ball DB press', 'Chest', 'Dumbbell', 'Unstable surface press'),
('Cable Cross', 'Chest', 'Cable', 'Cable chest fly'),
('Dumbbell Fly', 'Chest', 'Dumbbell', 'Chest stretch and contraction'),
('Deficit pushup', 'Chest', 'Bodyweight', 'Extended range push-up'),

-- Shoulders
('Cable Side Raise', 'Shoulders', 'Cable', 'Lateral deltoid isolation'),
('Landmine Front Press', 'Shoulders', 'Landmine', 'Overhead pressing variation'),
('Overhead Press', 'Shoulders', 'Barbell', 'Compound shoulder builder'),
('SA DB OH Press', 'Shoulders', 'Dumbbell', 'Single arm overhead press'),
('Shrugs', 'Shoulders', 'Dumbbell', 'Trap development'),

-- Arms
('Biceps Cable Curls', 'Arms', 'Cable', 'Bicep isolation with cable'),
('Cross Body SA Tricep Ext', 'Arms', 'Cable', 'Single arm tricep extension'),
('Dual Arm Cable OH Triceps Ext', 'Arms', 'Cable', 'Overhead tricep extension'),
('EZ Bar Curl', 'Arms', 'EZ Bar', 'Bicep curl with angled bar'),
('Jackson 5 Curls', 'Arms', 'Dumbbell', 'Multi-angle bicep curl'),
('Reverse Curls', 'Arms', 'Barbell', 'Forearm and bicep builder'),
('Triceps Extension - Decline', 'Arms', 'Dumbbell', 'Decline tricep isolation'),
('Triceps Pushdown', 'Arms', 'Cable', 'Tricep isolation'),
('Zottman Curls', 'Arms', 'Dumbbell', 'Bicep and forearm curl'),
('Decline DB Tricep Ext', 'Arms', 'Dumbbell', 'Decline tricep extension'),
('Forearm Complex', 'Arms', 'Various', 'Forearm strengthening routine'),
('Forearm banded KB/BB complex', 'Arms', 'Bands', 'Banded forearm work'),

-- Core
('Cable Chop High to Low', 'Core', 'Cable', 'Rotational core strength'),
('Cable Crunch', 'Core', 'Cable', 'Weighted ab crunch'),
('Cable Rotation', 'Core', 'Cable', 'Anti-rotation core exercise'),
('Dead Bugs', 'Core', 'Bodyweight', 'Core stability drill'),
('Hollow Hold', 'Core', 'Bodyweight', 'Anterior core isometric'),
('Leg Lifts', 'Core', 'Bodyweight', 'Lower ab exercise'),
('Leg Raises', 'Core', 'Bodyweight', 'Hanging or lying leg raise'),
('Pallof Press', 'Core', 'Cable', 'Anti-rotation press'),
('Plate V Ups', 'Core', 'Weight Plate', 'Weighted v-up variation'),
('RKC Plank', 'Core', 'Bodyweight', 'High-tension plank variation'),
('Suitcase Plate Crunch', 'Core', 'Weight Plate', 'Weighted crunch'),
('Supermans', 'Core', 'Bodyweight', 'Lower back extension'),
('L Sit Progression', 'Core', 'Bodyweight', 'Advanced core hold'),
('Landmine Rotation', 'Core', 'Landmine', 'Rotational core movement'),
('Landmine Rotational Deadlift', 'Core', 'Landmine', 'Rotational hinge pattern'),

-- Cardio
('Bear Crawl', 'Cardio', 'Bodyweight', 'Full body crawling movement'),
('Figure 8s', 'Cardio', 'Kettlebell', 'Kettlebell cardio pattern'),
('Kettlebell Swing', 'Cardio', 'Kettlebell', 'Hip hinge power exercise'),
('Medicine Ball Slams', 'Cardio', 'Medicine Ball', 'Power and conditioning'),
('Sandbag Over Shoulder', 'Cardio', 'Sandbag', 'Loaded carrying exercise'),
('VO2 Max', 'Cardio', 'Various', 'High intensity cardio intervals'),

-- Mobility
('Child''s Pose', 'Mobility', 'Bodyweight', 'Hip and back stretch'),
('Diaphragmatic Breathing', 'Mobility', 'Bodyweight', 'Breathing exercise'),
('Foam Rolling', 'Mobility', 'Foam Roller', 'Self-myofascial release'),
('Jefferson Curls', 'Mobility', 'Bodyweight', 'Spinal flexion mobility'),
('Spiderman Lunge w/ Thoracic Rotation', 'Mobility', 'Bodyweight', 'Hip mobility and rotation'),

-- Functional
('Farmer''s Carry', 'Functional', 'Dumbbell', 'Loaded carry exercise'),
('Power Clean', 'Functional', 'Barbell', 'Olympic lift variation'),
('Safety Bar Carry', 'Functional', 'Safety Bar', 'Loaded walking exercise');
