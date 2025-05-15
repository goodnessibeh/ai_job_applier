import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'development-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Database settings
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    
    # AI API settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    USE_ANTHROPIC = os.environ.get('USE_ANTHROPIC', 'True').lower() in ('true', '1', 't')
    
    # Web scraping settings - disabled by default
    WEB_SCRAPING_ENABLED = os.environ.get('WEB_SCRAPING_ENABLED', 'False').lower() in ('true', '1', 't')
    
    # RapidAPI settings
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')
    
    # Job API endpoints
    INDEED_API_HOST = os.environ.get('INDEED_API_HOST', 'indeed46.p.rapidapi.com')
    UPWORK_API_HOST = os.environ.get('UPWORK_API_HOST', 'upwork-jobs.p.rapidapi.com')
    GOOGLE_JOBS_API_HOST = os.environ.get('GOOGLE_JOBS_API_HOST', 'google-jobs-api.p.rapidapi.com')
    WORKDAY_JOBS_API_HOST = os.environ.get('WORKDAY_JOBS_API_HOST', 'workday-jobs-api.p.rapidapi.com')
    GLASSDOOR_API_HOST = os.environ.get('GLASSDOOR_API_HOST', 'glassdoor-jobs-scraper-api.p.rapidapi.com')
    STARTUP_JOBS_API_HOST = os.environ.get('STARTUP_JOBS_API_HOST', 'startup-jobs-api.p.rapidapi.com')
    JOB_SEARCH_API_HOST = os.environ.get('JOB_SEARCH_API_HOST', 'job-search-api2.p.rapidapi.com')
    INTERNSHIPS_API_HOST = os.environ.get('INTERNSHIPS_API_HOST', 'internships-api.p.rapidapi.com')
    ACTIVE_JOBS_API_HOST = os.environ.get('ACTIVE_JOBS_API_HOST', 'active-jobs-db.p.rapidapi.com')
    
    # Additional job API endpoints
    INDEED_JOBS_API_HOST = os.environ.get('INDEED_JOBS_API_HOST', 'indeed-jobs-api.p.rapidapi.com')
    JOBS_API_HOST = os.environ.get('JOBS_API_HOST', 'jobs-api22.p.rapidapi.com')
    LINKEDIN_JOB_SEARCH_API_HOST = os.environ.get('LINKEDIN_JOB_SEARCH_API_HOST', 'linkedin-job-search-api.p.rapidapi.com')
    LINKEDIN_JOB_API_HOST = os.environ.get('LINKEDIN_JOB_API_HOST', 'linkedin-job-api.p.rapidapi.com')
    GOOGLE_JOBS_API2_HOST = os.environ.get('GOOGLE_JOBS_API2_HOST', 'google-jobs-api.p.rapidapi.com')
    WORKDAY_JOBS_API2_HOST = os.environ.get('WORKDAY_JOBS_API2_HOST', 'workday-jobs-api.p.rapidapi.com')
    GLASSDOOR_JOBS_API2_HOST = os.environ.get('GLASSDOOR_JOBS_API2_HOST', 'glassdoor-jobs-scraper-api.p.rapidapi.com')
    STARTUP_JOBS_API2_HOST = os.environ.get('STARTUP_JOBS_API2_HOST', 'startup-jobs-api.p.rapidapi.com')
    JOB_SEARCH_API2_HOST = os.environ.get('JOB_SEARCH_API2_HOST', 'job-search-api2.p.rapidapi.com')
    HIRING_MANAGER_API_HOST = os.environ.get('HIRING_MANAGER_API_HOST', 'hiring-manager-api.p.rapidapi.com')
    
    # Selenium/Chrome settings
    CHROME_DRIVER_PATH = os.environ.get('CHROME_DRIVER_PATH', '')
    HEADLESS_BROWSER = os.environ.get('HEADLESS_BROWSER', 'True').lower() in ('true', '1', 't')
    
    # Email notification settings
    SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', '')
    NOTIFICATIONS_ENABLED = os.environ.get('NOTIFICATIONS_ENABLED', 'False').lower() in ('true', '1', 't')
    
    # Authentication settings
    TOKEN_EXPIRY_HOURS = int(os.environ.get('TOKEN_EXPIRY_HOURS', '24'))
    
    # LinkedIn OAuth settings
    LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
    LINKEDIN_REDIRECT_URI = os.environ.get('LINKEDIN_REDIRECT_URI', '')
    
    # Application settings
    SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'False').lower() in ('true', '1', 't')
    MAX_APPLICATIONS_PER_DAY = int(os.environ.get('MAX_APPLICATIONS_PER_DAY', '10'))
    
    @classmethod
    def get_job_portal_configs(cls):
        """Returns a dictionary of configured job portals"""
        portals = {}
        
        # RapidAPI
        if cls.RAPIDAPI_KEY:
            # Original APIs
            
            # Indeed API
            portals['indeed'] = {
                'enabled': True,
                'host': cls.INDEED_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://indeed46.p.rapidapi.com/job'
            }
            
            # Upwork API
            portals['upwork'] = {
                'enabled': True,
                'host': cls.UPWORK_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://upwork-jobs.p.rapidapi.com/jobs'
            }
            
            # Google Jobs API
            portals['google'] = {
                'enabled': True,
                'host': cls.GOOGLE_JOBS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://google-jobs-api.p.rapidapi.com/google-jobs/job-type'
            }
            
            # Workday Jobs API
            portals['workday'] = {
                'enabled': True,
                'host': cls.WORKDAY_JOBS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://workday-jobs-api.p.rapidapi.com/active-ats-24h'
            }
            
            # Glassdoor API
            portals['glassdoor'] = {
                'enabled': True,
                'host': cls.GLASSDOOR_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://glassdoor-jobs-scraper-api.p.rapidapi.com/api/job/wait'
            }
            
            # Startup Jobs API
            portals['startup'] = {
                'enabled': True,
                'host': cls.STARTUP_JOBS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://startup-jobs-api.p.rapidapi.com/active-jb-7d'
            }
            
            # Job Search API
            portals['job_search'] = {
                'enabled': True,
                'host': cls.JOB_SEARCH_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://job-search-api2.p.rapidapi.com/active-ats-expired'
            }
            
            # Internships API
            portals['internships'] = {
                'enabled': True,
                'host': cls.INTERNSHIPS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://internships-api.p.rapidapi.com/active-jb-7d'
            }
            
            # Active Jobs API
            portals['active_jobs'] = {
                'enabled': True,
                'host': cls.ACTIVE_JOBS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://active-jobs-db.p.rapidapi.com/active-ats-1h'
            }
            
            # New APIs
            
            # Indeed Jobs API (additional provider)
            portals['indeed_api'] = {
                'enabled': True,
                'host': cls.INDEED_JOBS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://indeed-jobs-api.p.rapidapi.com/indeed-us/'
            }
            
            # Jobs API
            portals['jobs_api'] = {
                'enabled': True,
                'host': cls.JOBS_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://jobs-api22.p.rapidapi.com/tags'
            }
            
            # LinkedIn Job Search API
            portals['linkedin_search'] = {
                'enabled': True,
                'host': cls.LINKEDIN_JOB_SEARCH_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d'
            }
            
            # LinkedIn Job API
            portals['linkedin_job'] = {
                'enabled': True,
                'host': cls.LINKEDIN_JOB_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://linkedin-job-api.p.rapidapi.com/job/search'
            }
            
            # Google Jobs API (additional provider)
            portals['google_jobs'] = {
                'enabled': True,
                'host': cls.GOOGLE_JOBS_API2_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://google-jobs-api.p.rapidapi.com/google-jobs/job-type'
            }
            
            # Workday Jobs API (additional provider)
            portals['workday_jobs'] = {
                'enabled': True,
                'host': cls.WORKDAY_JOBS_API2_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://workday-jobs-api.p.rapidapi.com/active-ats-24h'
            }
            
            # Glassdoor Jobs API (additional provider)
            portals['glassdoor_jobs'] = {
                'enabled': True,
                'host': cls.GLASSDOOR_JOBS_API2_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://glassdoor-jobs-scraper-api.p.rapidapi.com/api/job/wait'
            }
            
            # Startup Jobs API (additional provider)
            portals['startup_jobs'] = {
                'enabled': True,
                'host': cls.STARTUP_JOBS_API2_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://startup-jobs-api.p.rapidapi.com/active-jb-7d'
            }
            
            # Job Search API (additional provider)
            portals['job_search_api'] = {
                'enabled': True,
                'host': cls.JOB_SEARCH_API2_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://job-search-api2.p.rapidapi.com/active-ats-expired'
            }
            
            # Hiring Manager API
            portals['hiring_manager'] = {
                'enabled': True,
                'host': cls.HIRING_MANAGER_API_HOST,
                'api_key': cls.RAPIDAPI_KEY,
                'url': 'https://hiring-manager-api.p.rapidapi.com/recruitment-manager-24h'
            }
        else:
            # If no RapidAPI key, disable all portals
            portal_list = [
                'indeed', 'upwork', 'google', 'workday', 'glassdoor', 'startup', 
                'job_search', 'internships', 'active_jobs', 'indeed_api', 'jobs_api', 
                'linkedin_search', 'linkedin_job', 'google_jobs', 'workday_jobs', 
                'glassdoor_jobs', 'startup_jobs', 'job_search_api', 'hiring_manager'
            ]
            for portal in portal_list:
                portals[portal] = {'enabled': False}
                
        return portals