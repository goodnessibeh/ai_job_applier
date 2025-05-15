#!/bin/bash
# Script to create a separate frontend repository and deploy it to Heroku

# Create a temporary directory for the frontend
echo "Creating temporary directory for frontend..."
mkdir -p /tmp/careerpilot-frontend

# Copy frontend files
echo "Copying frontend files..."
cp -r frontend/* /tmp/careerpilot-frontend/

# Create .env file for production
echo "Creating environment file..."
echo "REACT_APP_API_URL=https://careerpilot-ai-530f45da3f80.herokuapp.com/api" > /tmp/careerpilot-frontend/.env.production

# Initialize git repo
echo "Initializing git repository..."
cd /tmp/careerpilot-frontend
git init
git add .
git commit -m "Initial commit of frontend code"

# Add GitHub remote
echo "Adding GitHub remote..."
git remote add origin https://github.com/goodnessibeh/careerpilot-frontend.git

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

# Add Heroku remote
echo "Adding Heroku remote..."
git remote add heroku https://git.heroku.com/careerpilot-ai-frontend.git

# Push to Heroku
echo "Pushing to Heroku..."
git push heroku main

echo "Deployment complete! Your frontend should be available at: https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/"