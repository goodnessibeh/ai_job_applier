import requests
import logging
import json
import time
from urllib.parse import urlencode
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

def _search_linkedin(config, criteria):
    """Search for jobs using LinkedIn API
    
    Documentation: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/jobs-search
    """
    logger.info("Searching LinkedIn for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    job_type = criteria.get('job_type', '')
    
    # Convert job_type to LinkedIn format
    job_types_map = {
        'Full-time': 'F',
        'Part-time': 'P',
        'Contract': 'C',
        'Temporary': 'T',
        'Internship': 'I'
    }
    
    linkedin_job_type = job_types_map.get(job_type, '')
    
    # Prepare headers with OAuth token
    # Note: You'll need to implement OAuth flow to get this token
    headers = {
        'Authorization': f'Bearer {config.get("access_token", "")}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
    }
    
    # Prepare parameters
    params = {
        'keywords': keywords,
        'location': location,
        'count': 20  # Number of results
    }
    
    if linkedin_job_type:
        params['jobType'] = linkedin_job_type
    
    # Make the request
    try:
        response = requests.get(
            'https://api.linkedin.com/v2/jobSearch',
            headers=headers,
            params=params
        )
        
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('elements', []):
            # Extract job details
            job_id = item.get('jobId', '')
            job_details = item.get('job', {})
            company = job_details.get('companyDetails', {}).get('company', {}).get('name', 'Unknown Company')
            title = job_details.get('title', 'Unknown Position')
            
            # Get location
            location_obj = job_details.get('formattedLocation', '')
            
            # Get apply URL
            apply_url = job_details.get('applyMethod', {}).get('companyApplyUrl', f'https://www.linkedin.com/jobs/view/{job_id}')
            
            # Format job
            job = {
                'id': f"linkedin-{job_id}",
                'title': title,
                'company': company,
                'location': location_obj,
                'job_type': job_type,
                'salary': job_details.get('salaryRange', {}).get('text', ''),
                'posted_date': _format_date(job_details.get('postedAt', '')),
                'description': job_details.get('description', {}).get('text', ''),
                'url': apply_url,
                'source': 'linkedin'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"LinkedIn API error: {str(e)}")
        raise

def _search_indeed(config, criteria):
    """Search for jobs using Indeed API
    
    Documentation: https://developer.indeed.com/docs/job-search
    """
    logger.info("Searching Indeed for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    job_type = criteria.get('job_type', '')
    
    # Convert job_type to Indeed format
    job_types_map = {
        'Full-time': 'fulltime',
        'Part-time': 'parttime',
        'Contract': 'contract',
        'Temporary': 'temporary',
        'Internship': 'internship'
    }
    
    indeed_job_type = job_types_map.get(job_type, '')
    
    # Prepare parameters
    params = {
        'publisher': config.get('publisher_id', ''),
        'q': keywords,
        'l': location,
        'limit': 20,
        'userip': '1.2.3.4',  # Required by API, should be the user's IP
        'useragent': 'Mozilla/5.0',  # Required by API, should be the user's user agent
        'format': 'json',
        'v': 2  # API version
    }
    
    if indeed_job_type:
        params['jt'] = indeed_job_type
    
    # Make the request
    try:
        response = requests.get(
            'https://api.indeed.com/ads/apisearch',
            params=params
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for result in data.get('results', []):
            # Format job
            job = {
                'id': f"indeed-{result.get('jobkey', '')}",
                'title': result.get('jobtitle', 'Unknown Position'),
                'company': result.get('company', 'Unknown Company'),
                'location': result.get('formattedLocation', result.get('city', '') + ', ' + result.get('state', '')),
                'job_type': job_type,
                'salary': result.get('formattedRelativeTime', ''),
                'posted_date': result.get('formattedRelativeTime', ''),
                'description': result.get('snippet', ''),
                'url': result.get('url', ''),
                'source': 'indeed'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Indeed API error: {str(e)}")
        raise

def _search_glassdoor(config, criteria):
    """Search for jobs using Glassdoor API
    
    Documentation: https://www.glassdoor.com/developer/index.htm
    """
    logger.info("Searching Glassdoor for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare parameters
    params = {
        'v': '1',
        'format': 'json',
        't.p': config.get('partner_id', ''),
        't.k': config.get('api_key', ''),
        'action': 'jobs',
        'keyword': keywords,
        'location': location,
        'jobType': 'all',
        'returnJobListings': 'true',
        'returnEmployers': 'true',
        'returnLocations': 'true',
        'pageSize': 20
    }
    
    # Make the request
    try:
        response = requests.get(
            'https://api.glassdoor.com/api/api.htm',
            params=params
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for job in data.get('response', {}).get('jobListings', []):
            # Format job
            formatted_job = {
                'id': f"glassdoor-{job.get('jobId', '')}",
                'title': job.get('jobTitle', 'Unknown Position'),
                'company': job.get('employer', {}).get('name', 'Unknown Company'),
                'location': job.get('location', ''),
                'job_type': job.get('jobType', {}).get('name', ''),
                'salary': job.get('salarySourceText', ''),
                'posted_date': f"{job.get('daysOld', '0')} days ago",
                'description': job.get('jobDescription', ''),
                'url': job.get('jobViewUrl', ''),
                'source': 'glassdoor'
            }
            
            jobs.append(formatted_job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Glassdoor API error: {str(e)}")
        raise

def _search_monster(config, criteria):
    """Search for jobs using Monster API"""
    logger.info("Searching Monster for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers with authorization
    headers = {
        'Authorization': f"Bearer {config.get('client_secret', '')}",
        'Accept': 'application/json'
    }
    
    # Prepare parameters
    params = {
        'q': keywords,
        'where': location,
        'limit': 20
    }
    
    # Make the request
    try:
        response = requests.get(
            'https://apis.monster.com/jobs/search',
            headers=headers,
            params=params
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for job in data.get('jobs', []):
            # Format job
            formatted_job = {
                'id': f"monster-{job.get('id', '')}",
                'title': job.get('title', 'Unknown Position'),
                'company': job.get('company', {}).get('name', 'Unknown Company'),
                'location': job.get('location', {}).get('name', ''),
                'job_type': job.get('type', ''),
                'salary': '',  # Monster doesn't always provide salary
                'posted_date': _calculate_days_ago(job.get('postedDate', '')),
                'description': job.get('description', ''),
                'url': job.get('url', ''),
                'source': 'monster'
            }
            
            jobs.append(formatted_job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Monster API error: {str(e)}")
        raise

def _search_ziprecruiter(config, criteria):
    """Search for jobs using ZipRecruiter API
    
    Documentation: https://www.ziprecruiter.com/developers
    """
    logger.info("Searching ZipRecruiter for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare parameters
    params = {
        'api_key': config.get('api_key', ''),
        'search': keywords,
        'location': location,
        'page': 1,
        'jobs_per_page': 20,
        'days_ago': 30,  # Jobs posted within the last 30 days
        'refine_by_radius': 25,  # Miles
        'refine_by_salary': ''  # Optional
    }
    
    # Make the request
    try:
        response = requests.get(
            'https://api.ziprecruiter.com/jobs/v1',
            params=params
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for job in data.get('jobs', []):
            # Format job
            formatted_job = {
                'id': f"ziprecruiter-{job.get('id', '')}",
                'title': job.get('name', 'Unknown Position'),
                'company': job.get('hiring_company', {}).get('name', 'Unknown Company'),
                'location': job.get('location', ''),
                'job_type': job.get('job_type', ''),
                'salary': job.get('salary_interval', {}).get('text', ''),
                'posted_date': _calculate_days_ago(job.get('posted_time', '')),
                'description': job.get('snippet', ''),
                'url': job.get('url', ''),
                'source': 'ziprecruiter'
            }
            
            jobs.append(formatted_job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"ZipRecruiter API error: {str(e)}")
        raise

# Helper functions

def _format_date(timestamp):
    """Format a timestamp to '3 days ago' format"""
    if not timestamp:
        return "Recently"
    
    try:
        # Parse the timestamp (this depends on the format provided by LinkedIn)
        # For example, if it's in milliseconds since epoch:
        post_date = datetime.fromtimestamp(int(timestamp) / 1000)
        days_diff = (datetime.now() - post_date).days
        
        if days_diff == 0:
            return "Today"
        elif days_diff == 1:
            return "Yesterday"
        else:
            return f"{days_diff} days ago"
    except:
        return "Recently"

def _calculate_days_ago(date_str):
    """Calculate days ago from a date string"""
    if not date_str:
        return "Recently"
    
    try:
        # Parse the date (format depends on the API)
        date_formats = [
            '%Y-%m-%dT%H:%M:%S%z',  # ISO format with timezone
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with milliseconds and Z
            '%Y-%m-%d %H:%M:%S',  # Standard format
            '%Y-%m-%d',  # Just date
        ]
        
        post_date = None
        for fmt in date_formats:
            try:
                post_date = datetime.strptime(date_str, fmt)
                break
            except:
                continue
        
        if not post_date:
            return "Recently"
        
        days_diff = (datetime.now() - post_date).days
        
        if days_diff == 0:
            return "Today"
        elif days_diff == 1:
            return "Yesterday"
        else:
            return f"{days_diff} days ago"
    except:
        return "Recently"