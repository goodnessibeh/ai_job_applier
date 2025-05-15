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
    <Paper 
      sx={{ 
        p: { xs: 2, sm: 3 },
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        borderRadius: 2,
        boxShadow: (theme) => theme.shadows[2]
      }}
      elevation={2}
    >
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 2
        }}
      >
        <Typography 
          variant="h6" 
          fontWeight="bold"
          color="primary"
        >
          Recent Applications
        </Typography>
        <Chip 
          label={`${applications.length} Total`} 
          size="small" 
          variant="outlined" 
          color="primary"
          sx={{ 
            fontWeight: 'medium',
            borderWidth: 1.5
          }}
        />
      </Box>
      
      {applications.length === 0 ? (
        <Box 
          sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'center', 
            alignItems: 'center', 
            flexGrow: 1,
            backgroundColor: (theme) => theme.palette.background.paper,
            borderRadius: 2,
            p: 3,
            my: 2
          }}
        >
          <ViewListIcon 
            sx={{ 
              fontSize: '3rem', 
              color: 'text.secondary',
              opacity: 0.5,
              mb: 2 
            }} 
          />
          <Typography variant="body1" color="text.secondary" fontWeight="medium">
            No applications submitted yet
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
            Start applying to jobs to see your application history here
          </Typography>
        </Box>
      ) : (
        <>
          <List 
            sx={{ 
              flexGrow: 1,
              '& .MuiListItem-root': {
                borderRadius: 1,
                mb: 0.5,
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }
            }}
          >
            {displayedApplications.map((app, index) => (
              <React.Fragment key={index}>
                <ListItem 
                  button 
                  onClick={() => app.job_id && navigate(`/job/${app.job_id}`)}
                  sx={{ 
                    py: 1.5,
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateX(4px)'
                    }
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: { xs: 40, sm: 44 }
                    }}
                  >
                    <Box
                      sx={{
                        width: 36,
                        height: 36,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: (theme) => theme.palette.action.hover
                      }}
                    >
                      {getPlatformIcon(app.platform)}
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          alignItems: { xs: 'flex-start', sm: 'center' },
                          flexDirection: { xs: 'column', sm: 'row' },
                          gap: { xs: 0.5, sm: 0 }
                        }}
                      >
                        <Typography 
                          component="span" 
                          variant="body1" 
                          sx={{ 
                            mr: 1,
                            fontWeight: 'medium'
                          }}
                        >
                          {app.position || 'Job Position'}
                        </Typography>
                        <Typography 
                          component="span" 
                          variant="body2" 
                          color="text.secondary"
                        >
                          at {app.company || 'Company'}
                        </Typography>
                      </Box>
                    } 
                    secondary={
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          alignItems: { xs: 'flex-start', sm: 'center' },
                          flexDirection: { xs: 'column', sm: 'row' },
                          gap: { xs: 0.75, sm: 1.5 },
                          mt: 0.5,
                          flexWrap: 'wrap'
                        }}
                      >
                        <Typography 
                          component="span" 
                          variant="body2"
                          sx={{
                            fontSize: { xs: '0.7rem', sm: '0.75rem' }
                          }}
                        >
                          {formatTimestamp(app.timestamp)}
                        </Typography>
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center'
                          }}
                        >
                          {app.success ? (
                            <CheckCircleIcon fontSize="small" color="success" sx={{ mr: 0.5 }} />
                          ) : (
                            <ErrorIcon fontSize="small" color="error" sx={{ mr: 0.5 }} />
                          )}
                          <Typography 
                            component="span" 
                            variant="body2" 
                            color={app.success ? "success.main" : "error.main"}
                            fontWeight="medium"
                            sx={{
                              fontSize: { xs: '0.7rem', sm: '0.75rem' }
                            }}
                          >
                            {app.success ? 'Submitted' : 'Failed'}
                          </Typography>
                        </Box>
                        {app.application_type && (
                          <Chip 
                            label={app.application_type === 'easy_apply' ? 'Easy Apply' : 'External'} 
                            size="small" 
                            color={app.application_type === 'easy_apply' ? "info" : "warning"}
                            sx={{ 
                              height: 20, 
                              fontSize: { xs: '0.6rem', sm: '0.625rem' },
                              fontWeight: 'medium'
                            }}
                          />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < displayedApplications.length - 1 && <Divider sx={{ opacity: 0.6 }} />}
              </React.Fragment>
            ))}
          </List>
          
          <Box sx={{ mt: 2, textAlign: 'right' }}>
            <Button 
              endIcon={<ViewListIcon />}
              onClick={() => navigate('/history')}
              size="small"
              color="primary"
              sx={{ fontWeight: 'medium' }}
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