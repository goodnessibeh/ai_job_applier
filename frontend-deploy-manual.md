# Manual Frontend Deployment Guide

Since you've already created the GitHub repository "careerpilot-frontend", follow these steps to deploy your frontend:

## Step 1: Clone the main repository and create a new one
```bash
# Clone your main repository if you haven't already
git clone https://github.com/goodnessibeh/ai_job_applier.git
cd ai_job_applier

# Create a new directory for the frontend
mkdir ../careerpilot-frontend
cp -r frontend/* ../careerpilot-frontend/

# Create .env.production file
echo "REACT_APP_API_URL=https://careerpilot-ai-530f45da3f80.herokuapp.com/api" > ../careerpilot-frontend/.env.production

# Copy our static.json file
cp frontend/static.json ../careerpilot-frontend/
```

## Step 2: Initialize the new repo and push to GitHub
```bash
# Initialize the new repository
cd ../careerpilot-frontend
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit of frontend code"

# Add remote and push
git remote add origin https://github.com/goodnessibeh/careerpilot-frontend.git
git push -u origin main
```

## Step 3: Configure Heroku buildpacks
```bash
# Login to Heroku if you haven't already
heroku login

# Set the remote for your Heroku app
heroku git:remote -a careerpilot-ai-frontend

# Set the buildpack to Node.js
heroku buildpacks:set heroku/nodejs
```

## Step 4: Deploy to Heroku
```bash
# Push to Heroku
git push heroku main
```

## Step 5: Verify the deployment
Visit https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/ to check if your frontend is working properly.

The admin login should be available at:
https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/admin/login

## Troubleshooting

If you encounter issues:

1. **Check Heroku logs**:
```bash
heroku logs --tail
```

2. **Ensure buildpacks are correct**:
```bash
heroku buildpacks
```

3. **Verify environment variables**:
```bash
heroku config
```

4. **Set environment variables if needed**:
```bash
heroku config:set REACT_APP_API_URL=https://careerpilot-ai-530f45da3f80.herokuapp.com/api
```