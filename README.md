# Trainer-Client Dashboard

A web-based dashboard for personal trainers to manage their clients and for clients to access their workout programs remotely.

## Features

### For Trainers
- Manage multiple clients
- Create custom workout programs for each client
- Schedule in-person training sessions
- Track client progress
- Add exercises with sets, reps, and notes

### For Clients
- Secure login with username and password
- View assigned workout programs
- Log workout completions with weight and notes
- See upcoming training sessions
- Access programs anytime, anywhere

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based with password hashing

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd trainer-client-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### First Time Setup

The application comes with demo accounts for testing:

**Trainer Account:**
- Username: `trainer1`
- Password: `password123`

**Client Account:**
- Username: `client1`
- Password: `password123`

### Trainer Workflow

1. **Login** as a trainer
2. **Add Clients**: Click "Add New Client" to create client accounts
3. **Create Programs**: For each client, create workout programs with exercises
4. **Schedule Sessions**: Schedule in-person training sessions
5. **View Client Details**: Monitor client progress and program adherence

### Client Workflow

1. **Login** with credentials provided by your trainer
2. **View Programs**: See all workout programs assigned to you
3. **Log Workouts**: Record your sets, reps, and weights for each exercise
4. **Check Sessions**: View upcoming training sessions with your trainer

## Database Schema

The application uses SQLite with the following tables:

- **users**: Stores trainer and client accounts
- **clients**: Links trainers with their clients
- **programs**: Workout programs assigned to clients
- **exercises**: Individual exercises within programs
- **workout_logs**: Client workout completion records
- **training_sessions**: Scheduled in-person training sessions

## Security Features

- Password hashing using Werkzeug's security utilities
- Session-based authentication
- Role-based access control (trainer vs. client)
- Protected routes requiring authentication

## File Structure

```
trainer-client-dashboard/
├── app.py                  # Main Flask application
├── schema.sql              # Database schema and seed data
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── trainer_dashboard.html
│   ├── client_dashboard.html
│   ├── add_client.html
│   ├── view_client.html
│   ├── create_program.html
│   ├── view_program.html
│   └── schedule_session.html
└── static/                # Static assets
    └── css/
        └── style.css      # Application styles
```

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard` - Main dashboard (redirects based on role)
- `GET /trainer/dashboard` - Trainer dashboard
- `GET /client/dashboard` - Client dashboard

### Trainer Functions
- `GET/POST /trainer/clients/add` - Add new client
- `GET /trainer/client/<id>` - View client details
- `GET/POST /trainer/programs/create/<client_id>` - Create workout program
- `GET/POST /trainer/session/schedule/<client_id>` - Schedule training session

### Program Management
- `GET /program/<id>` - View program details

### Client Functions
- `POST /api/log_workout` - Log workout completion (JSON API)

## Customization

### Adding New Features

The application is built with a modular structure. To add new features:

1. Add new routes in `app.py`
2. Create corresponding templates in `templates/`
3. Update `schema.sql` if new database tables are needed
4. Add styling in `static/css/style.css`

### Changing Default Credentials

To change demo credentials, update the password hashes in `schema.sql`:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('your_new_password'))
```

Then update the INSERT statements in `schema.sql` with the new hash.

## Production Deployment

For production use, consider:

1. **Change the secret key** in `app.py` to a secure random value
2. **Use PostgreSQL or MySQL** instead of SQLite for better performance
3. **Enable HTTPS** for secure communication
4. **Set up proper user registration** instead of trainer-created accounts
5. **Add email notifications** for session reminders
6. **Implement password reset functionality**
7. **Add input validation and sanitization**
8. **Set up proper logging and error handling**
9. **Use a production WSGI server** like Gunicorn instead of Flask's development server

## Troubleshooting

**Database not found:**
- The database is automatically created on first run
- If issues persist, delete `trainer_dashboard.db` and restart the application

**Cannot login:**
- Ensure you're using the correct credentials
- Check that the database was initialized properly
- Try resetting the database by deleting it and restarting

**Port already in use:**
- Change the port in `app.py`: `app.run(port=5001)`

## License

This project is provided as-is for educational and commercial use.

## Support

For issues, questions, or contributions, please contact your development team.
