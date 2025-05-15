import os
import openai
import re
import json
import requests
from dotenv import load_dotenv
from app.config import Config

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Anthropic API settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", Config.ANTHROPIC_API_KEY)
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

def generate_application(resume_data, job_data):
    """Generate a customized job application based on resume and job data
    
    Args:
        resume_data: Dict containing parsed resume information
        job_data: Dict containing job details
        
    Returns:
        dict: Customized application materials
    """
    # Create a tailored cover letter
    cover_letter = _generate_cover_letter(resume_data, job_data)
    
    # Customize resume bullet points to match job requirements
    tailored_resume = _tailor_resume(resume_data, job_data)
    
    # Prepare application answers for common questions
    application_answers = _generate_application_answers(resume_data, job_data)
    
    return {
        'cover_letter': cover_letter,
        'tailored_resume': tailored_resume,
        'application_answers': application_answers
    }

def _generate_cover_letter(resume_data, job_data):
    """Generate a tailored cover letter using Anthropic or OpenAI's API"""
    try:
        # Extract key information for prompt
        applicant_name = resume_data.get('contact_info', {}).get('name', 'Applicant')
        job_title = job_data.get('title', 'the position')
        company_name = job_data.get('company', 'your company')
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        
        # Create a prompt for the AI
        prompt = f"""Write a compelling, top-tier cover letter for {applicant_name} applying for the {job_title} role at {company_name}. The letter should serve as a powerful pitch that will grab the recruiter's attention immediately.

Job Description:
{job_data.get('description', 'Not provided')}

Applicant Skills:
{', '.join(skills) if skills else 'Not provided'}

Applicant Experience:
{'; '.join(experience[:5]) if experience else 'Not provided'}

Education:
{'; '.join(resume_data.get('education', [])[:2]) if resume_data.get('education') else 'Not provided'}

IMPORTANT GUIDELINES:
1. Create a DETAILED, personalized cover letter that specifically connects the applicant's experience to the job requirements
2. Begin with a compelling hook that immediately grabs attention 
3. Clearly demonstrate deep understanding of the {company_name}'s industry and challenges
4. Highlight 3-4 SPECIFIC achievements from past experience that directly relate to this role's requirements
5. Use metrics and quantifiable results where possible (e.g., "increased efficiency by 35%")
6. Explain exactly how the applicant's unique combination of skills addresses the company's current needs
7. Show genuine enthusiasm for the company with specific details about why they stand out in their industry
8. Include a strong call-to-action closing paragraph that expresses confidence and interest in discussing further
9. Follow a professional format (date, greeting, body, closing, signature)
10. Aim for 350-500 words - detailed enough to be compelling but concise enough to respect the reader's time

This letter should be so well-tailored that the recruiter immediately recognizes the perfect fit between candidate and position.
"""
        
        # Use Anthropic API if enabled, otherwise use OpenAI
        if Config.USE_ANTHROPIC and ANTHROPIC_API_KEY:
            cover_letter = _generate_cover_letter_with_anthropic(prompt)
        else:
            cover_letter = _generate_cover_letter_with_openai(prompt)
        
        # If no API key is set or generation failed, use a fallback template
        if not cover_letter:
            cover_letter = _generate_fallback_cover_letter(resume_data, job_data)
        
        return cover_letter
    
    except Exception as e:
        # Use fallback template if API call fails
        print(f"Error generating cover letter: {e}")
        return _generate_fallback_cover_letter(resume_data, job_data)


