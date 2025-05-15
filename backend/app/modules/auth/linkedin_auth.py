import os
import json
import requests
import logging
import uuid
import base64
from urllib.parse import urlencode
from flask import session, redirect, url_for, request
from app.config import Config

# Setup logging
logger = logging.getLogger(__name__)

class LinkedInOAuth:
    """Class to handle LinkedIn OAuth process"""
    
    def __init__(self):
        self.client_id = Config.LINKEDIN_CLIENT_ID
        self.client_secret = Config.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = Config.LINKEDIN_REDIRECT_URI
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.user_info_url = "https://api.linkedin.com/v2/me"
        self.email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        self.profile_url = "https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
        self.scopes = ["r_liteprofile", "r_emailaddress", "w_member_social"]
    
    def get_auth_url(self):
        """Generate LinkedIn authorization URL"""
        if not self.client_id or not self.redirect_uri:
            logger.error("LinkedIn OAuth client_id or redirect_uri not configured")
            return None
        
        # Generate a random state string for CSRF protection
        state = str(uuid.uuid4())
        session['linkedin_auth_state'] = state
        
        # Build authorization URL
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': ' '.join(self.scopes)
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url
    
    def get_access_token(self, auth_code, state):
        """Exchange authorization code for access token"""
        # Verify state parameter to prevent CSRF
        if state != session.get('linkedin_auth_state'):
            logger.error("LinkedIn OAuth state mismatch")
            return None
        
        if not self.client_id or not self.client_secret:
            logger.error("LinkedIn OAuth client_id or client_secret not configured")
            return None
        
        # Prepare token request
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            # Request access token
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            # Parse token response
            token_data = response.json()
            
            # Store token information
            session['linkedin_access_token'] = token_data.get('access_token')
            session['linkedin_token_expiry'] = token_data.get('expires_in')
            
            return token_data
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn access token: {str(e)}")
            return None
    
    def get_user_profile(self, access_token=None):
        """Get user profile information"""
        if not access_token:
            access_token = session.get('linkedin_access_token')
        
        if not access_token:
            logger.error("No LinkedIn access token available")
            return None
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            # Get basic profile info
            profile_response = requests.get(self.profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get email address
            email_response = requests.get(self.email_url, headers=headers)
            email_response.raise_for_status()
            email_data = email_response.json()
            
            # Extract profile details
            first_name = profile_data.get('firstName', {}).get('localized', {}).get('en_US', '')
            last_name = profile_data.get('lastName', {}).get('localized', {}).get('en_US', '')
            user_id = profile_data.get('id', '')
            
            # Extract email
            email = None
            if 'elements' in email_data and email_data['elements']:
                email_handle = email_data['elements'][0].get('handle~', {}).get('emailAddress', '')
                if email_handle:
                    email = email_handle
            
            # Build profile data
            user_profile = {
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'full_name': f"{first_name} {last_name}",
                'email': email,
                'provider': 'linkedin',
                'access_token': access_token
            }
            
            # Store profile in session
            session['linkedin_profile'] = user_profile
            
            return user_profile
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn user profile: {str(e)}")
            return None
    
    def is_authenticated(self):
        """Check if user is authenticated with LinkedIn"""
        return bool(session.get('linkedin_access_token') and session.get('linkedin_profile'))