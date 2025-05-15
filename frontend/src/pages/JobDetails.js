import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Paper, 
  Button, 
  Chip, 
  Divider,
  Grid,
  CircularProgress,
  Breadcrumbs,
  Link,
  Stack
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';

import { findJobById, saveJobToFavorites, getFavoriteJobs } from '../services/jobService';

const JobDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    const loadJob = () => {
      try {
        const jobData = findJobById(id);
        if (jobData) {
          setJob(jobData);
          
          // Check if job is in favorites
          const favorites = getFavoriteJobs();
          setIsFavorite(favorites.some(favJob => favJob.id === id));
        } else {
          setError('Job not found. It may have been removed or expired.');
        }
      } catch (err) {
        setError(err.message || 'Error loading job details');
      } finally {
        setLoading(false);
      }
    };
    
    loadJob();
  }, [id]);
  
  const handleFavoriteToggle = () => {
    if (!isFavorite && job) {
      saveJobToFavorites(job);
      setIsFavorite(true);
    }
    // Note: We don't implement removing from favorites in this demo
  };
  
  const handleApply = () => {
    navigate(`/apply/${id}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !job) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          {error || 'Job not found'}
        </Typography>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/search')}
        >
          Back to Search
        </Button>
      </Paper>
    );
  }

  // Format the job description with line breaks
  const formattedDescription = job.description.split('\n').map((line, index) => (
    <React.Fragment key={index}>
      {line}
      <br />
    </React.Fragment>
  ));

  return (
    <Box>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link 
          underline="hover" 
          color="inherit" 
          onClick={() => navigate('/')}
          sx={{ cursor: 'pointer' }}
        >
          Dashboard
        </Link>
        <Link 
          underline="hover" 
          color="inherit" 
          onClick={() => navigate('/search')}
          sx={{ cursor: 'pointer' }}
        >
          Job Search
        </Link>
        <Typography color="text.primary">{job.title}</Typography>
      </Breadcrumbs>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {job.title}
            </Typography>
            <Typography variant="h5" color="text.secondary" gutterBottom>
              {job.company}
            </Typography>
          </Box>
          <Button 
            variant="outlined" 
            startIcon={isFavorite ? <BookmarkIcon /> : <BookmarkBorderIcon />}
            onClick={handleFavoriteToggle}
            color={isFavorite ? 'primary' : 'inherit'}
          >
            {isFavorite ? 'Saved' : 'Save'}
          </Button>
        </Box>

        <Stack direction="row" spacing={2} sx={{ my: 2 }}>
          <Chip 
            icon={<LocationOnIcon />} 
            label={job.location} 
            variant="outlined" 
          />
          <Chip 
            icon={<WorkIcon />} 
            label={job.job_type} 
            variant="outlined" 
          />
          {job.salary && (
            <Chip 
              icon={<AttachMoneyIcon />} 
              label={job.salary} 
              variant="outlined" 
            />
          )}
          <Chip 
            icon={<AccessTimeIcon />} 
            label={job.posted_date} 
            variant="outlined" 
          />
        </Stack>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Chip 
            label={`Source: ${job.source}`} 
            color="primary" 
            variant="outlined" 
          />
          <Button 
            variant="contained" 
            color="primary"
            size="large"
            onClick={handleApply}
          >
            Apply Now
          </Button>
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <Typography variant="h6" gutterBottom>
          Job Description
        </Typography>
        <Typography variant="body1" paragraph component="div">
          {formattedDescription}
        </Typography>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
          <Button 
            startIcon={<ArrowBackIcon />} 
            onClick={() => navigate('/search')}
          >
            Back to Results
          </Button>
          <Button 
            variant="contained" 
            color="primary"
            onClick={handleApply}
          >
            Apply Now
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default JobDetails;
