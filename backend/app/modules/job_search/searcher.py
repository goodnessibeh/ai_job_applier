import time
import logging
from flask_login import current_user
from app.config import Config
from app.modules.job_search.api_implementations import (
    _search_indeed, _search_upwork, _search_google_jobs, _search_workday,
    _search_glassdoor, _search_startup_jobs, _search_job_search,
    _search_internships, _search_active_jobs,
    _search_indeed_api, _search_jobs_api, _search_linkedin_api, 
    _search_linkedin_job_api, _search_google_jobs_api, _search_workday_jobs_api,
    _search_glassdoor_jobs_api, _search_startup_jobs_api, _search_job_search_api,
    _fetch_hiring_manager_info
)

# Setup logging
logger = logging.getLogger(__name__)

# Supported job sites
JOB_SITES = {
    'indeed': 'Indeed',
    'upwork': 'Upwork',
    'google': 'Google Jobs',
    'workday': 'Workday',
    'glassdoor': 'Glassdoor',
    'startup': 'Startup Jobs',
    'job_search': 'Job Search',
    'internships': 'Internships',
    'active_jobs': 'Active Jobs',
    'indeed_api': 'Indeed API',
    'jobs_api': 'Jobs API',
    'linkedin_search': 'LinkedIn Search API',
    'linkedin_job': 'LinkedIn Job API',
    'google_jobs': 'Google Jobs API',
    'workday_jobs': 'Workday Jobs API',
    'glassdoor_jobs': 'Glassdoor Jobs API',
    'startup_jobs': 'Startup Jobs API',
    'job_search_api': 'Job Search API',
    'hiring_manager': 'Hiring Manager API'
}

def search_jobs(criteria):
    """Search for jobs matching the given criteria
    
    Args:
        criteria: dict containing search parameters like:
            - keywords: list of keywords to search for
            - location: location to search in
            - job_type: full-time, part-time, etc.
            - sites: list of job sites to search
            - user_id: user ID for personalized search
            
    Returns:
        list: Job listings matching the criteria with match scores
    """
    # Validate input
    if 'keywords' not in criteria:
        # If keywords not provided directly, check if there's a user_id and get their job titles
        if current_user and current_user.is_authenticated and current_user.job_titles:
            criteria['keywords'] = current_user.get_job_titles_list()
        else:
            raise ValueError("Keywords are required for job search")
    
    # Default to all available sites if none specified
    sites = criteria.get('sites', list(JOB_SITES.keys()))
    
    # Collect jobs from all specified sites
    all_jobs = []
    for site in sites:
        if site.lower() in JOB_SITES:
            site_jobs = _search_site(site.lower(), criteria)
            all_jobs.extend(site_jobs)
    
    # If no jobs found, return empty list
    if not all_jobs:
        logger.info("No jobs found through API search")
        return []
    
    # Remove duplicates (based on job title and company)
    unique_jobs = _remove_duplicate_jobs(all_jobs)
    
    # Add match scores to jobs
    jobs_with_scores = _add_match_scores(unique_jobs, criteria)
    
    # Enhance job listings with hiring manager info if available
    enhanced_jobs = _enhance_with_hiring_manager_info(jobs_with_scores)
    
    # Sort jobs by match score
    sorted_jobs = sorted(enhanced_jobs, key=lambda x: x['match_score'], reverse=True)
    
    return sorted_jobs
    
