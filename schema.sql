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

-- Insert demo data
INSERT INTO users (username, password_hash, role, full_name, email) VALUES
('trainer1', 'scrypt:32768:8:1$xqB1VzRnFpyUycY9$026e7ca159aede32212b0675768def409ea041148b7a95357fd936743d35042641a87ae8200d5c24435603f2957454c1c4b1399bff724df330a1b8c94b6011da', 'trainer', 'John Trainer', 'john@example.com'),
('client1', 'scrypt:32768:8:1$br49hJ2xTt3N3OhS$85a9c62b271e6d1c8c05dd2457be3452ec2068f9904a61df9396e95953db2a6cc0ad6e77b70deba85f103068761411bd83a618e882f1be8254a78cbd8343a918', 'client', 'Jane Client', 'jane@example.com');

-- Link client to trainer
INSERT INTO clients (trainer_id, client_id) VALUES (1, 2);

-- Populate Exercise Library
INSERT INTO exercise_library (name, category, equipment, description) VALUES
-- Chest Exercises
('Barbell Bench Press', 'Chest', 'Barbell', 'Classic compound chest exercise'),
('Incline Barbell Bench Press', 'Chest', 'Barbell', 'Targets upper chest'),
('Decline Barbell Bench Press', 'Chest', 'Barbell', 'Targets lower chest'),
('Dumbbell Bench Press', 'Chest', 'Dumbbell', 'Allows greater range of motion'),
('Incline Dumbbell Press', 'Chest', 'Dumbbell', 'Upper chest focus'),
('Dumbbell Flyes', 'Chest', 'Dumbbell', 'Isolation exercise for chest'),
('Cable Flyes', 'Chest', 'Cable', 'Constant tension chest isolation'),
('Push-ups', 'Chest', 'Bodyweight', 'Classic bodyweight chest exercise'),
('Dips', 'Chest', 'Bodyweight', 'Compound chest and tricep exercise'),
('Chest Press Machine', 'Chest', 'Machine', 'Beginner-friendly chest press'),

-- Back Exercises
('Deadlift', 'Back', 'Barbell', 'Full body compound exercise'),
('Barbell Row', 'Back', 'Barbell', 'Horizontal pulling movement'),
('T-Bar Row', 'Back', 'Barbell', 'Thick back builder'),
('Pull-ups', 'Back', 'Bodyweight', 'Vertical pulling bodyweight exercise'),
('Chin-ups', 'Back', 'Bodyweight', 'Underhand grip pull-up variation'),
('Lat Pulldown', 'Back', 'Cable', 'Vertical pulling cable exercise'),
('Seated Cable Row', 'Back', 'Cable', 'Horizontal rowing movement'),
('Dumbbell Row', 'Back', 'Dumbbell', 'Unilateral back exercise'),
('Face Pulls', 'Back', 'Cable', 'Rear delt and upper back'),
('Hyperextensions', 'Back', 'Bodyweight', 'Lower back strengthening'),

-- Leg Exercises
('Barbell Squat', 'Legs', 'Barbell', 'King of leg exercises'),
('Front Squat', 'Legs', 'Barbell', 'Quad-focused squat variation'),
('Romanian Deadlift', 'Legs', 'Barbell', 'Hamstring and glute focus'),
('Leg Press', 'Legs', 'Machine', 'Compound leg exercise'),
('Leg Extension', 'Legs', 'Machine', 'Quad isolation'),
('Leg Curl', 'Legs', 'Machine', 'Hamstring isolation'),
('Walking Lunges', 'Legs', 'Dumbbell', 'Unilateral leg exercise'),
('Bulgarian Split Squat', 'Legs', 'Dumbbell', 'Single leg strength builder'),
('Calf Raises', 'Legs', 'Machine', 'Calf isolation exercise'),
('Goblet Squat', 'Legs', 'Dumbbell', 'Beginner-friendly squat'),

