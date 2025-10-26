-- Users table (both trainers and clients)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('trainer', 'client')),
    full_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trainer-Client relationships
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    trainer_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trainer_id) REFERENCES users(id),
    FOREIGN KEY (client_id) REFERENCES users(id),
    UNIQUE(trainer_id, client_id)
);

-- Workout programs
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,
    program_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sets TEXT,
    reps TEXT,
    notes TEXT,
    exercise_order INTEGER,
    FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE
);

-- Exercise completion tracking
CREATE TABLE IF NOT EXISTS exercise_completions (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sets_completed INTEGER,
    notes TEXT,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);

-- Progress tracking
CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    date DATE NOT NULL,
    weight DECIMAL(5,2),
    notes TEXT,
    FOREIGN KEY (client_id) REFERENCES users(id),
    UNIQUE(client_id, date)
);

-- Exercise library for trainers
CREATE TABLE IF NOT EXISTS exercise_library (
    id SERIAL PRIMARY KEY,
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

-- Program templates
CREATE TABLE IF NOT EXISTS program_templates (
    id SERIAL PRIMARY KEY,
    created_by INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Program template exercises
CREATE TABLE IF NOT EXISTS program_template_exercises (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sets TEXT,
    reps TEXT,
    notes TEXT,
    exercise_order INTEGER,
    FOREIGN KEY (template_id) REFERENCES program_templates(id) ON DELETE CASCADE
);

-- Insert default trainer account
INSERT INTO users (username, password_hash, role, full_name, email)
VALUES ('trainer1', 'scrypt:32768:8:1$EupJLZ9eztbpGQdY$05c8ea5cd8f9f8c6e7d3b8e6c8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8', 'trainer', 'Default Trainer', 'trainer@example.com')
ON CONFLICT (username) DO NOTHING;

-- Insert default client account
INSERT INTO users (username, password_hash, role, full_name, email)
VALUES ('client1', 'scrypt:32768:8:1$EupJLZ9eztbpGQdY$05c8ea5cd8f9f8c6e7d3b8e6c8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8e8', 'client', 'Default Client', 'client@example.com')
ON CONFLICT (username) DO NOTHING;

-- Insert sample exercises
INSERT INTO exercise_library (name, category, description, instructions, muscle_groups, equipment, difficulty_level, created_by)
VALUES
('Push-up', 'Bodyweight', 'Classic upper body exercise', 'Start in plank position, lower body to ground, push back up', 'Chest, Triceps, Shoulders', 'None', 'beginner', 1),
('Squat', 'Bodyweight', 'Fundamental lower body movement', 'Stand with feet shoulder-width apart, lower hips back and down, return to standing', 'Quadriceps, Glutes, Hamstrings', 'None', 'beginner', 1),
('Plank', 'Bodyweight', 'Core stability exercise', 'Hold body in straight line on forearms and toes', 'Core, Shoulders', 'None', 'beginner', 1),
('Dumbbell Row', 'Weight Training', 'Back strengthening exercise', 'Bend at waist, pull dumbbell to ribcage', 'Back, Biceps', 'Dumbbells', 'intermediate', 1),
('Deadlift', 'Weight Training', 'Full body compound movement', 'Lift barbell from ground to standing position', 'Back, Glutes, Hamstrings, Core', 'Barbell', 'intermediate', 1)
ON CONFLICT DO NOTHING;
