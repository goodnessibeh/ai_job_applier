import requests
import json
import logging
from app.models import UserSettings
import anthropic
import openai

# Setup logging
logger = logging.getLogger(__name__)

class ResumeImprover:
    """Class to generate resume improvement suggestions using AI APIs (OpenAI or Anthropic)"""
    
    def __init__(self, user_id=None, anthropic_api_key=None, openai_api_key=None):
        """
        Initialize ResumeImprover with user_id or explicit API keys
        
        Args:
            user_id (str, optional): User ID to fetch API keys from user settings
            anthropic_api_key (str, optional): Explicit Anthropic API key
            openai_api_key (str, optional): Explicit OpenAI API key
        """
        self.anthropic_api_key = anthropic_api_key
        self.openai_api_key = openai_api_key
        self.user_settings = None
        
        # If no explicit API keys, try to get from user settings
        if user_id:
            self.user_settings = UserSettings.query.filter_by(user_id=user_id).first()
            if self.user_settings:
                # Only set keys if not already provided explicitly
                if not self.anthropic_api_key and self.user_settings.anthropic_api_key:
                    self.anthropic_api_key = self.user_settings.anthropic_api_key
                if not self.openai_api_key and self.user_settings.openai_api_key:
                    self.openai_api_key = self.user_settings.openai_api_key
    
    def generate_improvement_suggestions(self, resume_data):
        """
        Generate improvement suggestions for a resume using AI APIs
        
        Args:
            resume_data (dict): Resume data including raw text and structured components
            
        Returns:
            dict: Improvement suggestions with different categories
        """
        # Format resume data into a more readable form for the LLM
        resume_text = self._format_resume_for_analysis(resume_data)
        
        # Determine which AI provider to use based on settings and available keys
        # Priority: User settings preference if available, then Anthropic if available, then OpenAI if available
        use_anthropic = True  # Default is Anthropic
        
        if self.user_settings:
            # Check user preferences if set
            if self.user_settings.use_anthropic and self.anthropic_api_key:
                use_anthropic = True
            elif self.user_settings.use_openai and self.openai_api_key:
                use_anthropic = False
        # If user has no preference, use available keys
        elif not self.anthropic_api_key and self.openai_api_key:
            use_anthropic = False
        
        # Try to generate suggestions with chosen provider
        if use_anthropic and self.anthropic_api_key:
            return self._generate_anthropic_suggestions(resume_text)
        elif self.openai_api_key:
            return self._generate_openai_suggestions(resume_text)
        else:
            logger.warning("No API keys available for any AI provider. Cannot generate resume improvements.")
            return {
                "success": False,
                "error": "API key is required for resume improvement suggestions.",
                "suggestions": None
            }
    
    def _generate_anthropic_suggestions(self, resume_text):
        """Generate suggestions using Anthropic API"""
        try:
            # Create the Anthropic client
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Call Anthropic API to get improvement suggestions
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                system="You are an expert career coach and resume writer. Your task is to provide constructive, detailed feedback on a resume to help the candidate improve their chances of getting interviews. Focus on content, formatting, wording, skills presentation, and achievement descriptions. Provide specific actionable suggestions.",
                messages=[
                    {
                        "role": "user", 
                        "content": f"""Here is a resume to analyze and improve:

{resume_text}

Provide a comprehensive analysis with specific suggestions for improvement in the following categories:
1. Overall Impression 
2. Content and Structure
3. Skills Presentation
4. Experience Descriptions (focus on achievements vs responsibilities)
5. Education Section
6. Formatting and Readability
7. Keywords and ATS Optimization
8. Most Critical Changes Needed (top 3)

For each category, provide concrete examples of how to improve. Be specific about text to change, rephrase or remove. Format your response as properly structured JSON with the following fields:
- overall_impression: A brief summary of overall impression and resume strength (1-2 paragraphs)
- content_structure: Suggestions for improving the overall content organization
- skills_presentation: How to better present skills
- experience_descriptions: Specific suggestions to improve job descriptions
- education_section: Improvements for education presentation
- formatting_readability: Formatting and readability issues
- keywords_ats: Keyword optimization suggestions
- critical_changes: List of top 3 most important changes to make

Make sure your JSON is properly formatted."""
                    }
                ]
            )
            
            # Extract and parse the response
            try:
                # Attempt to extract the JSON content from the response
                raw_content = response.content[0].text
                
                # Check if the content is enclosed in triple backticks
                if "```json" in raw_content and "```" in raw_content.split("```json")[1]:
                    # Extract the JSON part
                    json_content = raw_content.split("```json")[1].split("```")[0]
                else:
                    # Try to find JSON-like structure
                    json_start = raw_content.find('{')
                    json_end = raw_content.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > 0:
                        json_content = raw_content[json_start:json_end]
                    else:
                        json_content = raw_content
                
                # Parse the JSON content
                suggestions_data = json.loads(json_content)
                
                return {
                    "success": True,
                    "provider": "anthropic",
                    "suggestions": suggestions_data
                }
            except Exception as e:
                logger.error(f"Error parsing Anthropic API response: {str(e)}")
                # Fallback to providing the raw text if JSON parsing fails
                return {
                    "success": True,
                    "provider": "anthropic",
                    "raw_response": response.content[0].text,
                    "suggestions": None,
                    "parsing_error": str(e)
                }
                
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            return {
                "success": False,
                "provider": "anthropic",
                "error": str(e),
                "suggestions": None
            }
    
    def _generate_openai_suggestions(self, resume_text):
        """Generate suggestions using OpenAI API"""
        try:
            # Create the OpenAI client
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            # Call OpenAI API to get improvement suggestions
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert career coach and resume writer. Your task is to provide constructive, detailed feedback on a resume to help the candidate improve their chances of getting interviews. Focus on content, formatting, wording, skills presentation, and achievement descriptions. Provide specific actionable suggestions."
                    },
                    {
                        "role": "user", 
                        "content": f"""Here is a resume to analyze and improve:

{resume_text}

Provide a comprehensive analysis with specific suggestions for improvement in the following categories:
1. Overall Impression 
2. Content and Structure
3. Skills Presentation
4. Experience Descriptions (focus on achievements vs responsibilities)
5. Education Section
6. Formatting and Readability
7. Keywords and ATS Optimization
8. Most Critical Changes Needed (top 3)

For each category, provide concrete examples of how to improve. Be specific about text to change, rephrase or remove. Format your response as properly structured JSON with the following fields:
- overall_impression: A brief summary of overall impression and resume strength (1-2 paragraphs)
- content_structure: Suggestions for improving the overall content organization
- skills_presentation: How to better present skills
- experience_descriptions: Specific suggestions to improve job descriptions
- education_section: Improvements for education presentation
- formatting_readability: Formatting and readability issues
- keywords_ats: Keyword optimization suggestions
- critical_changes: List of top 3 most important changes to make

Make sure your JSON is properly formatted."""
                    }
                ]
            )
            
            # Extract and parse the response
            try:
                # Attempt to extract the JSON content from the response
                raw_content = response.choices[0].message.content
                
                # Check if the content is enclosed in triple backticks
                if "```json" in raw_content and "```" in raw_content.split("```json")[1]:
                    # Extract the JSON part
                    json_content = raw_content.split("```json")[1].split("```")[0]
                else:
                    # Try to find JSON-like structure
                    json_start = raw_content.find('{')
                    json_end = raw_content.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > 0:
                        json_content = raw_content[json_start:json_end]
                    else:
                        json_content = raw_content
                
                # Parse the JSON content
                suggestions_data = json.loads(json_content)
                
                return {
                    "success": True,
                    "provider": "openai",
                    "suggestions": suggestions_data
                }
            except Exception as e:
                logger.error(f"Error parsing OpenAI API response: {str(e)}")
                # Fallback to providing the raw text if JSON parsing fails
                return {
                    "success": True,
                    "provider": "openai",
                    "raw_response": raw_content,
                    "suggestions": None,
                    "parsing_error": str(e)
                }
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {
                "success": False,
                "provider": "openai",
                "error": str(e),
                "suggestions": None
            }
    
    def _format_resume_for_analysis(self, resume_data):
        """
        Format the resume data into a readable text form for the LLM
        
        Args:
            resume_data (dict): Resume data including both structured data and raw text
            
        Returns:
            str: Formatted resume text
        """
        # If formatted_text is available, use it to preserve structure
        if 'formatted_text' in resume_data and resume_data['formatted_text']:
            formatted_sections = []
            
            for section in resume_data['formatted_text']:
                if section['type'] == 'paragraph':
                    formatted_sections.append(section['content'])
                elif section['type'] == 'bullet_list':
                    bullet_items = '\n'.join([f"• {item.strip()}" for item in section['items']])
                    formatted_sections.append(bullet_items)
            
            return '\n\n'.join(formatted_sections)
        
        # Fallback to raw text if formatted text is not available
        elif 'raw_text' in resume_data:
            return resume_data['raw_text']
        
        # If no raw text is available, construct from structured data
        else:
            resume_text = []
            
            # Add contact info
            if 'contact_info' in resume_data:
                contact = resume_data['contact_info']
                if 'name' in contact:
                    resume_text.append(contact['name'])
                if 'email' in contact:
                    resume_text.append(contact['email'])
                if 'phone' in contact:
                    resume_text.append(contact['phone'])
                resume_text.append("")
            
            # Add skills
            if 'skills' in resume_data and resume_data['skills']:
                resume_text.append("SKILLS")
                for skill in resume_data['skills']:
                    resume_text.append(f"• {skill}")
                resume_text.append("")
            
            # Add experience
            if 'experience' in resume_data and resume_data['experience']:
                resume_text.append("EXPERIENCE")
                for exp in resume_data['experience']:
                    resume_text.append(exp)
                resume_text.append("")
            
            # Add education
            if 'education' in resume_data and resume_data['education']:
                resume_text.append("EDUCATION")
                for edu in resume_data['education']:
                    resume_text.append(edu)
                resume_text.append("")
            
            return '\n'.join(resume_text)