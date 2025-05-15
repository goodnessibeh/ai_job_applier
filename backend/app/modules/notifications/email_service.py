import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, smtp_server, smtp_port, username, password, from_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.enabled = all([smtp_server, smtp_port, username, password, from_email])
    
    def is_enabled(self):
        return self.enabled
    
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
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Job Application Submitted: {application_data['position']} at {application_data['company']}"
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Create plain text content
            text_content = f"""
            Job Application Submitted
            
            Position: {application_data['position']}
            Company: {application_data['company']}
            Location: {application_data.get('location', 'Not specified')}
            Platform: {application_data.get('platform', 'External')}
            Time: {application_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
            Status: {'Successful' if application_data.get('success', False) else 'Failed'}
            
            Job URL: {application_data.get('job_url', 'Not available')}
            
            {'Application submitted successfully!' if application_data.get('success', False) else 'Application submission failed. Please check the details.'}
            
            {application_data.get('message', '')}
            
            This is an automated notification from AI Job Applier.
            """
            
            # Create HTML content for better formatting
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4285F4; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }}
                    .content {{ padding: 20px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; }}
                    .success {{ color: #4CAF50; font-weight: bold; }}
                    .failed {{ color: #F44336; font-weight: bold; }}
                    .details {{ margin: 20px 0; }}
                    .details table {{ width: 100%; border-collapse: collapse; }}
                    .details td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                    .details td:first-child {{ font-weight: bold; width: 30%; }}
                    .button {{ display: inline-block; background-color: #4285F4; color: white; padding: 10px 20px; 
                              text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Job Application Submitted</h2>
                    </div>
                    <div class="content">
                        <p>Your job application has been {'<span class="success">successfully submitted</span>' if application_data.get('success', False) else '<span class="failed">failed</span>'}.</p>
                        
                        <div class="details">
                            <table>
                                <tr>
                                    <td>Position:</td>
                                    <td>{application_data['position']}</td>
                                </tr>
                                <tr>
                                    <td>Company:</td>
                                    <td>{application_data['company']}</td>
                                </tr>
                                <tr>
                                    <td>Location:</td>
                                    <td>{application_data.get('location', 'Not specified')}</td>
                                </tr>
                                <tr>
                                    <td>Platform:</td>
                                    <td>{application_data.get('platform', 'External')}</td>
                                </tr>
                                <tr>
                                    <td>Application Time:</td>
                                    <td>{application_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</td>
                                </tr>
                                <tr>
                                    <td>Status:</td>
                                    <td>{'<span class="success">Successful</span>' if application_data.get('success', False) else '<span class="failed">Failed</span>'}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <p>{application_data.get('message', '')}</p>
                        
                        <a href="{application_data.get('job_url', '#')}" class="button">View Job Posting</a>
                        
                        <div class="footer">
                            <p>This is an automated notification from AI Job Applier.</p>
                        </div>
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
            
            logger.info(f"Email notification sent to {to_email} for job application at {application_data['company']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False