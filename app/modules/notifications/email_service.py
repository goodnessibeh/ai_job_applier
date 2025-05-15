import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, smtp_server, smtp_port, username, password, from_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.enabled = all([smtp_server, smtp_port, username, password, from_email])
        
        # Initialize Jinja2 environment for email templates
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        # Create templates directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Create default templates if they don't exist
        self._ensure_default_templates_exist()
    
    def is_enabled(self):
        return self.enabled
        
    def _ensure_default_templates_exist(self):
        """Ensure default email templates exist in the templates directory"""
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        
        # Create application notification HTML template
        application_template_path = os.path.join(templates_dir, 'application_notification.html')
        if not os.path.exists(application_template_path):
            with open(application_template_path, 'w') as f:
                f.write(self._get_default_application_template())
            logger.info(f"Created default application notification template at {application_template_path}")
    
    def _get_default_application_template(self):
        """Return the default HTML template for application notifications"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Update</title>
    <style>
        /* Base styles */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 0;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            background-color: #4361ee;
            color: white;
            padding: 25px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        .content {
            padding: 25px 30px;
            color: #444;
        }
        .footer {
            background-color: #f1f2f6;
            padding: 20px 30px;
            color: #666;
            font-size: 13px;
            text-align: center;
            border-top: 1px solid #e1e5eb;
        }
        .button {
            display: inline-block;
            padding: 12px 25px;
            background-color: #4361ee;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            margin-top: 20px;
            text-align: center;
            transition: background-color 0.2s;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .button:hover {
            background-color: #3a56e4;
        }
        .summary {
            background-color: #f8fafc;
            border-radius: 6px;
            padding: 20px 25px;
            margin: 20px 0;
            border-left: 4px solid {% if success %}#10b981{% else %}#ef4444{% endif %};
        }
        .summary h2 {
            margin-top: 0;
            font-size: 18px;
            color: {% if success %}#10b981{% else %}#ef4444{% endif %};
        }
        .details {
            margin: 25px 0;
        }
        .detail-row {
            display: flex;
            border-bottom: 1px solid #eee;
            padding: 12px 0;
        }
        .detail-row:last-child {
            border-bottom: none;
        }
        .detail-label {
            flex: 0 0 40%;
            font-weight: 500;
            color: #555;
        }
        .detail-value {
            flex: 0 0 60%;
        }
        .success {
            color: #10b981;
            font-weight: 600;
        }
        .failed {
            color: #ef4444;
            font-weight: 600;
        }
        .highlight {
            font-weight: 600;
            color: #4361ee;
        }
        .message {
            background-color: #f8fafc;
            border-radius: 6px;
            padding: 15px 20px;
            margin: 20px 0;
            font-style: italic;
            color: #666;
        }
        
        /* Responsive styles */
        @media only screen and (max-width: 480px) {
            .header {
                padding: 20px 15px;
            }
            .content {
                padding: 20px 15px;
            }
            .summary {
                padding: 15px;
            }
            .detail-row {
                flex-direction: column;
            }
            .detail-label, .detail-value {
                flex: 0 0 100%;
            }
            .detail-label {
                margin-bottom: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Job Application {{ 'Submitted' if success else 'Update' }}</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Your job application has been {{ 'successfully submitted' if success else 'processed' }}.</p>
            
            <div class="summary">
                <h2>{{ 'Success' if success else 'Status Update' }}</h2>
                <p>Your application for <span class="highlight">{{ position }}</span> at <span class="highlight">{{ company }}</span> has been {{ '<span class="success">successfully submitted</span>' if success else '<span class="failed">processed with issues</span>' }}.</p>
            </div>
            
            <div class="details">
                <div class="detail-row">
                    <div class="detail-label">Position:</div>
                    <div class="detail-value">{{ position }}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Company:</div>
                    <div class="detail-value">{{ company }}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Location:</div>
                    <div class="detail-value">{{ location }}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Platform:</div>
                    <div class="detail-value">{{ platform }}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Applied On:</div>
                    <div class="detail-value">{{ timestamp }}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">Status:</div>
                    <div class="detail-value">{{ '<span class="success">Successful</span>' if success else '<span class="failed">Requires Attention</span>' }}</div>
                </div>
            </div>
            
            {% if message %}
            <div class="message">
                {{ message }}
            </div>
            {% endif %}
            
            {% if job_url %}
            <div style="text-align: center;">
                <a href="{{ job_url }}" class="button">View Job Posting</a>
            </div>
            {% endif %}
            
            <p>You can view your application history and status in your AI Job Applier dashboard.</p>
            <p>Best regards,<br>AI Job Applier Team</p>
        </div>
        <div class="footer">
            <p>This is an automated notification from AI Job Applier.</p>
            <p>© {{ current_year }} AI Job Applier. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
    
    def test_connection(self):
        """
        Test the SMTP connection to verify the configuration is correct.
        
        Returns:
            tuple: (success: bool, message: str) - success status and message
        """
        if not self.enabled:
            return False, "Email service is not properly configured. Please check your SMTP settings."
        
        try:
            # Create secure connection
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.username, self.password)
                
                logger.info(f"SMTP connection test successful for {self.smtp_server}:{self.smtp_port}")
                return True, "SMTP connection test successful!"
        except Exception as e:
            error_message = str(e)
            logger.error(f"SMTP connection test failed: {error_message}")
            
            # Provide more user-friendly error messages
            if "Authentication" in error_message:
                return False, "Authentication failed. Please check your username and password."
            elif "getaddrinfo failed" in error_message or "Name or service not known" in error_message:
                return False, "Could not connect to SMTP server. Please check the server address."
            elif "Connection refused" in error_message:
                return False, "Connection refused. Please check if the SMTP server is accepting connections on the specified port."
            else:
                return False, f"SMTP connection test failed: {error_message}"
    
    def send_application_notification(self, to_email, application_data):
        """
        Send an email notification about a job application.
        
        Args:
            to_email (str): The recipient's email address
            application_data (dict): Job application details
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email notifications are not enabled. Missing SMTP configuration.")
            return False
        
        try:
            # Prepare template data
            template_data = {
                'position': application_data.get('position', 'Not specified'),
                'company': application_data.get('company', 'Not specified'),
                'location': application_data.get('location', 'Not specified'),
                'platform': application_data.get('platform', 'External'),
                'timestamp': application_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'success': application_data.get('success', False),
                'message': application_data.get('message', ''),
                'job_url': application_data.get('job_url', '#'),
                'current_year': datetime.now().year
            }
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Job Application Submitted: {template_data['position']} at {template_data['company']}"
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Create plain text content
            text_content = f"""
            Job Application Submitted
            
            Position: {template_data['position']}
            Company: {template_data['company']}
            Location: {template_data['location']}
            Platform: {template_data['platform']}
            Time: {template_data['timestamp']}
            Status: {'Successful' if template_data['success'] else 'Requires Attention'}
            
            Job URL: {template_data['job_url']}
            
            {'Application submitted successfully!' if template_data['success'] else 'Application submission requires your attention. Please check the details.'}
            
            {template_data['message']}
            
            This is an automated notification from AI Job Applier.
            """
            
            # Render HTML content from template
            try:
                template = self.jinja_env.get_template('application_notification.html')
                html_content = template.render(**template_data)
            except Exception as template_error:
                logger.error(f"Failed to render email template: {str(template_error)}")
                # Fallback to basic HTML content if template rendering fails
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #4361ee; color: white; padding: 15px 20px; text-align: center; }}
                        .content {{ padding: 20px; border: 1px solid #ddd; }}
                        .success {{ color: #10b981; font-weight: bold; }}
                        .failed {{ color: #ef4444; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Job Application {template_data['success'] and 'Submitted' or 'Update'}</h2>
                        </div>
                        <div class="content">
                            <p>Your job application for <strong>{template_data['position']}</strong> at <strong>{template_data['company']}</strong> 
                            has been {template_data['success'] and '<span class="success">successfully submitted</span>' or '<span class="failed">processed with issues</span>'}.</p>
                            
                            <p><strong>Details:</strong><br>
                            Location: {template_data['location']}<br>
                            Platform: {template_data['platform']}<br>
                            Time: {template_data['timestamp']}<br>
                            Status: {template_data['success'] and '<span class="success">Successful</span>' or '<span class="failed">Requires Attention</span>'}</p>
                            
                            {template_data['message'] and f"<p><strong>Message:</strong> {template_data['message']}</p>" or ""}
                            
                            <p><a href="{template_data['job_url']}" style="color: #4361ee;">View Job Posting</a></p>
                            
                            <p>This is an automated notification from AI Job Applier.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            # Attach parts
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email notification sent to {to_email} for job application at {template_data['company']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False