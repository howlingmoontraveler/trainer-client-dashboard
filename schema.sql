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

-- Exercises within programs
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sets TEXT,
    reps TEXT,
    weight TEXT,
    notes TEXT,
    exercise_order INTEGER,
    FOREIGN KEY (program_id) REFERENCES programs(id)
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

-- Exercise library (master list of exercises)
CREATE TABLE IF NOT EXISTS exercise_library (
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
);

-- Program Templates table
CREATE TABLE IF NOT EXISTS program_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_by INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Template exercises
CREATE TABLE IF NOT EXISTS program_template_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sets TEXT,
    reps TEXT,
    notes TEXT,
    exercise_order INTEGER,
    FOREIGN KEY (template_id) REFERENCES program_templates(id) ON DELETE CASCADE
);

-- Link client to trainer
INSERT INTO clients (trainer_id, client_id) VALUES (1, 2);

-- Insert sample exercises
INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by) VALUES
('Push-ups', 'Bodyweight', 'Classic upper body exercise', 'Start in plank position, lower chest to ground, push back up', 'Chest, Shoulders, Triceps', 'None', 'beginner', 1),
('Squats', 'Bodyweight', 'Fundamental lower body exercise', 'Stand with feet shoulder-width apart, lower as if sitting, return to standing', 'Quadriceps, Glutes, Hamstrings', 'None', 'beginner', 1),
('Deadlifts', 'Weight Training', 'Hip hinge movement with weights', 'Stand with feet hip-width apart, hinge at hips, lower weight, return to standing', 'Hamstrings, Glutes, Lower Back', 'Barbell, Dumbbells', 'intermediate', 1),
('Bench Press', 'Weight Training', 'Horizontal pushing exercise', 'Lie on bench, lower bar to chest, press up', 'Chest, Shoulders, Triceps', 'Barbell, Bench', 'intermediate', 1),
('Pull-ups', 'Bodyweight', 'Vertical pulling exercise', 'Hang from bar, pull body up until chin over bar, lower with control', 'Lats, Biceps, Rear Delts', 'Pull-up Bar', 'intermediate', 1);
