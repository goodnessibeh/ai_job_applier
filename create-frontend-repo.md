# Creating a Standalone Repository for the Frontend

Since deploying the frontend from the monorepo is causing issues, here's how to create a standalone repository for the frontend:

1. Create a new directory on your computer:
```
mkdir careerpilot-frontend
cd careerpilot-frontend
```

2. Initialize a git repository:
```
git init
```

3. Copy all files from the frontend directory of the main project:
```
cp -r /path/to/ai_job_applier/frontend/* .
```

4. Create a new `.env` file to point to the backend API:
```
echo "REACT_APP_API_URL=https://careerpilot-ai-530f45da3f80.herokuapp.com/api" > .env
```

5. Add, commit, and push to a new GitHub repository:
```
git add .
git commit -m "Initial commit of frontend code"
git remote add origin https://github.com/goodnessibeh/careerpilot-frontend.git
git push -u origin main
```

6. Connect this new repository to your Heroku app:
```
heroku git:remote -a careerpilot-ai-frontend
git push heroku main
```

## Alternative Method: Direct Deployment

You can also deploy directly from your local machine to Heroku:

1. Make sure you're in the frontend directory:
```
cd /path/to/ai_job_applier/frontend
```

2. Initialize a git repo in this subdirectory:
```
git init
git add .
git commit -m "Initial commit"
```

3. Set the remote and push to Heroku:
```
heroku git:remote -a careerpilot-ai-frontend
git push heroku main
```

## After Deployment

Once deployed, your frontend should be accessible at:
https://careerpilot-ai-frontend-790af8a4ffad.herokuapp.com/