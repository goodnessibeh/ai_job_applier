import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import logging
from app.config import Config
from app.modules.job_search.api_implementations import (
    _search_linkedin, _search_indeed, _search_glassdoor,
    _search_monster, _search_ziprecruiter
)
from app.modules.job_search.web_scraper import get_scraper

# Setup logging
logger = logging.getLogger(__name__)

# API endpoints for job portals
JOB_PORTAL_ENDPOINTS = {
    'linkedin': 'https://api.linkedin.com/v2/jobSearch',
    'indeed': 'https://api.indeed.com/ads/apisearch',
    'glassdoor': 'https://api.glassdoor.com/api/api.htm',
    'monster': 'https://apis.monster.com/jobs/search',
    'ziprecruiter': 'https://api.ziprecruiter.com/jobs/v1',
    'google': 'https://jobs.googleapis.com/v4/jobs:search',
}

# Supported job sites
JOB_SITES = {
    'linkedin': 'LinkedIn',
    'indeed': 'Indeed',
    'glassdoor': 'Glassdoor',
    'monster': 'Monster',
    'ziprecruiter': 'ZipRecruiter',
    'google': 'Google Jobs',
}

def search_jobs(criteria):
    """Search for jobs matching the given criteria
    
    Args:
        criteria: dict containing search parameters like:
            - keywords: list of keywords to search for
            - location: location to search in
            - job_type: full-time, part-time, etc.
            - sites: list of job sites to search
            
    Returns:
        list: Job listings matching the criteria
    """
    # Validate input
    if 'keywords' not in criteria:
        raise ValueError("Keywords are required for job search")
    
    # Default to all available sites if none specified
    sites = criteria.get('sites', list(JOB_SITES.keys()))
    
    # Collect jobs from all specified sites
    all_jobs = []
    for site in sites:
        if site.lower() in JOB_SITES:
            site_jobs = _search_site(site.lower(), criteria)
            all_jobs.extend(site_jobs)
    
    # If no jobs found through regular search, use fallback demo data
    if not all_jobs:
        logger.info("No jobs found through regular search, using fallback demo data")
        all_jobs = _generate_demo_results(criteria)
    
    # Remove duplicates (based on job title and company)
    unique_jobs = _remove_duplicate_jobs(all_jobs)
    
    # Sort jobs by relevance (simplified scoring for now)
    sorted_jobs = _sort_jobs_by_relevance(unique_jobs, criteria['keywords'])
    
    return sorted_jobs

def _search_site(site, criteria):
    """Search a specific job site
    
    Priority:
    1. Use web scraping for LinkedIn and Glassdoor
    2. Use API if available
    """
    # Get portal configurations
    portal_configs = Config.get_job_portal_configs()
    
    # Check for web scraping support first (for LinkedIn, Glassdoor, Google, Indeed)
    if site in ['linkedin', 'glassdoor', 'google', 'indeed']:
        try:
            # First try with web scraping
            use_web_scraping = Config.WEB_SCRAPING_ENABLED if hasattr(Config, 'WEB_SCRAPING_ENABLED') else True
            
            if use_web_scraping:
                logger.info(f"Attempting to scrape {site} for jobs")
                scraper = get_scraper(site)
                if scraper:
                    # Extract criteria
                    keywords = criteria.get('keywords', [])
                    location = criteria.get('location', '')
                    job_type = criteria.get('job_type', '')
                    
                    # Scrape jobs
                    scraped_jobs = scraper.search_jobs(keywords, location, job_type)
                    
                    if scraped_jobs:
                        logger.info(f"Successfully scraped {len(scraped_jobs)} jobs from {site}")
                        return scraped_jobs
                    else:
                        logger.warning(f"No jobs found via web scraping on {site}, trying API")
        except Exception as e:
            logger.error(f"Error during web scraping for {site}: {str(e)}")
            # Continue to API
    
    # Try API if available and enabled
    if site in portal_configs and portal_configs[site]['enabled']:
        try:
            # Use the appropriate API method based on the site
            if site == 'linkedin':
                return _search_linkedin(portal_configs[site], criteria)
            elif site == 'indeed':
                return _search_indeed(portal_configs[site], criteria)
            elif site == 'glassdoor':
                return _search_glassdoor(portal_configs[site], criteria)
            elif site == 'monster':
                return _search_monster(portal_configs[site], criteria)
            elif site == 'ziprecruiter':
                return _search_ziprecruiter(portal_configs[site], criteria)
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

