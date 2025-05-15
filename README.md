# CareerPilot Backend API

Backend API server for the CareerPilot job application automation platform.

## Features

- User authentication and profile management
- Resume parsing and improvement suggestions
- Automated job search across multiple platforms
- Application tracking and analytics
- Admin dashboard for system management

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```
   python wsgi.py
   ```

## API Documentation

API documentation is available at /api/docs when running the server.

## Environment Variables

- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SECRET_KEY`: Secret key for JWT token generation
- `MAIL_SERVER`: SMTP server for email notifications
- `MAIL_PORT`: SMTP port
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_USE_TLS`: Use TLS for SMTP (true/false)
- `LINKEDIN_CLIENT_ID`: LinkedIn OAuth client ID
- `LINKEDIN_CLIENT_SECRET`: LinkedIn OAuth client secret

## Deployment

This application is configured for deployment to Heroku:

1. Create a Heroku app:
   ```
   heroku create careerpilot-ai
   ```

2. Set up PostgreSQL:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. Configure environment variables:
   ```
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set FLASK_ENV=production
   ```

4. Deploy:
   ```
   git push heroku main
   ```

5. Initialize the database:
   ```
   heroku run python backend/db_init.py
   ```