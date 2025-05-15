import os
import PyPDF2
import docx
import re
import json
from werkzeug.utils import secure_filename

def parse_resume(file):
    """Extract information from a resume file (PDF or DOCX)
    
    Args:
        file: A file object from request.files
        
    Returns:
        dict: Structured resume data
    """
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext == '.pdf':
        text, formatted_text = _extract_text_from_pdf(file)
    elif file_ext == '.docx':
        text, formatted_text = _extract_text_from_docx(file)
    else:
        raise ValueError(f'Unsupported file format: {file_ext}')
    
    # Parse the extracted text
    parsed_data = _parse_resume_text(text)
    
    # Add the raw text with formatting preserved
    parsed_data['raw_text'] = text
    parsed_data['formatted_text'] = formatted_text
    
    return parsed_data

def _extract_text_from_pdf(file):
    """Extract text from a PDF file
    
    Returns:
        tuple: (plain text, formatted text with preserved structure)
    """
    reader = PyPDF2.PdfReader(file)
    plain_text = ''
    formatted_text = []
    
    for page in reader.pages:
        page_text = page.extract_text()
        plain_text += page_text
        
        # Process text to preserve structure
        page_sections = []
        current_section = []
        for line in page_text.split('\n'):
            # Detect if line is a bullet point
            is_bullet = line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*')
            is_bullet = is_bullet or re.match(r'^\s*\d+\.', line.strip()) is not None  # Numbered bullets
            
            # If empty line, start a new paragraph
            if not line.strip():
                if current_section:
                    page_sections.append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_section)
                    })
                    current_section = []
            # If bullet point, add as a list item
            elif is_bullet:
                # If we were in a paragraph, finish it
                if current_section and not current_section[0].strip().startswith(('•', '-', '*')) and not re.match(r'^\s*\d+\.', current_section[0].strip()):
                    page_sections.append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_section)
                    })
                    current_section = []
                    
                # Start a new bullet point or add to existing bullet list
                if not current_section:
                    current_section.append(line)
                elif current_section[0].strip().startswith(('•', '-', '*')) or re.match(r'^\s*\d+\.', current_section[0].strip()):
                    current_section.append(line)
                else:
                    page_sections.append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_section)
                    })
                    current_section = [line]
            else:
                # Regular paragraph line
                current_section.append(line)
                
        # Add any remaining content
        if current_section:
            if current_section[0].strip().startswith(('•', '-', '*')) or re.match(r'^\s*\d+\.', current_section[0].strip()):
                page_sections.append({
                    'type': 'bullet_list',
                    'items': current_section
                })
            else:
                page_sections.append({
                    'type': 'paragraph',
                    'content': '\n'.join(current_section)
                })
            
        formatted_text.extend(page_sections)
    
    return plain_text, formatted_text

def _extract_text_from_docx(file):
    """Extract text from a DOCX file
    
    Returns:
        tuple: (plain text, formatted text with preserved structure)
    """
    doc = docx.Document(file)
    plain_text = ''
    formatted_text = []
    
    # Process paragraphs to identify bullets and sections
    current_section = []
    current_section_type = None
    
    for para in doc.paragraphs:
        plain_text += para.text + '\n'
        
        # Skip empty paragraphs
        if not para.text.strip():
            # If we have content in the current section, add it
            if current_section:
                if current_section_type == 'bullet_list':
                    formatted_text.append({
                        'type': 'bullet_list',
                        'items': current_section
                    })
                else:
                    formatted_text.append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_section)
                    })
                current_section = []
                current_section_type = None
            continue
        
        # Detect bullet points
        is_bullet = False
        if para.style.name.startswith('List'):
            is_bullet = True
        elif para.text.strip().startswith(('•', '-', '*')) or re.match(r'^\s*\d+\.', para.text.strip()):
            is_bullet = True
            
        # If this is a bullet point
        if is_bullet:
            # If we were in a paragraph section, finish it
            if current_section and current_section_type != 'bullet_list':
                formatted_text.append({
                    'type': 'paragraph',
                    'content': '\n'.join(current_section)
                })
                current_section = []
            
            # Add to bullet list
            current_section.append(para.text)
            current_section_type = 'bullet_list'
        else:
            # If we were in a bullet list, finish it
            if current_section and current_section_type == 'bullet_list':
                formatted_text.append({
                    'type': 'bullet_list',
                    'items': current_section
                })
                current_section = []
            
            # Add to paragraph
            current_section.append(para.text)
            current_section_type = 'paragraph'
    
    # Add any remaining content
    if current_section:
        if current_section_type == 'bullet_list':
            formatted_text.append({
                'type': 'bullet_list',
                'items': current_section
            })
        else:
            formatted_text.append({
                'type': 'paragraph',
                'content': '\n'.join(current_section)
            })
    
    return plain_text, formatted_text

def _parse_resume_text(text):
    """Parse resume text into structured data"""
    data = {
        'contact_info': _extract_contact_info(text),
        'education': _extract_education(text),
        'experience': _extract_experience(text),
        'skills': _extract_skills(text)
    }
    
    return data

