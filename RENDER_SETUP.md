# Render Setup Guide - Fix Data Persistence

## Problem
Ralph and other clients disappear when you log back in because SQLite databases on Render's free tier don't persist - the filesystem is ephemeral and gets wiped on every restart/redeploy.

## Solution
Use PostgreSQL on Render (free tier available) for persistent data storage.

## Setup Steps

### 1. Create a PostgreSQL Database on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `trainer-dashboard-db`
   - **Database**: `trainer_dashboard`
   - **User**: (auto-generated)
   - **Region**: Same as your web service (Oregon/Ohio)
   - **Plan**: Free
4. Click "Create Database"
5. Wait for it to provision (takes ~1 minute)
6. **Copy the "Internal Database URL"** (starts with `postgres://`)

### 2. Connect Your Web Service to PostgreSQL

1. Go to your web service: https://dashboard.render.com/web/YOUR_SERVICE
2. Click "Environment" in the left sidebar
3. Add a new environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL you copied
4. Click "Save Changes"

### 3. Initialize the Database

Your app will automatically detect the `DATABASE_URL` and use PostgreSQL instead of SQLite. However, you need to initialize the schema:

**Option A - Via Render Shell (Recommended):**
1. In your web service dashboard, click "Shell" tab
2. Run: `python3 -c "from app import init_db; init_db()"`
3. This creates all tables and inserts demo data

**Option B - Manually via psql:**
1. In PostgreSQL database dashboard, click "Connect" → "External Connection"
2. Use the PSQL command shown
3. Copy/paste the SQL from `schema.sql` (adapt for PostgreSQL if needed)

### 4. Create Your Admin Account

After initializing, you'll need to recreate your trainer account and clients:

1. Log in with demo credentials:
   - Username: `trainer1`
   - Password: `password123`
2. Add your clients (like Ralph)
3. Create their programs

### 5. Optional - Set a Persistent SECRET_KEY

Add another environment variable:
- **Key**: `SECRET_KEY`
- **Value**: A random string (e.g., `python3 -c "import os; print(os.urandom(24).hex())"`)

This ensures sessions persist across restarts.

## Verification

After setup:
1. Add a client (like Ralph)
2. Restart your web service (Settings → "Manual Deploy")
3. Log back in - Ralph should still be there!

## Current Code Status

The code has been updated to support both:
- **SQLite** for local development
- **PostgreSQL** for Render (when `DATABASE_URL` environment variable is present)

Requirements have been updated to include `psycopg2-binary==2.9.9` for PostgreSQL support.

## Need Help?

If you encounter issues:
1. Check Render logs: Dashboard → your service → "Logs" tab
2. Verify DATABASE_URL is set correctly in Environment variables
3. Make sure the PostgreSQL database is in "Available" status
