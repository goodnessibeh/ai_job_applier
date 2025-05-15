#!/bin/bash

# Set up git remote for frontend if not already set
if ! git remote get-url frontend-heroku &>/dev/null; then
  echo "Setting up Heroku remote for frontend..."
  git remote add frontend-heroku https://git.heroku.com/careerpilot-ai-frontend.git
fi

# Deploy the frontend subtree to Heroku
echo "Deploying frontend to Heroku..."
git subtree push --prefix frontend frontend-heroku main

echo "Deployment complete! Your frontend should be available at: https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/"