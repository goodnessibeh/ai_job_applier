import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup logging
logger = logging.getLogger(__name__)

class JobScraper:
    """Base class for job scrapers"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Set up Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        
        # Add user agent to appear as a normal browser
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def search_jobs(self, keywords, location, job_type=None):
        """Search for jobs - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement search_jobs()")


class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn jobs"""
    
    def search_jobs(self, keywords, location, job_type=None):
        """Scrape LinkedIn jobs"""
        logger.info(f"Scraping LinkedIn for jobs with keywords: {keywords}, location: {location}")
        
        # Format keywords for URL
        keywords_str = '+'.join(keywords) if isinstance(keywords, list) else keywords.replace(' ', '+')
        location_str = location.replace(' ', '+') if location else 'remote'
        
        # Format job type for URL if provided
        job_type_param = ''
        if job_type:
            job_type_mapping = {
                'Full-time': 'F',
                'Part-time': 'P',
                'Contract': 'C',
                'Temporary': 'T',
                'Internship': 'I'
            }
            job_type_code = job_type_mapping.get(job_type, '')
            if job_type_code:
                job_type_param = f"&f_JT={job_type_code}"
        
        # Construct LinkedIn search URL
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords_str}&location={location_str}{job_type_param}"
        
        try:
            if not self.driver:
                self.setup_driver()
            
            self.driver.get(search_url)
            
            # Wait for job results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
            )
            
            # Scroll down to load more jobs
            self._scroll_to_load_jobs()
            
            # Parse job results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_listings = soup.find_all("div", class_="job-search-card")
            
            jobs = []
            for job_item in job_listings[:15]:  # Limit to 15 jobs for example
                try:
                    # Extract job details
                    job_title_elem = job_item.find("h3", class_="base-search-card__title")
                    job_title = job_title_elem.text.strip() if job_title_elem else "Unknown Position"
                    
                    company_elem = job_item.find("h4", class_="base-search-card__subtitle")
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    
                    location_elem = job_item.find("span", class_="job-search-card__location")
                    job_location = location_elem.text.strip() if location_elem else location
                    
                    posted_date_elem = job_item.find("time", class_="job-search-card__listdate")
                    posted_date = posted_date_elem.text.strip() if posted_date_elem else "Recently"
                    
                    job_link_elem = job_item.find("a", class_="base-card__full-link")
                    job_url = job_link_elem.get('href') if job_link_elem else None
                    
                    # Extract job ID from URL
                    job_id = "linkedin-unknown"
                    if job_url:
                        job_id_match = re.search(r'/view/(\d+)/', job_url)
                        if job_id_match:
                            job_id = f"linkedin-{job_id_match.group(1)}"
                    
                    # Check if job has "Easy Apply" button
                    easy_apply_elem = job_item.find("span", class_="job-search-card__easy-apply")
                    application_type = "easy_apply" if easy_apply_elem else "external"
                    
                    # Create job object
                    job = {
                        'id': job_id,
                        'title': job_title,
                        'company': company,
                        'location': job_location,
                        'job_type': job_type or "Not specified",
                        'posted_date': posted_date,
                        'description': self._get_job_description(job_url) if job_url else "No description available",
                        'url': job_url,
                        'source': 'linkedin',
                        'is_demo': False,  # Mark as real job (scraped)
                        'application_type': application_type,
                        'salary': "Not specified"  # LinkedIn often doesn't show salary
                    }
                    
                    jobs.append(job)
                    
                    # Small delay to avoid overloading
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {str(e)}")
            return []
        finally:
            self.close_driver()
    
    def _scroll_to_load_jobs(self):
        """Scroll down to load more job listings"""
        try:
            # Initial pause to let page load
            time.sleep(2)
            
            # Scroll down 3 times
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                
        except Exception as e:
            logger.error(f"Error scrolling LinkedIn page: {str(e)}")
    
    def _get_job_description(self, job_url):
        """Get job description from job details page"""
        try:
            # Open job details page
            self.driver.get(job_url)
            
            # Wait for job description to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "show-more-less-html__markup"))
            )
            
            # Get description text
            desc_elem = self.driver.find_element(By.CLASS_NAME, "show-more-less-html__markup")
            description = desc_elem.text
            
            return description
            
        except Exception as e:
            logger.error(f"Error extracting job description: {str(e)}")
            return "Description not available"


class GlassdoorScraper(JobScraper):
    """Scraper for Glassdoor jobs"""
    
    def search_jobs(self, keywords, location, job_type=None):
        """Scrape Glassdoor jobs"""
        logger.info(f"Scraping Glassdoor for jobs with keywords: {keywords}, location: {location}")
        
        # Format keywords for URL
        keywords_str = '-'.join(keywords) if isinstance(keywords, list) else keywords.replace(' ', '-')
        location_str = location.replace(' ', '-') if location else 'remote'
        
        # Construct Glassdoor search URL
        search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords_str}&locT=C&locId=1147401&locKeyword={location_str}"
        
        try:
            if not self.driver:
                self.setup_driver()
            
            self.driver.get(search_url)
            
            # Handle potential login popup
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "modal_closeIcon"))
                )
                close_button = self.driver.find_element(By.CLASS_NAME, "modal_closeIcon")
                close_button.click()
            except:
                pass  # No popup or unable to close
            
            # Wait for job results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobCard"))
            )
            
            # Parse job results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_listings = soup.find_all("li", class_="react-job-listing")
            
            jobs = []
            for job_item in job_listings[:15]:  # Limit to 15 jobs for example
                try:
                    # Extract job details
                    job_title_elem = job_item.find("a", class_="jobLink")
                    job_title = job_title_elem.text.strip() if job_title_elem else "Unknown Position"
                    
                    company_elem = job_item.find("div", class_="jobCardCompanyInfo")
                    company = company_elem.text.strip().split('\n')[0] if company_elem else "Unknown Company"
                    
                    location_elem = job_item.find("span", class_="loc")
                    job_location = location_elem.text.strip() if location_elem else location
                    
                    posted_date_elem = job_item.find("div", class_="jobDetailLine--age")
                    posted_date = posted_date_elem.text.strip() if posted_date_elem else "Recently"
                    
                    # Get relative link
                    job_link_elem = job_item.find("a", class_="jobLink")
                    relative_url = job_link_elem.get('href') if job_link_elem else None
                    job_url = f"https://www.glassdoor.com{relative_url}" if relative_url else None
                    
                    # Extract job ID from the job listing
                    job_id = "glassdoor-unknown"
                    if job_item.get('data-id'):
                        job_id = f"glassdoor-{job_item.get('data-id')}"
                    
                    # Get salary if available
                    salary_elem = job_item.find("span", class_="salary-estimate")
                    salary = salary_elem.text.strip() if salary_elem else "Not specified"
                    
                    # Determine application type - Glassdoor doesn't have an obvious "Easy Apply" indicator in the listing
                    # We'll just assume all are external for now
                    application_type = "external"
                    
                    # Create job object
                    job = {
                        'id': job_id,
                        'title': job_title,
                        'company': company,
                        'location': job_location,
                        'job_type': job_type or "Not specified",
                        'posted_date': posted_date,
                        'description': self._get_job_description(job_url) if job_url else "No description available",
                        'url': job_url,
                        'source': 'glassdoor',
                        'is_demo': False,  # Mark as real job (scraped)
                        'application_type': application_type,
                        'salary': salary
                    }
                    
                    jobs.append(job)
                    
                    # Small delay to avoid overloading
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    logger.error(f"Error parsing Glassdoor job: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {str(e)}")
            return []
        finally:
            self.close_driver()
    
    def _get_job_description(self, job_url):
        """Get job description from job details page"""
        try:
            # Open job details page
            self.driver.get(job_url)
            
            # Wait for job description to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobDescriptionContent"))
            )
            
            # Get description text
            desc_elem = self.driver.find_element(By.CLASS_NAME, "jobDescriptionContent")
            description = desc_elem.text
            
            return description
            
        except Exception as e:
            logger.error(f"Error extracting Glassdoor job description: {str(e)}")
            return "Description not available"


class GoogleJobsScraper(JobScraper):
    """Scraper for Google Jobs"""
    
    def search_jobs(self, keywords, location, job_type=None):
        """Scrape Google Jobs"""
        logger.info(f"Scraping Google Jobs for jobs with keywords: {keywords}, location: {location}")
        
        # Format keywords for URL
        keywords_str = '+'.join(keywords) if isinstance(keywords, list) else keywords.replace(' ', '+')
        location_str = location.replace(' ', '+') if location else 'remote'
        
        # Add job type to the query if provided
        if job_type and job_type != "All":
            keywords_str += f"+{job_type.replace('-', '+')}"
        
        # Construct Google Jobs search URL (via Google search)
        search_url = f"https://www.google.com/search?q={keywords_str}+jobs+{location_str}&ibp=htl;jobs"
        
        try:
            if not self.driver:
                self.setup_driver()
            
            self.driver.get(search_url)
            
            # Wait for job results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.gws-plugins-horizon-jobs__tl-lif"))
            )
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs()
            
            # Parse job results
            job_listings = self.driver.find_elements(By.CSS_SELECTOR, "div.gws-plugins-horizon-jobs__tl-lif")
            
            jobs = []
            for i, job_item in enumerate(job_listings[:15]):  # Limit to 15 jobs
                try:
                    # Click on the job to load details
                    job_item.click()
                    time.sleep(1)  # Wait for details to load
                    
                    # Extract job details from the right panel
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, "h2.gws-plugins-horizon-jobs__li-title")
                    job_title = title_elem.text if title_elem else "Unknown Position"
                    
                    company_elem = self.driver.find_element(By.CSS_SELECTOR, "div.gws-plugins-horizon-jobs__li-subtitle")
                    company = company_elem.text if company_elem else "Unknown Company"
                    
                    location_elem = self.driver.find_element(By.CSS_SELECTOR, "div.gws-plugins-horizon-jobs__li-loc")
                    job_location = location_elem.text if location_elem else location
                    
                    # Get posting date if available
                    try:
                        posted_elem = self.driver.find_element(By.CSS_SELECTOR, "span.gws-plugins-horizon-jobs__li-age")
                        posted_date = posted_elem.text
                    except:
                        posted_date = "Recently"
                    
                    # Get job description
                    try:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, "div.gws-plugins-horizon-jobs__description-text")
                        description = desc_elem.text
                    except:
                        description = "No description available"
                    
                    # Get apply link
                    try:
                        apply_btn = self.driver.find_element(By.CSS_SELECTOR, "a.gws-plugins-horizon-jobs__apply-button")
                        job_url = apply_btn.get_attribute('href')
                    except:
                        job_url = f"https://www.google.com/search?q={keywords_str}+jobs+{location_str}"
                    
                    # Create a unique ID
                    job_id = f"google-{int(time.time())}-{i}"
                    
                    # Create job object
                    job = {
                        'id': job_id,
                        'title': job_title,
                        'company': company,
                        'location': job_location,
                        'job_type': job_type or "Not specified",
                        'posted_date': posted_date,
                        'description': description,
                        'url': job_url,
                        'source': 'google',
                        'is_demo': False,  # Mark as real job (scraped)
                        'application_type': "external",  # Google Jobs links to external sites
                        'salary': self._extract_salary()
                    }
                    
                    jobs.append(job)
                    
                    # Small delay
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error parsing Google job: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Google Jobs: {str(e)}")
            return []
        finally:
            self.close_driver()
    
    def _scroll_to_load_jobs(self):
        """Scroll to load more job listings"""
        try:
            # Initial pause
            time.sleep(1)
            
            # Scroll down a few times
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(0.7)
                
        except Exception as e:
            logger.error(f"Error scrolling Google Jobs page: {str(e)}")
    
    def _extract_salary(self):
        """Try to extract salary information if available"""
        try:
            salary_elem = self.driver.find_element(By.CSS_SELECTOR, "span.gws-plugins-horizon-jobs__li-salary")
            return salary_elem.text
        except:
            return "Not specified"


class IndeedScraper(JobScraper):
    """Scraper for Indeed jobs"""
    
    def search_jobs(self, keywords, location, job_type=None):
        """Scrape Indeed jobs"""
        logger.info(f"Scraping Indeed for jobs with keywords: {keywords}, location: {location}")
        
        # Format keywords for URL
        keywords_str = '+'.join(keywords) if isinstance(keywords, list) else keywords.replace(' ', '+')
        location_str = location.replace(' ', '+') if location else 'remote'
        
        # Handle job type
        job_type_param = ''
        if job_type:
            if job_type == "Full-time":
                job_type_param = "&jt=fulltime"
            elif job_type == "Part-time":
                job_type_param = "&jt=parttime"
            elif job_type == "Contract":
                job_type_param = "&jt=contract"
            elif job_type == "Temporary":
                job_type_param = "&jt=temporary"
            elif job_type == "Internship":
                job_type_param = "&jt=internship"
        
        # Construct Indeed search URL
        search_url = f"https://www.indeed.com/jobs?q={keywords_str}&l={location_str}{job_type_param}"
        
        try:
            if not self.driver:
                self.setup_driver()
            
            self.driver.get(search_url)
            
            # Wait for job results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
            )
            
            # Parse job results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_listings = soup.find_all("div", class_="job_seen_beacon")
            
            jobs = []
            for i, job_item in enumerate(job_listings[:15]):  # Limit to 15 jobs
                try:
                    # Extract job details
                    job_title_elem = job_item.find("h2", class_="jobTitle")
                    job_title = job_title_elem.text.strip() if job_title_elem else "Unknown Position"
                    
                    company_elem = job_item.find("span", class_="companyName")
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    
                    location_elem = job_item.find("div", class_="companyLocation")
                    job_location = location_elem.text.strip() if location_elem else location
                    
                    # Get job URL
                    job_link = None
                    title_link = job_item.find("h2", class_="jobTitle").find("a") if job_item.find("h2", class_="jobTitle") else None
                    if title_link and 'href' in title_link.attrs:
                        relative_link = title_link['href']
                        job_link = f"https://www.indeed.com{relative_link}" if relative_link.startswith('/') else relative_link
                    
                    # Extract job description (summary from the card)
                    description_elem = job_item.find("div", class_="job-snippet")
                    brief_description = description_elem.text.strip() if description_elem else "No preview available"
                    
                    # Get full description if possible
                    full_description = self._get_job_description(job_link) if job_link else brief_description
                    
                    # Check for "Apply on company site" vs "Apply on Indeed"
                    application_type = "external"
                    apply_button = job_item.find("span", string=re.compile("Apply now"))
                    if apply_button and "Apply on Indeed" in apply_button.text:
                        application_type = "easy_apply"
                    
                    # Create unique job ID
                    job_id = f"indeed-{int(time.time())}-{i}"
                    
                    # Get salary if available
                    salary_elem = job_item.find("div", class_="salary-snippet-container")
                    salary = salary_elem.text.strip() if salary_elem else "Not specified"
                    
                    # Get posted date
                    date_elem = job_item.find("span", class_="date")
                    posted_date = date_elem.text.strip() if date_elem else "Recently"
                    
                    # Create job object
                    job = {
                        'id': job_id,
                        'title': job_title,
                        'company': company,
                        'location': job_location,
                        'job_type': job_type or "Not specified",
                        'posted_date': posted_date,
                        'description': full_description,
                        'url': job_link,
                        'source': 'indeed',
                        'is_demo': False,  # Mark as real job (scraped)
                        'application_type': application_type,
                        'salary': salary
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Error parsing Indeed job: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {str(e)}")
            return []
        finally:
            self.close_driver()
    
    def _get_job_description(self, job_url):
        """Get full job description from job details page"""
        if not job_url:
            return "No description available"
            
        try:
            # Navigate to job details page
            self.driver.get(job_url)
            
            # Wait for description to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "jobDescriptionText"))
            )
            
            # Extract full description
            desc_elem = self.driver.find_element(By.ID, "jobDescriptionText")
            return desc_elem.text
            
        except Exception as e:
            logger.error(f"Error getting Indeed job description: {str(e)}")
            return "Description not available"


# Function to get the appropriate scraper
def get_scraper(site):
    """Factory function to get appropriate scraper based on the site"""
    if site == 'linkedin':
        return LinkedInScraper()
    elif site == 'glassdoor':
        return GlassdoorScraper()
    elif site == 'google':
        return GoogleJobsScraper()
    elif site == 'indeed':
        return IndeedScraper()
    else:
        return None