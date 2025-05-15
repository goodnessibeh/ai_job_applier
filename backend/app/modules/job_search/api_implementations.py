import requests
import logging
import json
import time
from urllib.parse import urlencode
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger(__name__)

# Dictionary to store hiring manager data for jobs
hiring_manager_cache = {}

def _search_indeed(config, criteria):
    """Search for jobs using Indeed API via RapidAPI
    
    API: https://rapidapi.com/indeed46-indeed46-default/api/indeed46
    """
    logger.info("Searching Indeed for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'indeed46.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'country': 'US',
        'sort': '-1',  # sort by relevance
        'page_size': '20'
    }
    
    if location:
        querystring['location'] = location
    
    if keywords:
        querystring['query'] = keywords
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://indeed46.p.rapidapi.com/job'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('items', []):
            # Extract job details
            job = {
                'id': f"indeed-{item.get('job_id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company_name', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('job_type', ''),
                'salary': item.get('salary', ''),
                'posted_date': item.get('posted_at', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'indeed'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Indeed API error: {str(e)}")
        return []

def _search_upwork(config, criteria):
    """Search for jobs using Upwork API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/upwork-jobs
    """
    logger.info("Searching Upwork for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'upwork-jobs.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://upwork-jobs.p.rapidapi.com/jobs'),
            headers=headers
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Check if job title matches keywords
            if keywords and not any(keyword.lower() in item.get('title', '').lower() for keyword in keywords.split()):
                continue
                
            # Format job
            job = {
                'id': f"upwork-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': 'Upwork Client',
                'location': 'Remote',
                'job_type': item.get('type', 'Contract'),
                'salary': item.get('budget', {}).get('amount', ''),
                'posted_date': _format_date(item.get('date_created', '')),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'upwork'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Upwork API error: {str(e)}")
        return []

def _search_google_jobs(config, criteria):
    """Search for jobs using Google Jobs API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/google-jobs-api
    """
    logger.info("Searching Google Jobs for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    job_type = criteria.get('job_type', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'google-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if job_type:
        querystring['jobType'] = job_type
    
    if keywords:
        querystring['include'] = keywords
    
    if location:
        querystring['location'] = location
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://google-jobs-api.p.rapidapi.com/google-jobs/job-type'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"google-{hash(item.get('title', '') + item.get('company', ''))}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('jobType', ''),
                'salary': item.get('salary', ''),
                'posted_date': item.get('posted', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'google'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Google Jobs API error: {str(e)}")
        return []

def _search_workday(config, criteria):
    """Search for jobs using Workday Jobs API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/workday-jobs-api
    """
    logger.info("Searching Workday for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'workday-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if keywords:
        querystring['title_filter'] = f'"{keywords}"'
    
    if location:
        querystring['location_filter'] = f'"{location}"'
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://workday-jobs-api.p.rapidapi.com/active-ats-24h'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"workday-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': 'Full-time',  # Default to full-time
                'salary': item.get('salary', ''),
                'posted_date': item.get('posted_date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'workday'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Workday API error: {str(e)}")
        return []

def _search_glassdoor(config, criteria):
    """Search for jobs using Glassdoor API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/glassdoor-jobs-scraper-api
    """
    logger.info("Searching Glassdoor for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'glassdoor-jobs-scraper-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', ''),
        'Content-Type': 'application/json'
    }
    
    # Prepare request data
    payload = {
        "scraper": {
            "filters": {
                "country": "us",
                "keyword": keywords,
                "location": location or "United States"
            },
            "maxRows": 20
        }
    }
    
    # Make the request
    try:
        response = requests.post(
            config.get('url', 'https://glassdoor-jobs-scraper-api.p.rapidapi.com/api/job/wait'),
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('data', {}).get('jobs', []):
            # Format job
            job = {
                'id': f"glassdoor-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('jobType', ''),
                'salary': item.get('salary', ''),
                'posted_date': item.get('postedDate', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'glassdoor'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Glassdoor API error: {str(e)}")
        return []

def _search_startup_jobs(config, criteria):
    """Search for jobs using Startup Jobs API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/startup-jobs-api
    """
    logger.info("Searching Startup Jobs for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'startup-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'source': 'ycombinator'
    }
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://startup-jobs-api.p.rapidapi.com/active-jb-7d'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Check if job title matches keywords
            if keywords and not any(keyword.lower() in item.get('title', '').lower() for keyword in keywords.split()):
                continue
                
            # Format job
            job = {
                'id': f"startup-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': 'Full-time',  # Startups typically hire full-time
                'salary': '',  # Startups typically don't list salary
                'posted_date': item.get('date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'startup'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Startup Jobs API error: {str(e)}")
        return []

def _search_job_search(config, criteria):
    """Search for jobs using Job Search API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/job-search-api2
    """
    logger.info("Searching Job Search API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'job-search-api2.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if keywords:
        querystring['title_filter'] = keywords
        
    if location:
        querystring['location_filter'] = location
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://job-search-api2.p.rapidapi.com/active-ats-expired'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"jobsearch-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('job_type', ''),
                'salary': item.get('salary', ''),
                'posted_date': item.get('date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'jobsearch'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Job Search API error: {str(e)}")
        return []

def _search_internships(config, criteria):
    """Search for jobs using Internships API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/internships-api
    """
    logger.info("Searching Internships API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'internships-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://internships-api.p.rapidapi.com/active-jb-7d'),
            headers=headers
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Check if job matches criteria
            if keywords and not any(keyword.lower() in item.get('title', '').lower() for keyword in keywords.split()):
                continue
                
            if location and location.lower() not in item.get('location', '').lower():
                continue
                
            # Format job
            job = {
                'id': f"internship-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': 'Internship',
                'salary': item.get('salary', ''),
                'posted_date': item.get('date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'internship'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Internships API error: {str(e)}")
        return []

def _search_active_jobs(config, criteria):
    """Search for jobs using Active Jobs API via RapidAPI
    
    API: https://rapidapi.com/desolateventure/api/active-jobs-db
    """
    logger.info("Searching Active Jobs API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'active-jobs-db.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'offset': '0',
        'description_type': 'text'
    }
    
    if keywords:
        querystring['title_filter'] = f'"{keywords}"'
        
    if location:
        querystring['location_filter'] = f'"{location}"'
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://active-jobs-db.p.rapidapi.com/active-ats-1h'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"activejob-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('type', 'Full-time'),
                'salary': item.get('salary', ''),
                'posted_date': 'Today',  # Active jobs are posted within the last hour
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'activejobs'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Active Jobs API error: {str(e)}")
        return []

def _search_indeed_api(config, criteria):
    """Search for jobs using Indeed Jobs API via RapidAPI
    
    API: https://rapidapi.com/indeed-jobs-api.p.rapidapi.com
    """
    logger.info("Searching Indeed Jobs API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'indeed-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'offset': '0'
    }
    
    if keywords:
        querystring['keyword'] = keywords
        
    if location:
        querystring['location'] = location
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://indeed-jobs-api.p.rapidapi.com/indeed-us/'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"indeed-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('type', 'Full-time'),
                'salary': item.get('salary', ''),
                'posted_date': item.get('date_posted', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'indeed-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Indeed Jobs API error: {str(e)}")
        return []

def _search_jobs_api(config, criteria):
    """Search for jobs using Jobs API via RapidAPI
    
    API: https://rapidapi.com/jobs-api22.p.rapidapi.com
    """
    logger.info("Searching Jobs API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'jobs-api22.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if keywords:
        querystring['skill'] = keywords
        
    if location:
        querystring['locations'] = location
    
    # Optional parameters - defaults for better results
    querystring['levels'] = 'Entry'
    querystring['industry'] = 'Technology'
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://jobs-api22.p.rapidapi.com/tags'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"jobs-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('type', 'Full-time'),
                'salary': item.get('salary', ''),
                'posted_date': item.get('date_posted', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'jobs-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Jobs API error: {str(e)}")
        return []

def _search_linkedin_api(config, criteria):
    """Search for jobs using LinkedIn API via RapidAPI
    
    API: https://rapidapi.com/linkedin-job-search-api.p.rapidapi.com
    """
    logger.info("Searching LinkedIn API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'linkedin-job-search-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'limit': '10',
        'offset': '0'
    }
    
    if keywords:
        querystring['title_filter'] = f'"{keywords}"'
        
    if location:
        querystring['location_filter'] = f'"{location}"'
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"linkedin-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('type', 'Full-time'),
                'salary': item.get('salary', ''),
                'posted_date': item.get('date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'linkedin-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"LinkedIn API error: {str(e)}")
        return []

def _search_linkedin_job_api(config, criteria):
    """Search for jobs using LinkedIn Job API via RapidAPI
    
    API: https://rapidapi.com/linkedin-job-api.p.rapidapi.com
    """
    logger.info("Searching LinkedIn Job API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'linkedin-job-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'page': '1'
    }
    
    if keywords:
        querystring['keyword'] = keywords
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://linkedin-job-api.p.rapidapi.com/job/search'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('data', []):
            # Format job
            job = {
                'id': f"linkedin-job-api-{item.get('jobId', '')}",
                'title': item.get('jobTitle', 'Unknown Position'),
                'company': item.get('companyName', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': 'Full-time',  # Default if not provided
                'salary': '',  # Not typically provided
                'posted_date': item.get('postedAt', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('jobUrl', ''),
                'source': 'linkedin-job-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"LinkedIn Job API error: {str(e)}")
        return []

def _search_google_jobs_api(config, criteria):
    """Search for jobs using Google Jobs API via RapidAPI (additional provider)
    
    API: https://rapidapi.com/google-jobs-api.p.rapidapi.com
    """
    logger.info("Searching Google Jobs API for jobs")
    
    # Extract criteria
    job_type = criteria.get('job_type', 'Full-time')
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'google-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if job_type:
        querystring['jobType'] = job_type
        
    if keywords:
        querystring['include'] = keywords
        
    if location:
        querystring['location'] = location
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://google-jobs-api.p.rapidapi.com/google-jobs/job-type'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"google-jobs-api-{hash(item.get('title', '') + item.get('company', ''))}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('jobType', 'Full-time'),
                'salary': item.get('salary', ''),
                'posted_date': item.get('posted', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'google-jobs-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Google Jobs API error: {str(e)}")
        return []

def _search_workday_jobs_api(config, criteria):
    """Search for jobs using Workday Jobs API via RapidAPI (additional provider)
    
    API: https://rapidapi.com/workday-jobs-api.p.rapidapi.com
    """
    logger.info("Searching Workday Jobs API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'workday-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if keywords:
        querystring['title_filter'] = f'"{keywords}"'
        
    if location:
        querystring['location_filter'] = f'"{location}"'
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://workday-jobs-api.p.rapidapi.com/active-ats-24h'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"workday-jobs-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': 'Full-time',  # Default to full-time
                'salary': item.get('salary', ''),
                'posted_date': item.get('posted_date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'workday-jobs-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Workday Jobs API error: {str(e)}")
        return []

def _search_glassdoor_jobs_api(config, criteria):
    """Search for jobs using Glassdoor Jobs API via RapidAPI (additional provider)
    
    API: https://rapidapi.com/glassdoor-jobs-scraper-api.p.rapidapi.com
    """
    logger.info("Searching Glassdoor Jobs API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'glassdoor-jobs-scraper-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', ''),
        'Content-Type': 'application/json'
    }
    
    # Prepare request data
    payload = {
        "scraper": {
            "filters": {
                "country": "us",
                "keyword": keywords,
                "location": location or "United States"
            },
            "maxRows": 20
        }
    }
    
    # Make the request
    try:
        response = requests.post(
            config.get('url', 'https://glassdoor-jobs-scraper-api.p.rapidapi.com/api/job/wait'),
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('data', {}).get('jobs', []):
            # Format job
            job = {
                'id': f"glassdoor-jobs-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('jobType', ''),
                'salary': item.get('salary', ''),
                'posted_date': item.get('postedDate', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'glassdoor-jobs-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Glassdoor Jobs API error: {str(e)}")
        return []

def _search_startup_jobs_api(config, criteria):
    """Search for jobs using Startup Jobs API via RapidAPI (additional provider)
    
    API: https://rapidapi.com/startup-jobs-api.p.rapidapi.com
    """
    logger.info("Searching Startup Jobs API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'startup-jobs-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {
        'source': 'ycombinator'
    }
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://startup-jobs-api.p.rapidapi.com/active-jb-7d'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Check if job title matches keywords
            if keywords and not any(keyword.lower() in item.get('title', '').lower() for keyword in keywords.split()):
                continue
                
            # Format job
            job = {
                'id': f"startup-jobs-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': 'Full-time',  # Startups typically hire full-time
                'salary': '',  # Startups typically don't list salary
                'posted_date': item.get('date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'startup-jobs-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Startup Jobs API error: {str(e)}")
        return []

def _search_job_search_api(config, criteria):
    """Search for jobs using Job Search API via RapidAPI (additional provider)
    
    API: https://rapidapi.com/job-search-api2.p.rapidapi.com
    """
    logger.info("Searching Job Search API for jobs")
    
    # Extract criteria
    keywords = ' '.join(criteria.get('keywords', []))
    location = criteria.get('location', '')
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'job-search-api2.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Prepare parameters
    querystring = {}
    
    if keywords:
        querystring['title_filter'] = keywords
        
    if location:
        querystring['location_filter'] = location
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://job-search-api2.p.rapidapi.com/active-ats-expired'),
            headers=headers,
            params=querystring
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        jobs = []
        
        for item in data.get('jobs', []):
            # Format job
            job = {
                'id': f"job-search-api-{item.get('id', '')}",
                'title': item.get('title', 'Unknown Position'),
                'company': item.get('company', 'Unknown Company'),
                'location': item.get('location', ''),
                'job_type': item.get('job_type', ''),
                'salary': item.get('salary', ''),
                'posted_date': item.get('date', 'Recently'),
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source': 'job-search-api'
            }
            
            jobs.append(job)
        
        return jobs
    
    except Exception as e:
        logger.error(f"Job Search API error: {str(e)}")
        return []

def _fetch_hiring_manager_info(config, job_id=None):
    """Fetch hiring manager information for a job
    
    API: https://hiring-manager-api.p.rapidapi.com/recruitment-manager-24h
    """
    logger.info("Fetching hiring manager information")
    
    # If we already have hiring manager data cached and no specific job_id provided, return the cache
    if not job_id and hiring_manager_cache:
        return hiring_manager_cache
    
    # Prepare headers
    headers = {
        'x-rapidapi-host': config.get('host', 'hiring-manager-api.p.rapidapi.com'),
        'x-rapidapi-key': config.get('api_key', '')
    }
    
    # Make the request
    try:
        response = requests.get(
            config.get('url', 'https://hiring-manager-api.p.rapidapi.com/recruitment-manager-24h'),
            headers=headers
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Store manager data by company name for easier lookup
        managers_by_company = {}
        
        for manager in data.get('managers', []):
            company = manager.get('company', '').lower()
            if company:
                if company not in managers_by_company:
                    managers_by_company[company] = []
                    
                managers_by_company[company].append({
                    'name': manager.get('name', ''),
                    'title': manager.get('title', ''),
                    'email': manager.get('email', ''),
                    'phone': manager.get('phone', ''),
                    'company': manager.get('company', '')
                })
        
        # Update our cache
        global hiring_manager_cache
        hiring_manager_cache = managers_by_company
        
        # If a specific job_id was requested, find that manager
        if job_id:
            # This would require additional logic to match a job_id to a company
            # For demo purposes, we'll just return None
            return None
            
        return managers_by_company
    
    except Exception as e:
        logger.error(f"Hiring Manager API error: {str(e)}")
        return {} if not job_id else None

# Helper functions

def _format_date(timestamp):
    """Format a timestamp to '3 days ago' format"""
    if not timestamp:
        return "Recently"
    
    try:
        # Parse the timestamp (format depends on the API)
        try:
            post_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            try:
                post_date = datetime.fromtimestamp(int(timestamp) / 1000)
            except:
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