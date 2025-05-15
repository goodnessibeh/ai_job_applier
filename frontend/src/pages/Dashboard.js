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
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Welcome & Status */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Welcome to AI Job Applier
        </Typography>
        <Typography variant="body1" paragraph>
          Automate your job application process with AI. Upload your resume, find relevant jobs, and let AI help you apply.
        </Typography>
        
        {!resumeData ? (
          <Alert severity="info" sx={{ mt: 2 }}>
            <AlertTitle>Get Started</AlertTitle>
            Upload your resume to begin your job search journey.
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => navigate('/resume')}
                startIcon={<DescriptionIcon />}
              >
                Upload Resume
              </Button>
            </Box>
          </Alert>
        ) : (
          <Alert severity="success" sx={{ mt: 2 }}>
            <AlertTitle>Resume Ready</AlertTitle>
            Your resume has been parsed successfully. You're ready to search for jobs!
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => navigate('/search')}
                startIcon={<SearchIcon />}
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
            <Box sx={{ mb: 3 }}>
              <ApplicationAnalytics applications={applications} />
            </Box>
          )}

          <Grid container spacing={3}>
            {/* Application Trends */}
            <Grid item xs={12} lg={8}>
              <ApplicationTrendsChart applicationData={applications} />
            </Grid>

            {/* Quick Actions */}
            <Grid item xs={12} lg={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<SearchIcon />}
                      onClick={() => navigate('/search')}
                    >
                      Search for Jobs
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<DescriptionIcon />}
                      onClick={() => navigate('/resume')}
                    >
                      Update Resume
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth
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
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Recent Job Searches
                </Typography>
                
                {recentJobs.length === 0 ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 150 }}>
                    <Typography variant="body1" color="text.secondary">
                      No recent job searches. Start searching for jobs!
                    </Typography>
                  </Box>
                ) : (
                  <Box>
                    {recentJobs.map((job, index) => (
                      <React.Fragment key={index}>
                        <Box sx={{ py: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="subtitle1">
                              {job.title || 'Job Position'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {job.platform || 'Job Board'}
                            </Typography>
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {job.company || 'Company'} • {job.location || 'Location'}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Button 
                              size="small" 
                              variant="outlined"
                              onClick={() => navigate(`/job/${job.id}`)}
                            >
                              View
                            </Button>
                            <Button 
                              size="small" 
                              variant="contained"
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