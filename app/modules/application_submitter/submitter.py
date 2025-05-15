from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import random
import json
import logging
from app.config import Config
from app.modules.application_submitter.external_form_handler import ExternalFormHandler

# Setup logging
logger = logging.getLogger(__name__)

# Define common application form field mappings
COMMON_FIELD_MAPPINGS = {
    'first_name': ['first name', 'firstname', 'fname', 'given name'],
    'last_name': ['last name', 'lastname', 'lname', 'family name', 'surname'],
    'full_name': ['full name', 'name'],
    'email': ['email', 'e-mail', 'email address'],
    'phone': ['phone', 'telephone', 'phone number', 'mobile', 'cell'],
    'address': ['address', 'street address'],
    'city': ['city', 'town'],
    'state': ['state', 'province', 'region'],
    'zip': ['zip', 'zipcode', 'zip code', 'postal code', 'postcode'],
    'country': ['country', 'nation'],
    'resume': ['resume', 'cv', 'curriculum vitae', 'upload resume', 'upload cv'],
    'cover_letter': ['cover letter', 'cover', 'letter', 'upload cover letter'],
    'linkedin': ['linkedin', 'linkedin url', 'linkedin profile'],
    'website': ['website', 'website url', 'personal website', 'portfolio'],
    'years_of_experience': ['years of experience', 'experience years', 'total experience'],
    'education': ['education', 'degree', 'university', 'college'],
    'submit': ['submit', 'apply', 'send', 'submit application']
}

def submit_application(job_data, application_data, resume_data=None, resume_file_path=None, cover_letter_file_path=None):
    """Submit a job application to the specified job portal
    
    Args:
        job_data: Dict containing job details including URL and application method
        application_data: Dict containing customized application materials
        resume_data: Dict containing parsed resume information
        resume_file_path: Path to the resume file for upload
        cover_letter_file_path: Path to the cover letter file for upload
        
    Returns:
        dict: Result of the submission attempt
    """
    job_url = job_data.get('url')
    application_method = job_data.get('application_method', 'easy_apply')
    
    if not job_url:
        raise ValueError("Job URL is required for submission")
    
    # Log application attempt
    logger.info(f"Attempting to submit application for {job_data.get('title')} at {job_data.get('company')}")
    logger.info(f"Application method: {application_method}")
    
    # Handle based on application method
    if application_method == 'external_form':
        # For jobs with external forms, use the ExternalFormHandler
        return _handle_external_form_submission(
            job_data, 
            application_data, 
            resume_data, 
            resume_file_path, 
            cover_letter_file_path
        )
    else:
        # For "easy apply" jobs, use the _handle_easy_apply_submission function
        # This function will need to be implemented with real automation logic
        return _handle_easy_apply_submission(
            job_data,
            application_data,
            resume_data,
            resume_file_path,
            cover_letter_file_path
        )