def _sort_jobs_by_relevance(jobs, keywords):
    """Sort jobs by relevance to the given keywords"""
    # Simple relevance scoring
    def calculate_relevance(job):
        score = 0
        # Check for keywords in title (higher weight)
        for keyword in keywords:
            if keyword.lower() in job['title'].lower():
                score += 10
        
        # Check for keywords in description
        for keyword in keywords:
            if keyword.lower() in job['description'].lower():
                score += 5
        
        # Recency bonus
        try:
            days_ago = int(job['posted_date'].split()[0])
            score += max(0, 30 - days_ago)  # Newer posts get higher scores
        except (ValueError, IndexError, AttributeError):
            # If posted_date is not in expected format, assume recent
            score += 15
        
        return score
    
    # Sort jobs by score in descending order
    return sorted(jobs, key=calculate_relevance, reverse=True)


def _generate_demo_results(criteria):
    """Generate demo job results based on search criteria"""
    keywords = criteria.get('keywords', [])
    location = criteria.get('location', 'Remote')
    job_type = criteria.get('job_type', 'Full-time')
    
    # Format keywords for use in job titles/descriptions
    keyword_string = ', '.join(keywords)
    primary_keyword = keywords[0] if keywords else "Software"
    
    # Generate a list of demo jobs
    demo_jobs = []
    
    # Common tech companies
    companies = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Twitter",
        "Airbnb", "Dropbox", "Shopify", "Slack", "Zoom", "Square", "Stripe",
        "LinkedIn", "GitHub", "GitLab", "Atlassian", "Salesforce", "Adobe"
    ]
    
    # Job title templates
    job_titles = [
        f"Senior {primary_keyword} Engineer",
        f"{primary_keyword} Developer",
        f"{primary_keyword} Specialist",
        f"Lead {primary_keyword} Architect",
        f"{primary_keyword} Manager",
        f"{primary_keyword} Consultant",
        f"Principal {primary_keyword} Engineer",
        f"{primary_keyword} Analyst",
        f"Director of {primary_keyword}",
        f"{primary_keyword} Team Lead"
    ]
    
    # Description template
    description_template = """
    We are looking for a talented {title} to join our team. The ideal candidate has experience with {keywords}.
    
    Responsibilities:
    - Design and develop {keyword_focus} solutions
    - Collaborate with cross-functional teams
    - Maintain and improve existing {keyword_focus} systems
    - Stay up-to-date with latest {keyword_focus} technologies
    
    Requirements:
    - {experience} years of experience in {keyword_focus}
    - Strong understanding of {related_skills}
    - Excellent problem-solving and communication skills
    - BS/MS in Computer Science or related field
    
    We offer competitive salary and benefits, flexible work arrangements, and opportunities for growth.
    """
    
    # Generate 15 demo jobs
    for i in range(15):
        # Mix and match companies, titles
        company = companies[i % len(companies)]
        title = job_titles[i % len(job_titles)]
        
        # Randomize days ago (1-10)
        days_ago = (i % 10) + 1
        
        # Create demo job
        job = {
            'id': f"demo-{i+1}",
            'title': title,
            'company': company,
            'location': location,
            'job_type': job_type,
            'posted_date': f"{days_ago} days ago",
            'description': description_template.format(
                title=title,
                keywords=keyword_string,
                keyword_focus=primary_keyword,
                experience=str(3 + (i % 5)),
                related_skills=", ".join(keywords) if len(keywords) > 1 else primary_keyword
            ),
            'url': f"https://example.com/jobs/{i+1}",
            'source': 'demo',
            'is_demo': True,
            'application_type': "external",
            'salary': f"${80 + (i*10)}k - ${120 + (i*10)}k"
        }
        
        demo_jobs.append(job)
    
    return demo_jobs