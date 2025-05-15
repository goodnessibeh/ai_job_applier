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
    
    # Web scraping settings
    WEB_SCRAPING_ENABLED = os.environ.get('WEB_SCRAPING_ENABLED', 'True').lower() in ('true', '1', 't')
    
    # LinkedIn API settings
    LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
    LINKEDIN_REDIRECT_URI = os.environ.get('LINKEDIN_REDIRECT_URI', 'http://localhost:5001/api/auth/linkedin/callback')
    
    # Indeed API settings
    INDEED_PUBLISHER_ID = os.environ.get('INDEED_PUBLISHER_ID', '')
    INDEED_API_KEY = os.environ.get('INDEED_API_KEY', '')
    
    # Glassdoor API settings
    GLASSDOOR_PARTNER_ID = os.environ.get('GLASSDOOR_PARTNER_ID', '')
    GLASSDOOR_API_KEY = os.environ.get('GLASSDOOR_API_KEY', '')
    
    # Monster API settings
    MONSTER_CLIENT_ID = os.environ.get('MONSTER_CLIENT_ID', '')
    MONSTER_CLIENT_SECRET = os.environ.get('MONSTER_CLIENT_SECRET', '')
    
    # ZipRecruiter API settings
    ZIPRECRUITER_API_KEY = os.environ.get('ZIPRECRUITER_API_KEY', '')
    
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
    
    # Application settings
    SIMULATION_MODE = os.environ.get('SIMULATION_MODE', 'True').lower() in ('true', '1', 't')
    MAX_APPLICATIONS_PER_DAY = int(os.environ.get('MAX_APPLICATIONS_PER_DAY', '10'))
    
    @classmethod
    def get_job_portal_configs(cls):
        """Returns a dictionary of configured job portals"""
        portals = {}
        
        # LinkedIn
        if cls.LINKEDIN_CLIENT_ID and cls.LINKEDIN_CLIENT_SECRET:
            portals['linkedin'] = {
                'enabled': True,
                'client_id': cls.LINKEDIN_CLIENT_ID,
                'client_secret': cls.LINKEDIN_CLIENT_SECRET,
                'redirect_uri': cls.LINKEDIN_REDIRECT_URI
            }
        else:
            portals['linkedin'] = {'enabled': False}
            
        # Indeed
        if cls.INDEED_PUBLISHER_ID and cls.INDEED_API_KEY:
            portals['indeed'] = {
                'enabled': True,
                'publisher_id': cls.INDEED_PUBLISHER_ID,
                'api_key': cls.INDEED_API_KEY
            }
        else:
            portals['indeed'] = {'enabled': False}
            
        # Glassdoor
        if cls.GLASSDOOR_PARTNER_ID and cls.GLASSDOOR_API_KEY:
            portals['glassdoor'] = {
                'enabled': True,
                'partner_id': cls.GLASSDOOR_PARTNER_ID,
                'api_key': cls.GLASSDOOR_API_KEY
            }
        else:
            portals['glassdoor'] = {'enabled': False}
            
        return portals