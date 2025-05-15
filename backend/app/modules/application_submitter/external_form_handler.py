import re
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Setup logging
logger = logging.getLogger(__name__)

class ExternalFormHandler:
    """Class to handle external job application forms"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.field_mapping = {
            # Basic info fields
            'first_name': ['first name', 'firstname', 'fname', 'given name'],
            'last_name': ['last name', 'lastname', 'lname', 'family name', 'surname'],
            'full_name': ['full name', 'name'],
            'email': ['email', 'e-mail', 'email address'],
            'phone': ['phone', 'telephone', 'phone number', 'mobile', 'cell'],
            
            # Address fields
            'address': ['address', 'street address', 'address line 1'],
            'city': ['city', 'town'],
            'state': ['state', 'province', 'region'],
            'zip': ['zip', 'zipcode', 'zip code', 'postal code', 'postcode'],
            'country': ['country', 'nation'],
            
            # Resume and cover letter fields
            'resume': ['resume', 'cv', 'curriculum vitae', 'upload resume', 'upload cv', 'resume upload'],
            'cover_letter': ['cover letter', 'cover', 'letter', 'upload cover letter'],
            
            # Professional fields
            'linkedin': ['linkedin', 'linkedin url', 'linkedin profile'],
            'website': ['website', 'website url', 'personal website', 'portfolio'],
            'years_of_experience': ['years of experience', 'experience years', 'total experience'],
            
            # Work authorization fields
            'work_authorization': ['legally authorized', 'legally authorised', 'authorized to work', 'work authorization', 'require visa'],
            
            # Education fields
            'education_level': ['education level', 'highest degree', 'degree level'],
            'university': ['university', 'college', 'school', 'institution'],
            'major': ['major', 'field of study', 'degree field'],
            'graduation_year': ['graduation year', 'graduation date', 'year of graduation'],
            
            # Experience fields
            'current_job_title': ['current title', 'job title', 'position', 'current position', 'current role'],
            'current_company': ['current company', 'company', 'employer', 'current employer'],
            
            # Submit button - Initial application buttons and final submit buttons
            'apply_button': ['apply now', 'apply for this job', 'apply', 'continue application', 'start application'],
            'submit_button': ['submit', 'submit application', 'finish application', 'complete application', 'send application', 'send']
        }
    
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
    
    def fill_application_form(self, job_url, resume_data, application_data, resume_file_path=None, cover_letter_file_path=None):
        """Fill out an external application form without submitting
        
        Args:
            job_url: URL of the job application
            resume_data: Dict containing parsed resume information
            application_data: Dict containing customized application materials
            resume_file_path: Path to the resume file
            cover_letter_file_path: Path to the cover letter file
            
        Returns:
            dict: Result of the form filling
        """
        # Call the fill_and_submit_application_form method with auto_submit=False
        return self.fill_and_submit_application_form(
            job_url=job_url,
            resume_data=resume_data,
            application_data=application_data,
            resume_file_path=resume_file_path,
            cover_letter_file_path=cover_letter_file_path,
            auto_submit=False
        )
    
    def fill_and_submit_application_form(self, job_url, resume_data, application_data, resume_file_path=None, cover_letter_file_path=None, auto_submit=True):
        """Fill out an external application form and optionally submit it
        
        Args:
            job_url: URL of the job application
            resume_data: Dict containing parsed resume information
            application_data: Dict containing customized application materials
            resume_file_path: Path to the resume file
            cover_letter_file_path: Path to the cover letter file
            auto_submit: Whether to automatically click the submit button
            
        Returns:
            dict: Result of the form filling and submission
        """
        if not job_url:
            return {
                'success': False,
                'error': 'No job URL provided',
                'filled_fields': 0,
                'submission_successful': False
            }
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to the job application URL
            self.driver.get(job_url)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
            except TimeoutException:
                logger.warning("No form element found on the page, trying to find input elements")
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "input"))
                    )
                except TimeoutException:
                    return {
                        'success': False,
                        'error': 'No form or input elements found on the page',
                        'filled_fields': 0,
                        'submission_successful': False
                    }
            
            # Look for common form fields
            form_fields = (
                self.driver.find_elements(By.TAG_NAME, "input") +
                self.driver.find_elements(By.TAG_NAME, "textarea") +
                self.driver.find_elements(By.TAG_NAME, "select")
            )
            
            filled_fields = 0
            
            # Extract contact info, education, and experience from resume data
            contact_info = resume_data.get('contact_info', {})
            education_info = resume_data.get('education', [])
            experience_info = resume_data.get('experience', [])
            skills_info = resume_data.get('skills', [])
            
            # Prepare values for common fields
            field_values = {
                'first_name': contact_info.get('name', '').split()[0] if contact_info.get('name') else '',
                'last_name': contact_info.get('name', '').split()[-1] if contact_info.get('name') and len(contact_info.get('name', '').split()) > 1 else '',
                'full_name': contact_info.get('name', ''),
                'email': contact_info.get('email', ''),
                'phone': contact_info.get('phone', ''),
                
                # Address fields - these would come from a more complete resume parser
                'address': '',
                'city': '',
                'state': '',
                'zip': '',
                'country': '',
                
                # Professional fields
                'linkedin': '',
                'website': '',
                'years_of_experience': '3',  # Default value
                
                # Work authorization - default to yes
                'work_authorization': 'Yes',
                
                # Education fields - extract from the first education entry if available
                'education_level': 'Bachelor',  # Default value
                'university': education_info[0] if education_info else '',
                'major': '',
                'graduation_year': '',
                
                # Experience fields - extract from the first experience entry if available
                'current_job_title': experience_info[0].split(' at ')[0] if experience_info and ' at ' in experience_info[0] else '',
                'current_company': experience_info[0].split(' at ')[1] if experience_info and ' at ' in experience_info[0] else '',
                
                # Cover letter
                'cover_letter': application_data.get('cover_letter', '')
            }
            
            # Process each field
            for field in form_fields:
                # Skip hidden fields
                if field.get_attribute('type') == 'hidden':
                    continue
                
                # Get field attributes
                field_id = field.get_attribute('id') or ''
                field_name = field.get_attribute('name') or ''
                field_type = field.get_attribute('type') or ''
                field_placeholder = field.get_attribute('placeholder') or ''
                field_aria_label = field.get_attribute('aria-label') or ''
                
                # Try to find associated label
                field_label = ''
                if field_id:
                    try:
                        label_elem = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                        field_label = label_elem.text
                    except NoSuchElementException:
                        pass
                
                # Determine field purpose
                field_purpose = self._determine_field_purpose(
                    field_id, field_name, field_label, field_placeholder, field_aria_label
                )
                
                if not field_purpose:
                    continue
                
                # Fill field based on its purpose and type
                try:
                    # Handle file upload fields
                    if field_type == 'file':
                        if field_purpose == 'resume' and resume_file_path:
                            field.send_keys(resume_file_path)
                            filled_fields += 1
                        elif field_purpose == 'cover_letter' and cover_letter_file_path:
                            field.send_keys(cover_letter_file_path)
                            filled_fields += 1
                    
                    # Handle select fields
                    elif field.tag_name == 'select':
                        select = Select(field)
                        
                        # Education level
                        if field_purpose == 'education_level':
                            options = [o.text.lower() for o in select.options]
                            if 'bachelor' in options:
                                select.select_by_visible_text('Bachelor')
                                filled_fields += 1
                            elif 'bachelor\'s' in options:
                                select.select_by_visible_text('Bachelor\'s')
                                filled_fields += 1
                            elif len(options) > 1:  # Select an option that's not the first (often a placeholder)
                                select.select_by_index(1)
                                filled_fields += 1
                        
                        # Work authorization
                        elif field_purpose == 'work_authorization':
                            options = [o.text.lower() for o in select.options]
                            if 'yes' in options:
                                select.select_by_visible_text('Yes')
                                filled_fields += 1
                            elif len(options) > 1:
                                # Try to find a positive option
                                for i, option in enumerate(options):
                                    if 'yes' in option or 'authorized' in option or 'eligible' in option:
                                        select.select_by_index(i)
                                        filled_fields += 1
                                        break
                                else:
                                    # If no suitable option, select the first non-placeholder
                                    select.select_by_index(1)
                                    filled_fields += 1
                        
                        # Years of experience
                        elif field_purpose == 'years_of_experience':
                            options = [o.text.lower() for o in select.options]
                            for i, option in enumerate(options):
                                if '3' in option or '2-5' in option or '2 to 5' in option:
                                    select.select_by_index(i)
                                    filled_fields += 1
                                    break
                            else:
                                # If no suitable option, select a middle option
                                if len(options) > 2:
                                    select.select_by_index(len(options) // 2)
                                    filled_fields += 1
                    
                    # Handle text fields
                    elif field_type in ('text', 'email', 'tel', 'url', '') or field.tag_name == 'textarea':
                        value = field_values.get(field_purpose, '')
                        if value:
                            # For textareas, sometimes we need to clear first
                            if field.tag_name == 'textarea':
                                field.clear()
                            field.send_keys(value)
                            filled_fields += 1
                    
                    # Handle checkbox fields
                    elif field_type == 'checkbox':
                        # Work authorization checkbox - check it
                        if field_purpose == 'work_authorization':
                            if not field.is_selected():
                                field.click()
                                filled_fields += 1
                
                except (ElementNotInteractableException, NoSuchElementException) as e:
                    logger.warning(f"Could not interact with field {field_id or field_name}: {str(e)}")
                    continue
            
            # Try to find the submit button
            submit_button = self._find_submit_button()
            
            # Determine button type if found
            button_type = None
            submission_successful = False
            submission_error = None
            
            if submit_button:
                # Get button identifiers
                button_text = submit_button.text.lower()
                button_value = submit_button.get_attribute('value') or ''
                button_id = submit_button.get_attribute('id') or ''
                button_name = submit_button.get_attribute('name') or ''
                button_class = submit_button.get_attribute('class') or ''
                button_aria_label = submit_button.get_attribute('aria-label') or ''
                
                button_identifiers = f"{button_text} {button_value} {button_id} {button_name} {button_class} {button_aria_label}".lower()
                
                # Check if it's an apply button or submit button
                for keyword in self.field_mapping['apply_button']:
                    if keyword in button_identifiers or re.search(r'\b' + re.escape(keyword) + r'\b', button_identifiers):
                        button_type = 'apply_button'
                        break
                
                if not button_type:
                    for keyword in self.field_mapping['submit_button']:
                        if keyword in button_identifiers or re.search(r'\b' + re.escape(keyword) + r'\b', button_identifiers):
                            button_type = 'submit_button'
                            break
                
                if not button_type:
                    button_type = 'generic_button'
                
                # Click the submit button if auto_submit is enabled
                if auto_submit:
                    try:
                        # Take a screenshot before submitting (for record keeping)
                        screenshot_path = f"application_screenshot_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        
                        # Click the submit button
                        logger.info(f"Clicking submit button: {button_text}")
                        submit_button.click()
                        
                        # Wait for page to change to confirm submission
                        current_url = self.driver.current_url
                        time.sleep(3)  # Short wait for page transition
                        
                        # Check if URL changed or if there's a success message
                        if current_url != self.driver.current_url:
                            submission_successful = True
                            logger.info(f"Application submitted successfully - URL changed from {current_url} to {self.driver.current_url}")
                        else:
                            # Look for success messages
                            try:
                                success_elements = self.driver.find_elements(By.XPATH, 
                                    "//*[contains(text(), 'success') or contains(text(), 'thank you') or contains(text(), 'received') or contains(text(), 'confirmed')]")
                                
                                if success_elements:
                                    submission_successful = True
                                    logger.info("Application submitted successfully - Success message found")
                                else:
                                    # Check for error messages
                                    error_elements = self.driver.find_elements(By.XPATH, 
                                        "//*[contains(text(), 'error') or contains(text(), 'failed') or contains(text(), 'invalid')]")
                                    
                                    if error_elements:
                                        submission_successful = False
                                        submission_error = "Error message found on page after submission"
                                        logger.warning(f"Submission may have failed: {submission_error}")
                                    else:
                                        # If we can't determine success/failure, assume it worked
                                        submission_successful = True
                                        logger.info("Assuming application submitted successfully - no clear indicators")
                            except Exception as e:
                                logger.warning(f"Error checking submission status: {str(e)}")
                                submission_successful = False
                                submission_error = f"Error checking submission status: {str(e)}"
                    except Exception as e:
                        logger.error(f"Error clicking submit button: {str(e)}")
                        submission_successful = False
                        submission_error = f"Error clicking submit button: {str(e)}"
            else:
                submission_successful = False
                submission_error = "No submit button found"
            
            return {
                'success': True,
                'filled_fields': filled_fields,
                'submit_button_found': submit_button is not None,
                'button_type': button_type,
                'button_text': submit_button.text if submit_button else None,
                'url': job_url,
                'submission_successful': submission_successful,
                'submission_error': submission_error,
                'submission_notes': "Automatically submitted" if submission_successful else (submission_error or "Form filled but not submitted")
            }
            
        except Exception as e:
            logger.error(f"Error filling application form: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filled_fields': 0,
                'submission_successful': False,
                'submission_error': str(e)
            }
        finally:
            self.close_driver()
    
    def _determine_field_purpose(self, field_id, field_name, field_label, field_placeholder, field_aria_label):
        """Determine the purpose of a form field"""
        # Combine all field identifiers into a single string for matching
        field_identifiers = (
            f"{field_id} {field_name} {field_label} "
            f"{field_placeholder} {field_aria_label}"
        ).lower()
        
        # Check each field purpose against identifiers
        for purpose, keywords in self.field_mapping.items():
            if purpose not in ['apply_button', 'submit_button']:  # Skip button mappings
                for keyword in keywords:
                    if keyword in field_identifiers:
                        return purpose
        
        return None
    
    def _find_submit_button(self):
        """Find the submit button on the form"""
        # Look for buttons and input[type=submit]
        buttons = (
            self.driver.find_elements(By.TAG_NAME, "button") +
            self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']") +
            self.driver.find_elements(By.CSS_SELECTOR, "input[type='button']") +
            self.driver.find_elements(By.CSS_SELECTOR, "a.button") +
            self.driver.find_elements(By.CSS_SELECTOR, "a.btn") +
            self.driver.find_elements(By.CSS_SELECTOR, "[role='button']") +
            self.driver.find_elements(By.CSS_SELECTOR, ".button") +
            self.driver.find_elements(By.CSS_SELECTOR, ".btn")
        )
        
        # First, look for final submission buttons as they are most likely to be what we want
        submit_button = self._find_button_by_type(buttons, 'submit_button')
        if submit_button:
            return submit_button
            
        # If no submit button is found, look for initial apply buttons
        apply_button = self._find_button_by_type(buttons, 'apply_button')
        if apply_button:
            return apply_button
            
        # As a fallback, look for any submit-like button
        for button in buttons:
            # Check type attribute for "submit"
            button_type = button.get_attribute('type') or ''
            if button_type.lower() == 'submit':
                return button
                
        return None
        
    def _find_button_by_type(self, buttons, button_type):
        """Find a button by its type (submit_button or apply_button)"""
        for button in buttons:
            # Get button text and attributes
            button_text = button.text.lower()
            button_value = button.get_attribute('value') or ''
            button_id = button.get_attribute('id') or ''
            button_name = button.get_attribute('name') or ''
            button_class = button.get_attribute('class') or ''
            button_aria_label = button.get_attribute('aria-label') or ''
            
            # Combine all button identifiers
            button_identifiers = f"{button_text} {button_value} {button_id} {button_name} {button_class} {button_aria_label}".lower()
            
            # Check for button-type-related keywords
            for keyword in self.field_mapping[button_type]:
                if keyword in button_identifiers:
                    return button
                    
            # Check for exact matches (for shorter keywords like "apply" or "submit")
            for keyword in self.field_mapping[button_type]:
                # Check for exact word boundaries
                if re.search(r'\b' + re.escape(keyword) + r'\b', button_identifiers):
                    return button
        
        return None