-- Shoulder Exercises
('Overhead Press', 'Shoulders', 'Barbell', 'Compound shoulder builder'),
('Dumbbell Shoulder Press', 'Shoulders', 'Dumbbell', 'Overhead pressing movement'),
('Arnold Press', 'Shoulders', 'Dumbbell', 'Rotational shoulder press'),
('Lateral Raises', 'Shoulders', 'Dumbbell', 'Side delt isolation'),
('Front Raises', 'Shoulders', 'Dumbbell', 'Front delt isolation'),
('Reverse Flyes', 'Shoulders', 'Dumbbell', 'Rear delt isolation'),
('Upright Row', 'Shoulders', 'Barbell', 'Traps and shoulders'),
('Shrugs', 'Shoulders', 'Dumbbell', 'Trap development'),
('Cable Lateral Raises', 'Shoulders', 'Cable', 'Constant tension side delts'),

-- Arm Exercises
('Barbell Curl', 'Arms', 'Barbell', 'Classic bicep builder'),
('Dumbbell Curl', 'Arms', 'Dumbbell', 'Bicep isolation'),
('Hammer Curl', 'Arms', 'Dumbbell', 'Targets brachialis'),
('Preacher Curl', 'Arms', 'Barbell', 'Isolated bicep curl'),
('Cable Curl', 'Arms', 'Cable', 'Constant tension bicep curl'),
('Tricep Pushdown', 'Arms', 'Cable', 'Tricep isolation'),
('Overhead Tricep Extension', 'Arms', 'Dumbbell', 'Long head tricep focus'),
('Skull Crushers', 'Arms', 'Barbell', 'Lying tricep extension'),
('Close Grip Bench Press', 'Arms', 'Barbell', 'Compound tricep exercise'),
('Tricep Dips', 'Arms', 'Bodyweight', 'Bodyweight tricep builder'),

-- Core Exercises
('Plank', 'Core', 'Bodyweight', 'Isometric core exercise'),
('Side Plank', 'Core', 'Bodyweight', 'Oblique strengthening'),
('Crunches', 'Core', 'Bodyweight', 'Basic ab exercise'),
('Bicycle Crunches', 'Core', 'Bodyweight', 'Dynamic ab movement'),
('Russian Twists', 'Core', 'Bodyweight', 'Oblique rotation exercise'),
('Leg Raises', 'Core', 'Bodyweight', 'Lower ab focus'),
('Mountain Climbers', 'Core', 'Bodyweight', 'Dynamic core exercise'),
('Ab Wheel Rollout', 'Core', 'Equipment', 'Advanced ab exercise'),
('Cable Woodchoppers', 'Core', 'Cable', 'Rotational core strength'),
('Dead Bug', 'Core', 'Bodyweight', 'Core stability exercise'),

-- Cardio
('Treadmill Running', 'Cardio', 'Machine', 'Cardiovascular exercise'),
('Stationary Bike', 'Cardio', 'Machine', 'Low-impact cardio'),
('Rowing Machine', 'Cardio', 'Machine', 'Full-body cardio'),
('Elliptical', 'Cardio', 'Machine', 'Low-impact cardio machine'),
('Jump Rope', 'Cardio', 'Equipment', 'High-intensity cardio'),
('Burpees', 'Cardio', 'Bodyweight', 'Full-body conditioning'),
('Battle Ropes', 'Cardio', 'Equipment', 'Upper body cardio'),
('Box Jumps', 'Cardio', 'Equipment', 'Plyometric exercise'),

-- Functional/Olympic
('Power Clean', 'Olympic', 'Barbell', 'Explosive power exercise'),
('Hang Clean', 'Olympic', 'Barbell', 'Olympic lift variation'),
('Snatch', 'Olympic', 'Barbell', 'Technical Olympic lift'),
('Kettlebell Swing', 'Functional', 'Kettlebell', 'Hip hinge power exercise'),
('Turkish Get-Up', 'Functional', 'Kettlebell', 'Full-body movement'),
('Farmers Walk', 'Functional', 'Dumbbell', 'Loaded carry exercise'),
('Sled Push', 'Functional', 'Equipment', 'Leg and conditioning exercise'),
('Medicine Ball Slam', 'Functional', 'Equipment', 'Power and core exercise');
