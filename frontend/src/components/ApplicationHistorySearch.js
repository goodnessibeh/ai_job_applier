import React, { useState } from 'react';
import { 
  Paper, 
  Typography, 
  Box,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import FilterListIcon from '@mui/icons-material/FilterList';
import TuneIcon from '@mui/icons-material/Tune';
import DateRangeIcon from '@mui/icons-material/DateRange';

const ApplicationHistorySearch = ({ onSearch }) => {
  const [searchText, setSearchText] = useState('');
  const [applicationStatus, setApplicationStatus] = useState('all');
  const [applicationType, setApplicationType] = useState('all');
  const [platform, setPlatform] = useState('all');
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  });
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSearch = () => {
    onSearch({
      searchText,
      applicationStatus,
      applicationType,
      platform,
      dateRange
    });
  };

  const handleClear = () => {
    setSearchText('');
    setApplicationStatus('all');
    setApplicationType('all');
    setPlatform('all');
    setDateRange({
      startDate: '',
      endDate: ''
    });
    
    onSearch({
      searchText: '',
      applicationStatus: 'all',
      applicationType: 'all',
      platform: 'all',
      dateRange: {
        startDate: '',
        endDate: ''
      }
    });
  };

  const handleDateChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const toggleAdvanced = () => {
    setShowAdvanced(!showAdvanced);
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Search Applications
        </Typography>
        <Button 
          startIcon={showAdvanced ? <ClearIcon /> : <TuneIcon />}
          onClick={toggleAdvanced}
          size="small"
        >
          {showAdvanced ? 'Simple Search' : 'Advanced Search'}
        </Button>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={showAdvanced ? 12 : 8}>
          <TextField
            fullWidth
            placeholder="Search by job title, company, or keywords"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: searchText && (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={() => setSearchText('')}>
                    <ClearIcon fontSize="small" />
                  </IconButton>
                </InputAdornment>
              )
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
        </Grid>

        {!showAdvanced && (
          <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
            <Button 
              variant="contained" 
              fullWidth
              onClick={handleSearch}
              startIcon={<SearchIcon />}
            >
              Search
            </Button>
          </Grid>
        )}

        {showAdvanced && (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="application-status-label">Status</InputLabel>
                <Select
                  labelId="application-status-label"
                  value={applicationStatus}
                  onChange={(e) => setApplicationStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="success">Successful</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="application-type-label">Type</InputLabel>
                <Select
                  labelId="application-type-label"
                  value={applicationType}
                  onChange={(e) => setApplicationType(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="easy_apply">Easy Apply</MenuItem>
                  <MenuItem value="external">External</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth variant="outlined">
                <InputLabel id="platform-label">Platform</InputLabel>
                <Select
                  labelId="platform-label"
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  label="Platform"
                >
                  <MenuItem value="all">All Platforms</MenuItem>
                  <MenuItem value="linkedin">LinkedIn</MenuItem>
                  <MenuItem value="indeed">Indeed</MenuItem>
                  <MenuItem value="glassdoor">Glassdoor</MenuItem>
                  <MenuItem value="google">Google Jobs</MenuItem>
                  <MenuItem value="external">External Sites</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
                <DateRangeIcon sx={{ mr: 1, color: 'action.active' }} />
                <Box sx={{ flexGrow: 1 }}>
                  <TextField
                    label="From Date"
                    type="date"
                    fullWidth
                    variant="outlined"
                    size="small"
                    value={dateRange.startDate}
                    onChange={(e) => handleDateChange('startDate', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    sx={{ mb: 1 }}
                  />
                  <TextField
                    label="To Date"
                    type="date"
                    fullWidth
                    variant="outlined"
                    size="small"
                    value={dateRange.endDate}
                    onChange={(e) => handleDateChange('endDate', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
              </Box>
            </Grid>
            
            <Grid item xs={12} sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button 
                variant="outlined" 
                onClick={handleClear}
                startIcon={<ClearIcon />}
              >
                Clear Filters
              </Button>
              <Button 
                variant="contained" 
                onClick={handleSearch}
                startIcon={<SearchIcon />}
              >
                Search
              </Button>
            </Grid>
          </>
        )}
      </Grid>
      
      {/* Active filters display */}
      {(searchText || applicationStatus !== 'all' || applicationType !== 'all' || platform !== 'all' || dateRange.startDate || dateRange.endDate) && (
        <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="body2" sx={{ mr: 1, color: 'text.secondary', display: 'flex', alignItems: 'center' }}>
            <FilterListIcon fontSize="small" sx={{ mr: 0.5 }} /> Active Filters:
          </Typography>
          
          {searchText && (
            <Chip 
              label={`Keyword: ${searchText}`} 
              size="small" 
              onDelete={() => setSearchText('')} 
            />
          )}
          
          {applicationStatus !== 'all' && (
            <Chip 
              label={`Status: ${applicationStatus === 'success' ? 'Successful' : 'Failed'}`} 
              size="small" 
              onDelete={() => setApplicationStatus('all')} 
            />
          )}
          
          {applicationType !== 'all' && (
            <Chip 
              label={`Type: ${applicationType === 'easy_apply' ? 'Easy Apply' : 'External'}`} 
              size="small" 
              onDelete={() => setApplicationType('all')} 
            />
          )}
          
          {platform !== 'all' && (
            <Chip 
              label={`Platform: ${platform.charAt(0).toUpperCase() + platform.slice(1)}`} 
              size="small" 
              onDelete={() => setPlatform('all')} 
            />
          )}
          
          {dateRange.startDate && (
            <Chip 
              label={`From: ${dateRange.startDate}`} 
              size="small" 
              onDelete={() => handleDateChange('startDate', '')} 
            />
          )}
          
          {dateRange.endDate && (
            <Chip 
              label={`To: ${dateRange.endDate}`} 
              size="small" 
              onDelete={() => handleDateChange('endDate', '')} 
            />
          )}
        </Box>
      )}
    </Paper>
  );
};

export default ApplicationHistorySearch;