def _handle_easy_apply_submission(job_data, application_data, resume_data=None, resume_file_path=None, cover_letter_file_path=None):
    """Handle submission for "Easy Apply" type applications
    
    This uses Selenium to automate the application process for job sites with one-click apply options.
    """
    try:
        # Setup WebDriver
        driver = _setup_webdriver()
        
        # Navigate to job URL
        job_url = job_data.get('url')
        driver.get(job_url)
        logger.info(f"Navigated to job URL: {job_url}")
        
        # Wait for page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Look for apply button (different sites have different selectors)
        apply_button = None
        apply_button_selectors = [
            "//button[contains(text(), 'Apply')]",
            "//button[contains(text(), 'Easy Apply')]",
            "//a[contains(text(), 'Apply')]",
            "//a[contains(@class, 'apply')]",
            "//button[contains(@class, 'apply')]"
        ]
        
        for selector in apply_button_selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                logger.info(f"Found apply button using selector: {selector}")
                break
            except:
                continue
        
        if not apply_button:
            logger.warning("Could not find apply button")
            driver.quit()
            return {
                'success': False,
                'job_id': job_data.get('id'),
                'company': job_data.get('company'),
                'error': "Could not locate apply button",
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'application_method': 'easy_apply'
            }
        
        # Click apply button
        apply_button.click()
        logger.info("Clicked apply button")
        
        # Wait for form to appear and fill it out
        # This part depends heavily on the site, but we can look for common fields
        try:
            # Wait for form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Fill out form fields if they exist
            fields_filled = 0
            
            # Resume upload
            if resume_file_path:
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                for file_input in file_inputs:
                    try:
                        file_input.send_keys(resume_file_path)
                        fields_filled += 1
                        logger.info("Uploaded resume file")
                        break
                    except:
                        continue
            
            # Cover letter upload
            if cover_letter_file_path:
                # Look for cover letter specific upload fields
                cover_letter_selectors = [
                    "//input[@type='file' and contains(@name, 'cover')]",
                    "//input[@type='file' and contains(@id, 'cover')]",
                    "//input[@type='file' and contains(@aria-label, 'cover')]"
                ]
                
                for selector in cover_letter_selectors:
                    try:
                        upload_field = driver.find_element(By.XPATH, selector)
                        upload_field.send_keys(cover_letter_file_path)
                        fields_filled += 1
                        logger.info("Uploaded cover letter file")
                        break
                    except:
                        continue
            
            # Submit form
            submit_button = None
            submit_selectors = [
                "//button[@type='submit']",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Apply')]",
                "//input[@type='submit']"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
                logger.info("Clicked submit button")
                
                # Wait for confirmation
                time.sleep(3)
                
                # Check for success messages or errors
                success_messages = [
                    "successfully submitted",
                    "application submitted",
                    "thank you for applying",
                    "application received",
                    "successfully applied"
                ]
                
                for message in success_messages:
                    if message in driver.page_source.lower():
                        driver.quit()
                        return {
                            'success': True,
                            'job_id': job_data.get('id'),
                            'company': job_data.get('company'),
                            'position': job_data.get('title'),
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                            'message': "Application submitted successfully",
                            'application_method': 'easy_apply',
                            'fields_filled': fields_filled
                        }
            
            # If we couldn't confirm success, assume it worked but log a warning
            logger.warning("Could not confirm application submission success")
            driver.quit()
            return {
                'success': True,
                'job_id': job_data.get('id'),
                'company': job_data.get('company'),
                'position': job_data.get('title'),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'message': "Application likely submitted, but confirmation not detected",
                'application_method': 'easy_apply',
                'fields_filled': fields_filled
            }
            
        except Exception as e:
            logger.error(f"Error filling out application form: {str(e)}")
            driver.quit()
            return {
                'success': False,
                'job_id': job_data.get('id'),
                'company': job_data.get('company'),
                'error': f"Error filling out application form: {str(e)}",
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'application_method': 'easy_apply'
            }
            
    except Exception as e:
        logger.error(f"Error in easy apply submission: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return {
            'success': False,
            'job_id': job_data.get('id'),
            'company': job_data.get('company'),
            'error': str(e),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'application_method': 'easy_apply'
        }

def _setup_webdriver():
    """Set up the Selenium WebDriver for browser automation"""
    # Set up Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create a new ChromeDriver instance
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver



def _handle_external_form_submission(job_data, application_data, resume_data, resume_file_path, cover_letter_file_path, auto_submit=True):
    """Handle external form submission using the ExternalFormHandler
    
    Args:
        job_data: Dict containing job details including URL
        application_data: Dict containing customized application materials
        resume_data: Dict containing parsed resume information
        resume_file_path: Path to the resume file
        cover_letter_file_path: Path to the cover letter file
        auto_submit: Whether to automatically click the submit button (default: True)
        
    Returns:
        dict: Result of the form filling process
    """
    if not resume_data:
        return {
            'success': False,
            'error': 'Resume data is required for external form submission',
            'job_id': job_data.get('id'),
            'company': job_data.get('company'),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    try:
        # Create an instance of the ExternalFormHandler
        form_handler = ExternalFormHandler(headless=Config.HEADLESS_BROWSER)
        
        # Fill the application form and optionally submit it
        result = form_handler.fill_and_submit_application_form(
            job_url=job_data.get('url'),
            resume_data=resume_data,
            application_data=application_data,
            resume_file_path=resume_file_path,
            cover_letter_file_path=cover_letter_file_path,
            auto_submit=auto_submit
        )
        
        # Enhance the result with job information
        result.update({
            'job_id': job_data.get('id'),
            'company': job_data.get('company'),
            'position': job_data.get('title'),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'application_method': 'external_form',
            'requires_manual_submission': not auto_submit
        })
        
        # Store the application record in the database/storage
        application_record = {
            'job_id': job_data.get('id'),
            'job_title': job_data.get('title'),
            'company': job_data.get('company'),
            'source': job_data.get('source', 'external'),
            'application_type': 'external_form',
            'status': 'submitted' if auto_submit and result.get('submission_successful') else 'filled',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'fields_filled': result.get('filled_fields', 0),
            'url': job_data.get('url'),
            'notes': result.get('submission_notes', '')
        }
        
        # Save application record
        _save_application_record(application_record)
        
        if result.get('success'):
            if auto_submit:
                if result.get('submission_successful'):
                    result['message'] = (
                        f"Successfully submitted application to {job_data.get('company')} for {job_data.get('title')} position. "
                        f"Filled {result.get('filled_fields')} fields."
                    )
                else:
                    result['message'] = (
                        f"Filled {result.get('filled_fields')} fields but couldn't submit automatically. "
                        f"Reason: {result.get('submission_error', 'Unknown error')}"
                    )
            else:
                button_msg = ""
                if result.get('submit_button_found'):
                    button_type = result.get('button_type', 'button')
                    button_text = result.get('button_text', 'button')
                    
                    if button_type == 'apply_button':
                        button_msg = f" Found an application button ('{button_text}') that will likely start the application process."
                    elif button_type == 'submit_button':
                        button_msg = f" Found a submission button ('{button_text}') that will likely submit the completed application."
                    else:
                        button_msg = f" Found a button ('{button_text}') that may submit the application."
                else:
                    button_msg = " No submit button was found. You may need to navigate through multiple pages."
                    
                result['message'] = (
                    f"Successfully filled {result.get('filled_fields')} fields on the application form.{button_msg} "
                    "Please review the application before manual submission."
                )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in external form submission: {str(e)}")
        return {
            'success': False,
            'error': f"Error in external form submission: {str(e)}",
            'job_id': job_data.get('id'),
            'company': job_data.get('company'),
            'position': job_data.get('title'),
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'application_method': 'external_form'
        }

def _save_application_record(application_record):
    """Save application record to storage for dashboard tracking
    
    Args:
        application_record: Dict containing application details
    """
    try:
        # Get existing records
        applications_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'applications.json')
        os.makedirs(os.path.dirname(applications_file), exist_ok=True)
        
        applications = []
        if os.path.exists(applications_file):
            try:
                with open(applications_file, 'r') as f:
                    applications = json.load(f)
            except json.JSONDecodeError:
                applications = []
        
        # Add new record
        applications.append(application_record)
        
        # Save updated records
        with open(applications_file, 'w') as f:
            json.dump(applications, f, indent=2)
            
        logger.info(f"Saved application record for {application_record.get('company')} - {application_record.get('job_title')}")
    except Exception as e:
        logger.error(f"Error saving application record: {str(e)}")
