# Deploying the Frontend to Heroku

Since you're experiencing issues deploying the frontend with Git subtree push, here's an alternative approach:

## Method 1: Deploy from GitHub

1. Log in to your [Heroku Dashboard](https://dashboard.heroku.com/)
2. Select the app `careerpilot-ai-frontend`
3. Go to the "Deploy" tab
4. Under "Deployment method," select "GitHub"
5. Connect to your GitHub repository
6. Scroll down to "Manual deploy" and select "main" branch
7. Click "Deploy Branch"

## Method 2: Create a separate repository for the frontend

1. Create a new directory on your local machine:
   ```
   mkdir careerpilot-frontend
   ```

2. Copy all frontend files to this directory:
   ```
   cp -r /path/to/ai_job_applier/frontend/* ./careerpilot-frontend/
   ```

3. Initialize a new git repository:
   ```
   cd careerpilot-frontend
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. Create a new Heroku app or use the existing one:
   ```
   heroku git:remote -a careerpilot-ai-frontend
   ```

5. Push to Heroku:
   ```
   git push heroku main
   ```

## Method 3: Use Heroku's buildpack-static

If you still encounter issues, try this approach:

1. Add the static buildpack to your Heroku app:
   ```
   heroku buildpacks:set heroku/nodejs --app careerpilot-ai-frontend
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-static.git --app careerpilot-ai-frontend
   ```

2. Then push your code again:
   ```
   git push heroku main
   ```

## After Deployment

Check if your frontend is working by visiting:
https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/

The admin login page will be at:
https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/admin/login