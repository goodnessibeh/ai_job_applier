# AI Job Applier (CareerPilot)

An AI-powered job application system that automates resume parsing, job searching, and application submission. Deployed on Heroku at https://careerpilot-ai.herokuapp.com

## Features

- **Resume Parsing**: Upload and parse resumes in PDF or DOCX format to extract skills, experience, and other information with preserved formatting
- **Resume Improvement**: Get AI-powered suggestions to improve your resume using OpenAI or Anthropic models
- **Profile Pictures**: Upload and manage profile pictures for your user account
- **Job Search**: Find relevant jobs across 20+ job boards and APIs based on your skills and preferences
- **Application Customization**: Generate tailored cover letters and application responses using AI
- **Application Automation**: Submit applications automatically to job portals when possible
- **Application Tracking**: Keep track of all your job applications in one place
- **Email Notifications**: Receive beautifully designed HTML email notifications when applications are submitted
- **Admin Dashboard**: Admin-only access to configure system settings, view user statistics, and manage application data

## Tech Stack

- **Frontend**: React, Material-UI
- **Backend**: Flask (Python)
- **AI Integration**: OpenAI API, Anthropic Claude API
- **Job APIs**: 20+ job search APIs via RapidAPI
- **Database**: SQLite (with migrations)
- **Automation**: Selenium
- **File Parsing**: PyPDF2, python-docx

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose (optional)

### Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/goodnessibeh/ai_job_applier.git
   cd ai_job_applier
   ```

2. Set up environment variables:
   - Backend: Copy `.env.example` to `.env` in the backend directory and configure your API keys
   - Frontend: The frontend uses the `.env` file for API URL configuration

### Running with Docker (Recommended)

1. Start the application with Docker Compose:
   ```
   docker-compose up
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001/api

### Manual Setup

#### Backend

1. Set up a Python virtual environment and install dependencies:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the Flask development server:
   ```
   flask run --port=5001
   ```

#### Frontend

1. Install Node.js dependencies:
   ```
   cd frontend
   npm install
   ```

2. Run the React development server:
   ```
   npm start
   ```

## Usage Guide

### Regular Users

1. **Upload Resume**: Start by uploading your resume on the Resume Upload page
2. **Improve Resume**: Get AI-powered suggestions to enhance your resume's effectiveness
3. **Profile Management**: Customize your profile with a profile picture
4. **Search for Jobs**: Use the search filters to find jobs that match your skills and preferences
5. **View Job Details**: Examine job details to determine if it's a good fit
6. **Apply to Jobs**: Use the AI-assisted application process to generate and submit applications
7. **Track Applications**: View your application history to keep track of submitted applications
8. **Email Notifications**: Receive email updates when your applications are submitted (if enabled)
9. **User Settings**: Configure your application preferences and daily application limits

### Admin Users

1. **Admin Dashboard**: Access the admin dashboard to view system statistics and user activity
2. **System Configuration**: Configure global settings like API keys (OpenAI/Anthropic), SMTP server, and application limits
3. **AI Provider Management**: Select default AI provider (OpenAI or Anthropic) for resume improvement and cover letters
4. **Email Setup**: Set up the SMTP server for email notifications and test the connection
5. **User Management**: View and manage user accounts and their application histories
6. **Application Reports**: Generate reports on application trends and success rates

## Limitations

- Automatic application submission may not work for all job portals due to CAPTCHA, login requirements, or other verification processes
- The AI-generated cover letters and application responses should be reviewed and edited before submission

## Job Search APIs

The application integrates with multiple job search APIs through RapidAPI:

- Indeed (multiple endpoints)
- Google Jobs (multiple endpoints)
- LinkedIn (multiple endpoints)
- Upwork
- Workday Jobs
- Glassdoor Jobs
- Startup Jobs
- Job Search API
- Active Jobs API
- Jobs API
- Internships API
- Hiring Manager API (provides hiring manager contact information)

All API keys are managed through the admin settings panel. No API keys are hardcoded in the application code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI and Anthropic for providing APIs for AI-powered text generation
- Material-UI for the React component library
- PDF and DOCX parsing libraries for resume extraction
- All the job search platforms that inspired this project