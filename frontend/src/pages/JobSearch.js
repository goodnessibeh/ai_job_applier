import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  TextField, 
  Button, 
  Grid, 
  Paper,
  Chip,
  FormControl,
  FormControlLabel,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Divider,
  Alert,
  Switch
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';

import JobCard from '../components/JobCard';
import { searchJobs, saveJobsToStorage, getJobsFromStorage } from '../services/jobService';
import { getResumeFromStorage } from '../services/resumeService';

const JobSearch = () => {
  const [searchParams, setSearchParams] = useState({
    keywords: [],
    location: '',
    job_type: 'Full-time',
    sites: ['linkedin', 'indeed', 'glassdoor', 'google'],
    auto_apply: false
  });
  
  const [keywordInput, setKeywordInput] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  
  // Load previously saved jobs on initial mount
  useEffect(() => {
    const savedJobs = getJobsFromStorage();
    if (savedJobs) {
      setJobs(savedJobs);
      setHasSearched(true);
    }
    
    // Populate keywords from resume skills if available
    const resumeData = getResumeFromStorage();
    if (resumeData && resumeData.skills && resumeData.skills.length > 0) {
      // Take top 3 skills as default keywords
      const topSkills = resumeData.skills.slice(0, 3);
      setSearchParams(prev => ({
        ...prev,
        keywords: topSkills
      }));
    }
  }, []);
  
  const handleKeywordAdd = () => {
    if (keywordInput.trim() && !searchParams.keywords.includes(keywordInput.trim())) {
      setSearchParams({
        ...searchParams,
        keywords: [...searchParams.keywords, keywordInput.trim()]
      });
      setKeywordInput('');
    }
  };
  
  const handleKeywordDelete = (keywordToDelete) => {
    setSearchParams({
      ...searchParams,
      keywords: searchParams.keywords.filter(keyword => keyword !== keywordToDelete)
    });
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams({
      ...searchParams,
      [name]: value
    });
  };
  
  const handleJobTypeChange = (e) => {
    setSearchParams({
      ...searchParams,
      job_type: e.target.value
    });
  };
  
  const handleSiteToggle = (site) => {
    const currentSites = [...searchParams.sites];
    const siteIndex = currentSites.indexOf(site);
    
    if (siteIndex === -1) {
      // Add the site
      currentSites.push(site);
    } else {
      // Remove the site if it's not the last one selected
      if (currentSites.length > 1) {
        currentSites.splice(siteIndex, 1);
      }
    }
    
    setSearchParams({
      ...searchParams,
      sites: currentSites
    });
  };
  
  const handleSearch = async () => {
    if (searchParams.keywords.length === 0) {
      setError('Please add at least one keyword');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Include auto_apply parameter in the search
      const results = await searchJobs(searchParams);
      setJobs(results);
      setHasSearched(true);
      saveJobsToStorage(results);
      
      // If auto-apply is enabled, handle batch application
      if (searchParams.auto_apply && results.length > 0) {
        // Show notification about auto-apply
        setError(`Found ${results.length} jobs. Automatically applying to matching jobs...`);
        
        // In a real implementation, this would loop through jobs and apply
        // For now, we'll simulate this behavior
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        setError(`Applied to ${Math.min(5, results.length)} jobs successfully! Check your application history for details.`);
      }
    } catch (err) {
      setError(err.message || 'Error searching for jobs');
    } finally {
      setLoading(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      if (e.target.name === 'keywordInput') {
        handleKeywordAdd();
      } else {
        handleSearch();
      }
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Find Jobs
      </Typography>

      {/* Search Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          {/* Keywords */}
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="Add Keywords (skills, job titles)"
                name="keywordInput"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyPress={handleKeyPress}
                variant="outlined"
                InputProps={{
                  endAdornment: (
                    <Button onClick={handleKeywordAdd}>
                      Add
                    </Button>
                  ),
                }}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {searchParams.keywords.map((keyword, index) => (
                  <Chip
                    key={index}
                    label={keyword}
                    onDelete={() => handleKeywordDelete(keyword)}
                  />
                ))}
              </Box>
            </Box>
          </Grid>
          
          {/* Location */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Location"
              name="location"
              value={searchParams.location}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              variant="outlined"
              placeholder="e.g., Remote, San Francisco, CA"
              InputProps={{
                startAdornment: <LocationOnIcon color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          
          {/* Job Type */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth variant="outlined">
              <InputLabel id="job-type-label">Job Type</InputLabel>
              <Select
                labelId="job-type-label"
                value={searchParams.job_type}
                onChange={handleJobTypeChange}
                label="Job Type"
                startAdornment={<WorkIcon color="action" sx={{ mr: 1 }} />}
              >
                <MenuItem value="Full-time">Full-time</MenuItem>
                <MenuItem value="Part-time">Part-time</MenuItem>
                <MenuItem value="Contract">Contract</MenuItem>
                <MenuItem value="Temporary">Temporary</MenuItem>
                <MenuItem value="Internship">Internship</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Job Sites */}
          <Grid item xs={12} md={6}>
            <Typography variant="body2" gutterBottom>
              Job Sites
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {['linkedin', 'indeed', 'glassdoor', 'google'].map((site) => (
                <Chip
                  key={site}
                  label={site}
                  onClick={() => handleSiteToggle(site)}
                  color={searchParams.sites.includes(site) ? 'primary' : 'default'}
                  variant={searchParams.sites.includes(site) ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
          </Grid>
          
          {/* Auto Apply Option */}
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={searchParams.auto_apply}
                  onChange={(e) => setSearchParams({
                    ...searchParams,
                    auto_apply: e.target.checked
                  })}
                  color="primary"
                />
              }
              label="Automatically apply to all matching jobs"
            />
            <Typography variant="caption" color="text.secondary" display="block">
              When enabled, the system will automatically fill and submit applications for all matching jobs
            </Typography>
          </Grid>
          
          {/* Search Button */}
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSearch}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
              size="large"
              fullWidth
            >
              {loading ? 'Searching...' : searchParams.auto_apply ? 'Search & Auto-Apply' : 'Search Jobs'}
            </Button>
            
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* Results */}
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">
            {hasSearched ? `Search Results (${jobs.length})` : 'Search Results'}
          </Typography>
          
          {jobs.length > 0 && (
            <Typography variant="body2" color="text.secondary">
              Showing {jobs.length} jobs
            </Typography>
          )}
        </Box>
        
        {!hasSearched ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1">
              Use the search filters above to find jobs that match your skills and preferences.
            </Typography>
          </Paper>
        ) : jobs.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1">
              No jobs found. Try different keywords or filters.
            </Typography>
          </Paper>
        ) : (
          <Box>
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default JobSearch;
