-- Phase 1 Database Migration
-- Run this to add new fields for enhanced features
-- Safe to run multiple times

-- Add extended client profile fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS goals TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS fitness_level TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS medical_notes TEXT;

-- Add exercise metadata fields to exercise_library
ALTER TABLE exercise_library ADD COLUMN IF NOT EXISTS demo_url TEXT;
ALTER TABLE exercise_library ADD COLUMN IF NOT EXISTS instructions TEXT;
ALTER TABLE exercise_library ADD COLUMN IF NOT EXISTS muscle_groups TEXT;

-- Add workout template fields to exercises table
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS tempo TEXT;
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS rest_period TEXT;

-- Add is_template flag to programs for cloning
ALTER TABLE programs ADD COLUMN IF NOT EXISTS is_template BOOLEAN DEFAULT FALSE;
ALTER TABLE programs ADD COLUMN IF NOT EXISTS template_name TEXT;