def _enhance_with_hiring_manager_info(jobs):
    """Enhance job listings with hiring manager information if available"""
    # Fetch hiring manager information from API
    try:
        # Get portal configurations
        portal_configs = Config.get_job_portal_configs()
        
        # Check if hiring manager API is configured
        if 'hiring_manager' in portal_configs and portal_configs['hiring_manager']['enabled']:
            logger.info("Fetching hiring manager information to enhance job listings")
            
            # Get hiring manager data
            hiring_manager_data = _fetch_hiring_manager_info(portal_configs['hiring_manager'])
            
            if hiring_manager_data:
                # For each job, try to find matching hiring manager data
                for job in jobs:
                    company_name = job.get('company', '').lower()
                    if company_name in hiring_manager_data:
                        # Pick the first hiring manager for the company
                        manager = hiring_manager_data[company_name][0]
                        
                        # Add hiring manager info to job
                        job['hiring_manager'] = {
                            'name': manager.get('name', ''),
                            'title': manager.get('title', ''),
                            'email': manager.get('email', ''),
                            'phone': manager.get('phone', '')
                        }
                        
                        logger.info(f"Added hiring manager info for job at {company_name}")
                    else:
                        # No hiring manager info for this company
                        job['hiring_manager'] = None
            else:
                logger.warning("No hiring manager data available to enhance job listings")
                
    except Exception as e:
        logger.error(f"Error enhancing jobs with hiring manager info: {str(e)}")
    
    return jobs

def _search_site(site, criteria):
    """Search a specific job site"""
    # Get portal configurations
    portal_configs = Config.get_job_portal_configs()
    
    # Skip web scraping, only use API
    
    # Try API if available and enabled
    if site in portal_configs and portal_configs[site]['enabled']:
        try:
            # Use the appropriate API method based on the site
            if site == 'indeed':
                return _search_indeed(portal_configs[site], criteria)
            elif site == 'upwork':
                return _search_upwork(portal_configs[site], criteria)
            elif site == 'google':
                return _search_google_jobs(portal_configs[site], criteria)
            elif site == 'workday':
                return _search_workday(portal_configs[site], criteria)
            elif site == 'glassdoor':
                return _search_glassdoor(portal_configs[site], criteria)
            elif site == 'startup':
                return _search_startup_jobs(portal_configs[site], criteria)
            elif site == 'job_search':
                return _search_job_search(portal_configs[site], criteria)
            elif site == 'internships':
                return _search_internships(portal_configs[site], criteria)
            elif site == 'active_jobs':
                return _search_active_jobs(portal_configs[site], criteria)
            # New APIs
            elif site == 'indeed_api':
                return _search_indeed_api(portal_configs[site], criteria)
            elif site == 'jobs_api':
                return _search_jobs_api(portal_configs[site], criteria)
            elif site == 'linkedin_search':
                return _search_linkedin_api(portal_configs[site], criteria)
            elif site == 'linkedin_job':
                return _search_linkedin_job_api(portal_configs[site], criteria)
            elif site == 'google_jobs':
                return _search_google_jobs_api(portal_configs[site], criteria)
            elif site == 'workday_jobs':
                return _search_workday_jobs_api(portal_configs[site], criteria)
            elif site == 'glassdoor_jobs':
                return _search_glassdoor_jobs_api(portal_configs[site], criteria)
            elif site == 'startup_jobs':
                return _search_startup_jobs_api(portal_configs[site], criteria)
            elif site == 'job_search_api':
                return _search_job_search_api(portal_configs[site], criteria)
            elif site == 'hiring_manager':
                # Special case - hiring manager API doesn't directly search for jobs
                # It's used to supplement job data with hiring manager information
                logger.info("Hiring Manager API is used to supplement job information, not for direct job search")
                hiring_manager_data = _fetch_hiring_manager_info(portal_configs[site])
                return []
            else:
                logger.warning(f"No implementation for {site} API")
                return []
        except Exception as e:
            logger.error(f"Error searching {site} API: {str(e)}")
            return []
    else:
        logger.info(f"API not configured for {site}")
        return []


def _remove_duplicate_jobs(jobs):
    """Remove duplicate job listings based on title and company"""
    unique_jobs = []
    seen_jobs = set()
    
    for job in jobs:
        # Create a unique identifier for each job
        job_key = f"{job['title']}:{job['company']}"
        
        if job_key not in seen_jobs:
            seen_jobs.add(job_key)
            unique_jobs.append(job)
    
    return unique_jobs

