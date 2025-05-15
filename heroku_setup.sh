#!/bin/bash
# Heroku setup script for CareerPilot AI

# Set up Heroku PostgreSQL
echo "1. Adding PostgreSQL to Heroku app..."
echo "Running: heroku addons:create heroku-postgresql:mini --app careerpilot-ai"
heroku addons:create heroku-postgresql:mini --app careerpilot-ai

# Confirm database URL is set
echo "2. Checking database configuration..."
echo "Running: heroku config --app careerpilot-ai | grep DATABASE_URL"
heroku config --app careerpilot-ai | grep DATABASE_URL

# Initialize the database
echo "3. Initializing database..."
echo "Running: heroku run python backend/db_init.py --app careerpilot-ai"
heroku run python backend/db_init.py --app careerpilot-ai

# Restart the application
echo "4. Restarting application..."
echo "Running: heroku restart --app careerpilot-ai"
heroku restart --app careerpilot-ai

# Check logs for verification
echo "5. Displaying logs to verify successful setup..."
echo "Running: heroku logs --tail --app careerpilot-ai"
echo "Press Ctrl+C to exit logs when ready."
heroku logs --tail --app careerpilot-ai