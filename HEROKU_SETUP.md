# Heroku Setup Guide

This guide explains how to set up your application on Heroku properly with PostgreSQL support.

## Adding PostgreSQL to Your Heroku App

1. **Login to Heroku**
   ```
   heroku login
   ```

2. **Add PostgreSQL**
   ```
   heroku addons:create heroku-postgresql:mini --app careerpilot-ai
   ```

3. **Initialize the database**
   ```
   heroku run python backend/db_init.py --app careerpilot-ai
   ```

4. **Restart the app**
   ```
   heroku restart --app careerpilot-ai
   ```

## Monitoring

You can monitor the application logs to see what's happening:

```
heroku logs --tail --app careerpilot-ai
```

## Common Issues

1. **Database connection errors**
   - Make sure the PostgreSQL add-on is properly attached
   - Check if the DATABASE_URL environment variable is set correctly:
     ```
     heroku config --app careerpilot-ai
     ```

2. **"table already exists" errors**
   - The application now includes safeguards against this
   - You can manually reset the database if needed:
     ```
     heroku pg:reset DATABASE --confirm careerpilot-ai
     heroku run python backend/db_init.py --app careerpilot-ai
     ```

3. **Application crashes after startup**
   - Check logs for specific errors: `heroku logs --app careerpilot-ai`
   - Set DEBUG mode to see more details:
     ```
     heroku config:set FLASK_DEBUG=1 --app careerpilot-ai
     heroku restart --app careerpilot-ai
     ```

## Moving from SQLite to PostgreSQL

The updated application code now detects which database to use:
- On Heroku, it will use PostgreSQL through the DATABASE_URL environment variable
- Locally, it will continue to use SQLite

When deploying to Heroku:
1. The PostgreSQL add-on provides a DATABASE_URL variable
2. The application automatically configures the proper connection
3. Tables are created only if they don't already exist