def _extract_contact_info(text):
    """Extract contact information from text"""
    # Simple patterns for contact info
    email_pattern = r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    
    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)
    
    contact_info = {}
    if email:
        contact_info['email'] = email.group(0)
    if phone:
        contact_info['phone'] = phone.group(0)
    
    # Extract name (simplified approach - might need refinement)
    # Assuming name is at the beginning of the resume
    first_lines = text.split('\n')[:3]
    for line in first_lines:
        # Check if line is not email, phone, or very short
        if not re.search(email_pattern, line) and not re.search(phone_pattern, line) and len(line.strip()) > 3:
            contact_info['name'] = line.strip()
            break
    
    return contact_info

def _extract_education(text):
    """Extract education information from text"""
    education = []
    
    # Common education section markers
    edu_markers = ['EDUCATION', 'Education', 'ACADEMIC BACKGROUND', 'Academic Background']
    
    # Find education section using markers
    edu_section = None
    for marker in edu_markers:
        if marker in text:
            parts = text.split(marker, 1)
            if len(parts) > 1:
                edu_section = parts[1]
                break
    
    if not edu_section:
        return education
    
    # Find end of education section (start of next section)
    next_section_markers = ['EXPERIENCE', 'Experience', 'WORK HISTORY', 'SKILLS', 'Skills']
    for marker in next_section_markers:
        if marker in edu_section:
            edu_section = edu_section.split(marker, 1)[0]
    
    # Basic parsing of education entries (simplified)
    # This will need refinement for better accuracy
    degree_markers = ['Bachelor', 'Master', 'Ph.D', 'MBA', 'B.S.', 'M.S.', 'B.A.', 'M.A.']
    for line in edu_section.split('\n'):
        for marker in degree_markers:
            if marker in line:
                education.append(line.strip())
                break
    
    return education

def _extract_experience(text):
    """Extract work experience from text"""
    experience = []
    
    # Common experience section markers
    exp_markers = ['EXPERIENCE', 'Experience', 'WORK HISTORY', 'Work History', 'EMPLOYMENT']
    
    # Find experience section using markers
    exp_section = None
    for marker in exp_markers:
        if marker in text:
            parts = text.split(marker, 1)
            if len(parts) > 1:
                exp_section = parts[1]
                break
    
    if not exp_section:
        return experience
    
    # Find end of experience section (start of next section)
    next_section_markers = ['EDUCATION', 'Education', 'SKILLS', 'Skills']
    for marker in next_section_markers:
        if marker in exp_section:
            exp_section = exp_section.split(marker, 1)[0]
    
    # Basic parsing of experience entries (simplified)
    # This is a simplified approach and would need more robust parsing
    date_pattern = r'(\b\d{1,2}/\d{1,2}\b|\b\d{4}\b|\bPresent\b|\bCurrent\b)'
    
    current_experience = None
    for line in exp_section.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # If line has dates, it's likely a new job entry
        if re.search(date_pattern, line):
            if current_experience:
                experience.append(current_experience)
            current_experience = line
        elif current_experience:  # Additional details for current job
            current_experience += " " + line
    
    # Add the last experience
    if current_experience:
        experience.append(current_experience)
    
    return experience

def _extract_skills(text):
    """Extract skills from text"""
    skills = []
    
    # Common skills section markers
    skill_markers = ['SKILLS', 'Skills', 'TECHNICAL SKILLS', 'Technical Skills']
    
    # Find skills section using markers
    skill_section = None
    for marker in skill_markers:
        if marker in text:
            parts = text.split(marker, 1)
            if len(parts) > 1:
                skill_section = parts[1]
                break
    
    if not skill_section:
        return skills
    
    # Find end of skills section (start of next section)
    next_section_markers = ['EDUCATION', 'Education', 'EXPERIENCE', 'Experience']
    for marker in next_section_markers:
        if marker in skill_section:
            skill_section = skill_section.split(marker, 1)[0]
    
    # Extract skills (simplified approach)
    # First, try to find bullet points or commas
    if '•' in skill_section or ',' in skill_section:
        if '•' in skill_section:
            skill_items = skill_section.split('•')
            for item in skill_items[1:]:  # Skip the first item (header)
                item = item.strip()
                if item:
                    skills.append(item.split('\n')[0])  # Take only the first line of each bullet point
        else:  # Use commas
            skill_items = skill_section.replace('\n', ', ').split(',')
            for item in skill_items:
                item = item.strip()
                if item:
                    skills.append(item)
    else:  # Fallback: use individual words
        # Preprocessed list of common technical skills (could be expanded)
        common_skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'Excel', 
                        'Word', 'PowerPoint', 'Communication', 'Leadership', 'Project Management',
                        'Agile', 'Scrum', 'Marketing', 'Sales', 'Customer Service', 'HTML', 'CSS',
                        'Machine Learning', 'Data Analysis', 'Statistics', 'Research', 'Writing']
        
        for skill in common_skills:
            if skill in text:
                skills.append(skill)
    
    return skills