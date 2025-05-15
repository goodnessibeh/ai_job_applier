#!/bin/bash

# Push to Heroku first
echo "Pushing to Heroku..."
git push heroku main

# Check if push was successful
if [ $? -eq 0 ]; then
  echo "Heroku push successful, pushing to GitHub..."
  git push origin main
else
  echo "Heroku push failed, not pushing to GitHub"
  exit 1
fi