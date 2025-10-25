-- Phase 1 Database Migration
-- Run this to add new fields for enhanced features

-- Add extended client profile fields to users table
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users ADD COLUMN goals TEXT;
ALTER TABLE users ADD COLUMN fitness_level TEXT;
ALTER TABLE users ADD COLUMN medical_notes TEXT;

-- Add exercise metadata fields to exercise_library
ALTER TABLE exercise_library ADD COLUMN demo_url TEXT;
ALTER TABLE exercise_library ADD COLUMN instructions TEXT;
ALTER TABLE exercise_library ADD COLUMN muscle_groups TEXT;

-- Add workout template fields to exercises table
ALTER TABLE exercises ADD COLUMN tempo TEXT;
ALTER TABLE exercises ADD COLUMN rest_period TEXT;

-- Add is_template flag to programs for cloning
ALTER TABLE programs ADD COLUMN is_template BOOLEAN DEFAULT FALSE;
ALTER TABLE programs ADD COLUMN template_name TEXT;
