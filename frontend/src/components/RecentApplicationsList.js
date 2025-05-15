import React from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Divider,
  Button,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import BusinessIcon from '@mui/icons-material/Business';
import ViewListIcon from '@mui/icons-material/ViewList';

const RecentApplicationsList = ({ applications, limit = 5 }) => {
  const navigate = useNavigate();
  
  // Helper to get the appropriate platform icon
  const getPlatformIcon = (platform) => {
    switch ((platform || '').toLowerCase()) {
      case 'linkedin':
        return <LinkedInIcon style={{ color: '#0077B5' }} />;
      case 'indeed':
        return <BusinessIcon style={{ color: '#003A9B' }} />;
      case 'glassdoor':
        return <BusinessIcon style={{ color: '#0CAA41' }} />;
      case 'google':
        return <BusinessIcon style={{ color: '#4285F4' }} />;
      default:
        return <BusinessIcon />;
    }
  };
  
  // Format timestamp to show date and time
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };
  
  // Limit the applications to the specified number
  const displayedApplications = applications.slice(0, limit);

  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Recent Applications</Typography>
        <Chip 
          label={`${applications.length} Total`} 
          size="small" 
          variant="outlined" 
        />
      </Box>
      
      {applications.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
          <Typography variant="body1" color="text.secondary">No applications submitted yet</Typography>
        </Box>
      ) : (
        <>
          <List sx={{ flexGrow: 1 }}>
            {displayedApplications.map((app, index) => (
              <React.Fragment key={index}>
                <ListItem button onClick={() => app.job_id && navigate(`/job/${app.job_id}`)}>
                  <ListItemIcon>
                    {getPlatformIcon(app.platform)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography component="span" variant="body1" sx={{ mr: 1 }}>
                          {app.position || 'Job Position'}
                        </Typography>
                        <Typography component="span" variant="body2" color="text.secondary">
                          at {app.company || 'Company'}
                        </Typography>
                      </Box>
                    } 
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        <Typography component="span" variant="body2">
                          {formatTimestamp(app.timestamp)}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                          {app.success ? (
                            <CheckCircleIcon fontSize="small" color="success" sx={{ mr: 0.5 }} />
                          ) : (
                            <ErrorIcon fontSize="small" color="error" sx={{ mr: 0.5 }} />
                          )}
                          <Typography component="span" variant="body2" color={app.success ? "success.main" : "error.main"}>
                            {app.success ? 'Submitted' : 'Failed'}
                          </Typography>
                        </Box>
                        {app.application_type && (
                          <Chip 
                            label={app.application_type === 'easy_apply' ? 'Easy Apply' : 'External'} 
                            size="small" 
                            variant="outlined"
                            sx={{ ml: 1, height: 20, fontSize: '0.625rem' }}
                          />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < displayedApplications.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
          
          <Box sx={{ mt: 2, textAlign: 'right' }}>
            <Button 
              endIcon={<ViewListIcon />}
              onClick={() => navigate('/history')}
              size="small"
            >
              View All Applications
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default RecentApplicationsList;