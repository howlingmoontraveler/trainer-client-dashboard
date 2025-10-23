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

-- Link client to trainer
INSERT INTO clients (trainer_id, client_id) VALUES (1, 2);
