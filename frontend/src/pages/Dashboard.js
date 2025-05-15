import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Grid, 
  Paper, 
  Box, 
  Button, 
  Card,
  CardContent,
  CardActions,
  Divider,
  Alert,
  AlertTitle
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import SearchIcon from '@mui/icons-material/Search';
import AssessmentIcon from '@mui/icons-material/Assessment';

// Components
import RecentApplicationsList from '../components/RecentApplicationsList';
import ApplicationTrendsChart from '../components/ApplicationTrendsChart';
import ApplicationAnalytics from '../components/ApplicationAnalytics';

// Services
import { getResumeFromStorage } from '../services/resumeService';
import { getJobsFromStorage } from '../services/jobService';
import { getApplicationHistory } from '../services/applicationService';

const Dashboard = () => {
  const navigate = useNavigate();
  const [resumeData, setResumeData] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);
  const [applications, setApplications] = useState([]);

  useEffect(() => {
    // Load data from local storage
    const savedResume = getResumeFromStorage();
    const savedJobs = getJobsFromStorage() || [];
    const applicationHistory = getApplicationHistory() || [];

    setResumeData(savedResume);
    setRecentJobs(savedJobs.slice(0, 5)); // Show only 5 most recent jobs
    setApplications(applicationHistory); // Get all applications for analytics
  }, []);

  return (
    <Box
      sx={{
        maxWidth: '100%',
        overflow: 'hidden',
        pb: { xs: 8, sm: 4 } // Add bottom padding for mobile navigation
      }}
    >
      <Typography 
        variant="h4" 
        gutterBottom
        sx={{ 
          fontSize: { xs: '1.75rem', sm: '2.125rem' },
          fontWeight: 'bold',
          mb: 3
        }}
      >
        Dashboard
      </Typography>

      {/* Welcome & Status */}
      <Paper 
        sx={{ 
          p: { xs: 2, sm: 3 }, 
          mb: { xs: 3, md: 4 },
          borderRadius: 2,
          boxShadow: (theme) => theme.shadows[2]
        }}
        elevation={1}
      >
        <Typography 
          variant="h5" 
          gutterBottom
          sx={{ 
            fontSize: { xs: '1.25rem', sm: '1.5rem' },
            fontWeight: 'medium',
            color: 'primary.main'
          }}
        >
          Welcome to AI Job Applier
        </Typography>
        <Typography variant="body1" paragraph>
          Automate your job application process with AI. Upload your resume, find relevant jobs, and let AI help you apply.
        </Typography>
        
        {!resumeData ? (
          <Alert 
            severity="info" 
            sx={{ 
              mt: 2,
              borderRadius: 1,
              '& .MuiAlert-icon': {
                alignItems: 'center'
              }
            }}
            variant="outlined"
          >
            <AlertTitle sx={{ fontWeight: 'bold' }}>Get Started</AlertTitle>
            Upload your resume to begin your job search journey.
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => navigate('/resume')}
                startIcon={<DescriptionIcon />}
                sx={{ 
                  fontWeight: 'medium',
                  boxShadow: 2,
                  '&:hover': {
                    boxShadow: 4
                  }
                }}
              >
                Upload Resume
              </Button>
            </Box>
          </Alert>
        ) : (
          <Alert 
            severity="success" 
            sx={{ 
              mt: 2,
              borderRadius: 1,
              '& .MuiAlert-icon': {
                alignItems: 'center'
              }
            }}
            variant="outlined"
          >
            <AlertTitle sx={{ fontWeight: 'bold' }}>Resume Ready</AlertTitle>
            Your resume has been parsed successfully. You're ready to search for jobs!
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => navigate('/search')}
                startIcon={<SearchIcon />}
                sx={{ 
                  fontWeight: 'medium',
                  boxShadow: 2,
                  '&:hover': {
                    boxShadow: 4
                  }
                }}
              >
                Find Jobs
              </Button>
            </Box>
          </Alert>
        )}
      </Paper>

      {/* Main Dashboard Content */}
      {resumeData && (
        <>
          {/* Analytics Overview */}
          {applications.length > 0 && (
            <ApplicationAnalytics applications={applications} />
          )}

          <Grid container spacing={{ xs: 2, md: 3 }}>
            {/* Application Trends */}
            <Grid item xs={12} lg={8}>
              <ApplicationTrendsChart applicationData={applications} />
            </Grid>

            {/* Quick Actions */}
            <Grid item xs={12} lg={4}>
              <Card 
                sx={{ 
                  height: '100%', 
                  borderRadius: 2,
                  boxShadow: (theme) => theme.shadows[3]
                }}
                elevation={3}
              >
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Typography 
                    variant="h6" 
                    gutterBottom
                    color="primary"
                    fontWeight="bold"
                  >
                    Quick Actions
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      flexDirection: { xs: 'row', md: 'column' }, 
                      flexWrap: { xs: 'wrap', md: 'nowrap' },
                      gap: { xs: 1, sm: 2 }
                    }}
                  >
                    <Button 
                      variant="outlined" 
                      fullWidth={false}
                      sx={{ 
                        minWidth: { xs: '100%', sm: 'calc(50% - 8px)', md: '100%' },
                        py: 1.5,
                        justifyContent: 'flex-start',
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                          backgroundColor: 'action.hover'
                        }
                      }}
                      startIcon={<SearchIcon />}
                      onClick={() => navigate('/search')}
                    >
                      Search for Jobs
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth={false}
                      sx={{ 
                        minWidth: { xs: '100%', sm: 'calc(50% - 8px)', md: '100%' },
                        py: 1.5,
                        justifyContent: 'flex-start',
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                          backgroundColor: 'action.hover'
                        }
                      }}
                      startIcon={<DescriptionIcon />}
                      onClick={() => navigate('/resume')}
                    >
                      Update Resume
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth={false}
                      sx={{ 
                        minWidth: { xs: '100%', sm: 'calc(50% - 8px)', md: '100%' },
                        py: 1.5,
                        justifyContent: 'flex-start',
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                          backgroundColor: 'action.hover'
                        }
                      }}
                      startIcon={<AssessmentIcon />}
                      onClick={() => navigate('/history')}
                    >
                      View Application Analytics
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Recent Applications */}
            <Grid item xs={12} md={6}>
              <RecentApplicationsList applications={applications} limit={5} />
            </Grid>

            {/* Recent Job Searches */}
            <Grid item xs={12} md={6}>
              <Paper 
                sx={{ 
                  p: { xs: 2, sm: 3 }, 
                  height: '100%',
                  borderRadius: 2,
                  boxShadow: (theme) => theme.shadows[2]
                }}
                elevation={2}
              >
                <Typography 
                  variant="h6" 
                  gutterBottom
                  color="primary"
                  fontWeight="bold"
                >
                  Recent Job Searches
                </Typography>
                
                {recentJobs.length === 0 ? (
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      flexDirection: 'column',
                      justifyContent: 'center', 
                      alignItems: 'center', 
                      height: 180,
                      backgroundColor: (theme) => theme.palette.background.paper,
                      borderRadius: 2,
                      p: 3,
                      mt: 2
                    }}
                  >
                    <SearchIcon 
                      sx={{ 
                        fontSize: '3rem', 
                        color: 'text.secondary',
                        opacity: 0.5,
                        mb: 2 
                      }} 
                    />
                    <Typography variant="body1" color="text.secondary" fontWeight="medium">
                      No recent job searches.
                    </Typography>
                    <Typography variant="body2" color="text.secondary" align="center">
                      Start searching for jobs to see them here!
                    </Typography>
                  </Box>
                ) : (
                  <Box>
                    {recentJobs.map((job, index) => (
                      <React.Fragment key={index}>
                        <Box sx={{ py: 2 }}>
                          <Box 
                            sx={{ 
                              display: 'flex', 
                              justifyContent: 'space-between',
                              flexWrap: { xs: 'wrap', sm: 'nowrap' }
                            }}
                          >
                            <Typography 
                              variant="subtitle1"
                              fontWeight="medium"
                              sx={{ maxWidth: { sm: '70%' } }}
                            >
                              {job.title || 'Job Position'}
                            </Typography>
                            <Typography 
                              variant="body2" 
                              color="text.secondary"
                              sx={{ 
                                ml: 'auto', 
                                order: { xs: 3, sm: 2 },
                                width: { xs: '100%', sm: 'auto' },
                                mt: { xs: 0.5, sm: 0 }
                              }}
                            >
                              {job.platform || 'Job Board'}
                            </Typography>
                          </Box>
                          <Typography 
                            variant="body2" 
                            color="text.secondary"
                            sx={{ mb: 1.5 }}
                          >
                            {job.company || 'Company'} • {job.location || 'Location'}
                          </Typography>
                          <Box 
                            sx={{ 
                              display: 'flex', 
                              gap: 1, 
                              mt: 1,
                              justifyContent: { xs: 'flex-start', sm: 'flex-start' }
                            }}
                          >
                            <Button 
                              size="small" 
                              variant="outlined"
                              sx={{ 
                                borderRadius: 1,
                                minWidth: '80px'
                              }}
                              onClick={() => navigate(`/job/${job.id}`)}
                            >
                              View
                            </Button>
                            <Button 
                              size="small" 
                              variant="contained"
                              sx={{ 
                                borderRadius: 1,
                                minWidth: '80px',
                                boxShadow: 1
                              }}
                              onClick={() => navigate(`/apply/${job.id}`)}
                            >
                              Apply
                            </Button>
                          </Box>
                        </Box>
                        {index < recentJobs.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                    
                    <Box sx={{ mt: 2, textAlign: 'right' }}>
                      <Button 
                        size="small"
                        endIcon={<SearchIcon />}
                        onClick={() => navigate('/search')}
                      >
                        View All Jobs
                      </Button>
                    </Box>
                  </Box>
                )}
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
};

export default Dashboard;