def _add_match_scores(jobs, criteria):
    """Add match scores to jobs based on user preferences"""
    keywords = criteria.get('keywords', [])
    
    # Get user preferences if available
    user_preferences = _get_user_preferences()
    
    for job in jobs:
        score, reasons = _calculate_match_score(job, keywords, user_preferences)
        job['match_score'] = score
        job['match_reasons'] = reasons
    
    return jobs

def _get_user_preferences():
    """Get the current user's job preferences"""
    if current_user and current_user.is_authenticated:
        return {
            'job_titles': current_user.get_job_titles_list(),
            'min_salary': current_user.min_salary,
            'max_commute_distance': current_user.max_commute_distance,
            'preferred_locations': current_user.get_preferred_locations_list(),
            'remote_only': current_user.remote_only
        }
    return None

def _calculate_match_score(job, keywords, user_preferences=None):
    """Calculate a match score (0-100) for a job based on keywords and user preferences"""
    score = 0
    reasons = []
    
    # Basic keyword matching
    keyword_title_matches = 0
    for keyword in keywords:
        if keyword.lower() in job['title'].lower():
            keyword_title_matches += 1
            
    if keyword_title_matches > 0:
        title_score = min(40, 20 + (keyword_title_matches * 5))
        score += title_score
        reasons.append(f"Title matches {keyword_title_matches} keyword(s): +{title_score} points")
    
    # Description keyword matching
    keyword_desc_matches = 0
    for keyword in keywords:
        if keyword.lower() in job['description'].lower():
            keyword_desc_matches += 1
            
    if keyword_desc_matches > 0:
        desc_score = min(20, keyword_desc_matches * 3)
        score += desc_score
        reasons.append(f"Description matches {keyword_desc_matches} keyword(s): +{desc_score} points")
    
    # Recency bonus
    recency_score = 0
    try:
        if 'Today' in job['posted_date'] or 'today' in job['posted_date'].lower():
            recency_score = 15
            reasons.append("Job posted today: +15 points")
        elif 'Yesterday' in job['posted_date'] or 'yesterday' in job['posted_date'].lower():
            recency_score = 10
            reasons.append("Job posted yesterday: +10 points")
        else:
            days_text = job['posted_date'].split()[0]
            if days_text.isdigit():
                days_ago = int(days_text)
                if days_ago <= 7:
                    recency_score = max(0, 10 - days_ago)
                    reasons.append(f"Job posted {days_ago} days ago: +{recency_score} points")
    except (ValueError, IndexError, AttributeError):
        pass
        
    score += recency_score
    
    # If user preferences are available, incorporate them
    if user_preferences:
        # Location matching
        location_score = 0
        is_remote = 'remote' in job['location'].lower()
        
        if user_preferences['remote_only'] and is_remote:
            location_score = 15
            reasons.append("Remote job matches preference: +15 points")
        elif not user_preferences['remote_only']:
            # Check preferred locations
            if user_preferences['preferred_locations']:
                for location in user_preferences['preferred_locations']:
                    if location.lower() in job['location'].lower():
                        location_score = 15
                        reasons.append(f"Location {location} matches preference: +15 points")
                        break
        
        score += location_score
        
        # Salary matching
        if user_preferences['min_salary'] and 'salary' in job and job['salary']:
            # Extract salary from text with simple heuristics
            try:
                salary_text = job['salary'].lower()
                # Try to find numbers in the text
                numbers = []
                for word in salary_text.replace('$', ' ').replace(',', '').replace('k', '000 ').split():
                    if word.isdigit():
                        numbers.append(int(word))
                    elif word.replace('.', '').isdigit():
                        numbers.append(float(word))
                
                if numbers:
                    # Use the largest number as an approximation
                    if max(numbers) >= user_preferences['min_salary']:
                        salary_score = 10
                        reasons.append(f"Salary meets minimum requirement: +10 points")
                        score += salary_score
            except Exception as e:
                logger.error(f"Error parsing salary: {str(e)}")
    
    # Ensure score is within 0-100
    score = max(0, min(100, score))
    
    return score, reasons

