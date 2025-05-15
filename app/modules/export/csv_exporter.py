import csv
import io
import logging
import tempfile
import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CSVExporter:
    def __init__(self):
        pass
    
    def export_applications_to_csv(self, applications: List[Dict[str, Any]]) -> Optional[str]:
        """
        Export applications to a CSV file.
        
        Args:
            applications: List of application data dictionaries
            
        Returns:
            str: Path to the generated CSV file or None if export failed
        """
        if not applications:
            logger.warning("No applications to export")
            return None
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv') as temp_file:
                # Define CSV headers
                headers = [
                    'Job Title',
                    'Company',
                    'Location',
                    'Platform',
                    'Application Type',
                    'Status',
                    'Date',
                    'Job URL',
                    'Notes'
                ]
                
                # Create CSV writer
                writer = csv.DictWriter(temp_file, fieldnames=headers)
                writer.writeheader()
                
                # Write application data
                for app in applications:
                    timestamp = app.get('timestamp')
                    if isinstance(timestamp, str):
                        try:
                            timestamp = datetime.datetime.fromisoformat(timestamp)
                        except ValueError:
                            timestamp = datetime.datetime.now()
                    elif not isinstance(timestamp, datetime.datetime):
                        timestamp = datetime.datetime.now()
                        
                    formatted_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    
                    writer.writerow({
                        'Job Title': app.get('position', ''),
                        'Company': app.get('company', ''),
                        'Location': app.get('location', ''),
                        'Platform': app.get('platform', 'External'),
                        'Application Type': app.get('application_type', 'Unknown'),
                        'Status': 'Successful' if app.get('success', False) else 'Failed',
                        'Date': formatted_date,
                        'Job URL': app.get('job_url', ''),
                        'Notes': app.get('message', '') or app.get('error', '')
                    })
                
                return temp_file.name
        
        except Exception as e:
            logger.error(f"Failed to export applications to CSV: {str(e)}")
            return None
    
    def generate_applications_csv_string(self, applications: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a CSV string from applications data.
        
        Args:
            applications: List of application data dictionaries
            
        Returns:
            str: CSV string representation of the applications or None if failed
        """
        if not applications:
            logger.warning("No applications to export")
            return None
        
        try:
            # Create a string buffer
            output = io.StringIO()
            
            # Define CSV headers
            headers = [
                'Job Title',
                'Company',
                'Location',
                'Platform',
                'Application Type',
                'Status',
                'Date',
                'Job URL',
                'Notes'
            ]
            
            # Create CSV writer
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            
            # Write application data
            for app in applications:
                timestamp = app.get('timestamp')
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.datetime.fromisoformat(timestamp)
                    except ValueError:
                        timestamp = datetime.datetime.now()
                elif not isinstance(timestamp, datetime.datetime):
                    timestamp = datetime.datetime.now()
                    
                formatted_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                writer.writerow({
                    'Job Title': app.get('position', ''),
                    'Company': app.get('company', ''),
                    'Location': app.get('location', ''),
                    'Platform': app.get('platform', 'External'),
                    'Application Type': app.get('application_type', 'Unknown'),
                    'Status': 'Successful' if app.get('success', False) else 'Failed',
                    'Date': formatted_date,
                    'Job URL': app.get('job_url', ''),
                    'Notes': app.get('message', '') or app.get('error', '')
                })
            
            # Get the CSV string
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to generate CSV string: {str(e)}")
            return None