def _generate_cover_letter_with_anthropic(prompt):
    """Generate a cover letter using Anthropic's Claude API"""
    if not ANTHROPIC_API_KEY:
        return None
        
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(ANTHROPIC_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        response_data = response.json()
        cover_letter = response_data.get("content", [{}])[0].get("text", "").strip()
        
        return cover_letter
    
    except Exception as e:
        print(f"Error generating cover letter with Anthropic API: {e}")
        return None


def _generate_cover_letter_with_openai(prompt):
    """Generate a cover letter using OpenAI's API"""
    if not openai.api_key:
        return None
        
    try:
        # Call OpenAI API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Use appropriate engine
            prompt=prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        # Get the generated cover letter
        cover_letter = response.choices[0].text.strip()
        return cover_letter
    
    except Exception as e:
        print(f"Error generating cover letter with OpenAI: {e}")
        return None

def _generate_fallback_cover_letter(resume_data, job_data):
    """Generate a cover letter using a template when API is unavailable"""
    name = resume_data.get('contact_info', {}).get('name', 'Applicant')
    email = resume_data.get('contact_info', {}).get('email', 'applicant@example.com')
    job_title = job_data.get('title', 'the position')
    company = job_data.get('company', 'your company')
    
    # Get top skills (up to 3)
    skills = resume_data.get('skills', [])[:3]
    skills_text = ', '.join(skills) if skills else 'relevant skills'
    
    # Current date
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Basic cover letter template
    cover_letter = f"""{current_date}

Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}. With my background and expertise in {skills_text}, I believe I would be a valuable addition to your team.

Throughout my career, I have developed strong skills in problem-solving, collaboration, and delivering high-quality results. I am particularly drawn to {company} because of its reputation for innovation and excellence in the industry.

My resume provides additional details about my experience and qualifications. I would welcome the opportunity to discuss how my background and skills would benefit your organization.

Thank you for considering my application. I look forward to the possibility of working with {company}.

Sincerely,
{name}
{email}
"""
    
    return cover_letter

def _tailor_resume(resume_data, job_data):
    """Customize resume data to better match the job description"""
    # Create a deep copy to avoid modifying the original
    tailored_resume = {k: v for k, v in resume_data.items()}
    
    # Extract job details
    job_title = job_data.get('title', '').lower()
    job_description = job_data.get('description', '').lower()
    company = job_data.get('company', '').lower()
    
    # Check if we have enough data to perform tailoring
    if not job_description:
        return tailored_resume
    
    # Extract potential requirements and skills from job description using regex
    skill_patterns = [
        r'proficient in ([^.]*)',
        r'experience with ([^.]*)',
        r'knowledge of ([^.]*)',
        r'familiarity with ([^.]*)',
        r'skills:? ([^.]*)',
        r'requirements:? ([^.]*)',
        r'qualifications:? ([^.]*)',
        r'expertise in ([^.]*)',
        r'background in ([^.]*)',
        r'understanding of ([^.]*)'
    ]
    
    extracted_requirements = set()
    for pattern in skill_patterns:
        matches = re.finditer(pattern, job_description)
        for match in matches:
            extracted_text = match.group(1).strip().lower()
            # Split by common delimiters
            for delimiter in [',', ';', 'and', 'or']:
                extracted_text = extracted_text.replace(delimiter, '|')
            skills = [s.strip() for s in extracted_text.split('|') if s.strip()]
            extracted_requirements.update(skills)
    
    # Common skill keywords from the original function
    common_keywords = [
        "leadership", "management", "communication", "analysis", "research",
        "development", "design", "testing", "project", "team", "collaboration",
        "customer", "client", "service", "problem-solving", "innovation", "strategy",
        "planning", "implementation", "evaluation", "reporting", "presentation",
        "sales", "marketing", "budget", "financial", "compliance", "regulation",
        "quality", "assurance", "training", "mentoring"
    ]
    
    # Technical keywords - expanded
    tech_keywords = [
        # Programming languages
        "python", "java", "javascript", "typescript", "c++", "c#", ".net", "ruby", "perl",
        "php", "swift", "kotlin", "golang", "go", "scala", "r", "matlab", "cobol", "fortran",
        
        # Web technologies
        "html", "css", "jquery", "react", "angular", "vue", "node", "express", "django",
        "flask", "spring", "bootstrap", "tailwind", "rest", "graphql", "json", "xml",
        
        # Database
        "sql", "mysql", "postgresql", "mongodb", "nosql", "oracle", "firebase",
        "dynamodb", "cassandra", "redis", "neo4j", "elasticsearch", "couchbase",
        
        # Cloud & DevOps
        "cloud", "aws", "azure", "gcp", "devops", "ci/cd", "jenkins", "github actions",
        "docker", "kubernetes", "terraform", "ansible", "chef", "puppet", "prometheus",
        "grafana", "splunk", "elk", "virtualization", "vmware", "serverless",
        
        # Methodologies
        "agile", "scrum", "kanban", "lean", "waterfall", "prince2", "itil", "sdlc",
        
        # Data & AI
        "machine learning", "ai", "artificial intelligence", "data science", "nlp",
        "computer vision", "big data", "hadoop", "spark", "tableau", "power bi",
        "data visualization", "etl", "analytics", "statistics", "pandas", "tensorflow",
        "pytorch", "keras", "scikit-learn",
        
        # Infrastructure
        "networking", "security", "linux", "unix", "windows", "macos", "Active Directory",
        "firewall", "vpn", "load balancer", "cdn", "dns", "api gateway", "sso", "oauth",
        
        # Mobile
        "mobile", "ios", "android", "react native", "flutter", "xamarin", "swift", "kotlin",
        
        # Architecture
        "microservices", "monolith", "soa", "event-driven", "mvc", "mvvm", "rest",
        "distributed systems", "high availability", "fault tolerance", "scalability"
    ]
    
    # Find relevant keywords in job description
    relevant_keywords = []
    
    # First look for exact matches from extracted requirements
    for req in extracted_requirements:
        if len(req.split()) > 1:  # Multi-word requirement
            if req in job_description:
                relevant_keywords.append(req)
        else:  # Single word requirement
            # Use word boundary to avoid partial matches
            if re.search(r'\b' + re.escape(req) + r'\b', job_description):
                relevant_keywords.append(req)
    
    # Then look for common and tech keywords
    for keyword in common_keywords + tech_keywords:
        if keyword in job_description:
            # Use word boundary for more accurate matching
            if re.search(r'\b' + re.escape(keyword) + r'\b', job_description):
                relevant_keywords.append(keyword)
    
    # Tailor skills
    if 'skills' in tailored_resume and relevant_keywords:
        prioritized_skills = []
        other_skills = []
        
        # Enhanced algorithm for matching skills
        for skill in tailored_resume['skills']:
            skill_lower = skill.lower()
            
            # Exact match with relevant keywords
            if any(keyword == skill_lower for keyword in relevant_keywords):
                prioritized_skills.append(skill)
            # Partial match with multi-word skills
            elif any(keyword in skill_lower for keyword in relevant_keywords if len(keyword.split()) > 1):
                prioritized_skills.append(skill)
            # Word boundary match for single-word skills
            elif any(re.search(r'\b' + re.escape(keyword) + r'\b', skill_lower) for keyword in relevant_keywords if len(keyword.split()) == 1):
                prioritized_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Update skills order to prioritize relevant ones
        tailored_resume['skills'] = prioritized_skills + other_skills
    
    # Reorder experience to prioritize relevant experience
    if 'experience' in tailored_resume and isinstance(tailored_resume['experience'], list) and relevant_keywords:
        scored_experience = []
        
        for i, exp in enumerate(tailored_resume['experience']):
            exp_lower = exp.lower()
            # Calculate a relevance score based on keyword matches
            score = 0
            for keyword in relevant_keywords:
                if keyword in exp_lower:
                    score += 1
            
            # Also consider job title matches
            if job_title in exp_lower:
                score += 3
            
            # Add position to maintain original order in case of ties
            scored_experience.append((score, -i, exp))
        
        # Sort by score (descending) and then by original position
        scored_experience.sort(reverse=True)
        
        # Update experience list
        tailored_resume['experience'] = [exp for _, _, exp in scored_experience]
    
    # If education is a list, prioritize relevant education
    if 'education' in tailored_resume and isinstance(tailored_resume['education'], list) and relevant_keywords:
        scored_education = []
        
        for i, edu in enumerate(tailored_resume['education']):
            edu_lower = edu.lower()
            # Calculate a relevance score based on keyword matches
            score = 0
            for keyword in relevant_keywords:
                if keyword in edu_lower:
                    score += 1
            
            # Add position to maintain original order in case of ties
            scored_education.append((score, -i, edu))
        
        # Sort by score (descending) and then by original position
        scored_education.sort(reverse=True)
        
        # Update education list
        tailored_resume['education'] = [edu for _, _, edu in scored_education]
    
    # Add a flag to indicate the resume has been tailored
    tailored_resume['tailored_for_job'] = job_data.get('title', 'this position')
    
    return tailored_resume

def _generate_application_answers(resume_data, job_data):
    """Generate answers to common application questions"""
    # Common application questions
    common_questions = [
        "What makes you interested in this position?",
        "Why do you want to work for our company?",
        "What are your greatest strengths?",
        "What is your greatest weakness?",
        "Describe a challenging situation you've faced at work and how you handled it."
    ]
    
    answers = {}
    
    # Simple templated answers for now
    # In a real implementation, this would use more sophisticated AI-generated responses
    
    # Interest in position
    job_title = job_data.get('title', 'this position')
    skills = ', '.join(resume_data.get('skills', [])[:3]) if resume_data.get('skills') else 'my skills'
    answers[common_questions[0]] = f"I'm interested in the {job_title} role because it aligns well with my experience in {skills}. I believe my background has prepared me to make significant contributions in this position."
    
    # Interest in company
    company = job_data.get('company', 'your company')
    answers[common_questions[1]] = f"I've been following {company}'s work in the industry and am impressed by your innovation and commitment to excellence. I'm particularly drawn to your company culture and the opportunity to grow professionally in such an environment."
    
    # Strengths
    top_skills = resume_data.get('skills', [])[:2] if resume_data.get('skills') else ['problem-solving', 'adaptability']
    strengths = ', '.join(top_skills)
    answers[common_questions[2]] = f"My greatest strengths include {strengths}. Throughout my career, I've leveraged these skills to deliver results and overcome challenges."
    
    # Weakness
    answers[common_questions[3]] = "I sometimes tend to be overly detail-oriented, which can impact my efficiency. However, I've been working on improving my prioritization skills and focusing on the most impactful aspects of a project first, while still maintaining quality."
    
    # Challenge
    answers[common_questions[4]] = "In a previous role, I faced a tight deadline on a complex project when a team member unexpectedly left. I quickly reorganized our workflow, took on additional responsibilities, and communicated transparently with stakeholders. Despite the challenge, we delivered the project on time through effective collaboration and problem-solving."
    
    return answers