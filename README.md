# AI Job Applier

An AI-powered job application system that automates resume parsing, job searching, and application submission.

## Features

- **Resume Parsing**: Upload and parse resumes in PDF or DOCX format to extract skills, experience, and other information
- **Job Search**: Find relevant jobs across multiple job boards based on your skills and preferences
- **Application Customization**: Generate tailored cover letters and application responses using AI
- **Application Automation**: Submit applications automatically to job portals when possible
- **Application Tracking**: Keep track of all your job applications in one place

## Tech Stack

- **Frontend**: React, Material-UI
- **Backend**: Flask (Python)
- **AI Integration**: OpenAI API
- **Automation**: Selenium

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
   - Backend API: http://localhost:5000/api

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
   flask run
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

1. **Upload Resume**: Start by uploading your resume on the Resume Upload page
2. **Search for Jobs**: Use the search filters to find jobs that match your skills and preferences
3. **View Job Details**: Examine job details to determine if it's a good fit
4. **Apply to Jobs**: Use the AI-assisted application process to generate and submit applications
5. **Track Applications**: View your application history to keep track of submitted applications

## Limitations

- Automatic application submission may not work for all job portals due to CAPTCHA, login requirements, or other verification processes
- The AI-generated cover letters and application responses should be reviewed and edited before submission
- The job search functionality uses mock data for demonstration purposes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the API for AI-powered text generation
- Material-UI for the React component library
- All the job search platforms that inspired this project