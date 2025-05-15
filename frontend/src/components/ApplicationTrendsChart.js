import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  ToggleButton, 
  ToggleButtonGroup,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';

const ApplicationTrendsChart = ({ applicationData }) => {
  const [timeframe, setTimeframe] = useState('weekly');
  const [chartData, setChartData] = useState([]);
  const [chartType, setChartType] = useState('platform');
  
  useEffect(() => {
    if (applicationData && applicationData.length > 0) {
      generateChartData();
    } else {
      setChartData([]);
    }
  }, [applicationData, timeframe, chartType]);

  const generateChartData = () => {
    // Group data based on selected timeframe and chart type
    let data = [];
    
    if (chartType === 'platform') {
      data = generatePlatformChartData();
    } else if (chartType === 'status') {
      data = generateStatusChartData();
    } else if (chartType === 'type') {
      data = generateTypeChartData();
    }
    
    setChartData(data);
  };
  
  const generatePlatformChartData = () => {
    // Sample data structure until we connect to a proper chart library
    const platforms = {
      'linkedin': { count: 0, color: '#0077B5' },
      'indeed': { count: 0, color: '#003A9B' },
      'glassdoor': { count: 0, color: '#0CAA41' },
      'google': { count: 0, color: '#4285F4' },
      'external': { count: 0, color: '#FF6B6B' }
    };
    
    // Filter data based on timeframe
    const filteredData = filterDataByTimeframe(applicationData);
    
    // Count applications by platform
    filteredData.forEach(app => {
      const platform = (app.platform || 'external').toLowerCase();
      if (platforms[platform]) {
        platforms[platform].count++;
      } else {
        platforms['external'].count++;
      }
    });
    
    return Object.entries(platforms)
      .filter(([_, data]) => data.count > 0) // Only include platforms with data
      .map(([name, data]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1), // Capitalize platform name
        value: data.count,
        color: data.color
      }));
  };
  
  const generateStatusChartData = () => {
    // Filter data based on timeframe
    const filteredData = filterDataByTimeframe(applicationData);
    
    // Count applications by status (success/failure)
    const success = filteredData.filter(app => app.success).length;
    const failure = filteredData.filter(app => !app.success).length;
    
    return [
      { name: 'Successful', value: success, color: '#4CAF50' },
      { name: 'Failed', value: failure, color: '#F44336' }
    ];
  };
  
  const generateTypeChartData = () => {
    // Filter data based on timeframe
    const filteredData = filterDataByTimeframe(applicationData);
    
    // Count applications by type (easy apply/external)
    const easyApply = filteredData.filter(app => app.application_type === 'easy_apply').length;
    const external = filteredData.filter(app => app.application_type === 'external').length;
    
    return [
      { name: 'Easy Apply', value: easyApply, color: '#2196F3' },
      { name: 'External', value: external, color: '#FF9800' }
    ];
  };
  
  const filterDataByTimeframe = (data) => {
    const now = new Date();
    
    if (timeframe === 'weekly') {
      // Filter to last 7 days
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      return data.filter(item => new Date(item.timestamp) >= weekAgo);
    } else if (timeframe === 'monthly') {
      // Filter to last 30 days
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      return data.filter(item => new Date(item.timestamp) >= monthAgo);
    }
    
    // All time - return all data
    return data;
  };

  const handleTimeframeChange = (event, newTimeframe) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };
  
  const handleChartTypeChange = (event) => {
    setChartType(event.target.value);
  };

  // Enhanced bar chart rendering
  const renderBarChart = () => {
    const maxValue = Math.max(...chartData.map(item => item.value), 1); // Ensure at least 1 for division
    
    return (
      <Box sx={{ 
        display: 'flex', 
        mt: 4, 
        height: { xs: 220, sm: 250, md: 280 }, 
        alignItems: 'flex-end',
        justifyContent: 'center',
        px: { xs: 1, sm: 3 }
      }}>
        {chartData.map((item, index) => (
          <Box 
            key={index} 
            sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mx: { xs: 0.5, sm: 1, md: 2 },
              flexGrow: 1,
              maxWidth: { xs: '60px', sm: '80px', md: '100px' }
            }}
          >
            <Box 
              sx={{ 
                width: '100%',
                backgroundColor: item.color,
                height: `${maxValue > 0 ? (item.value / maxValue) * 200 : 0}px`,
                minHeight: item.value > 0 ? 20 : 0,
                borderRadius: '4px 4px 0 0',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'flex-start',
                color: 'white',
                fontWeight: 'bold',
                pt: 1,
                position: 'relative',
                transition: 'height 0.5s ease-in-out',
                boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                '&:hover': {
                  opacity: 0.9,
                  transform: 'translateY(-5px)',
                  boxShadow: '0 5px 10px rgba(0,0,0,0.15)'
                }
              }}
            >
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 'bold',
                  fontSize: { xs: '0.75rem', sm: '0.875rem' }
                }}
              >
                {item.value}
              </Typography>
            </Box>
            <Box 
              sx={{ 
                mt: 1,
                p: 1,
                width: '100%',
                textAlign: 'center',
                backgroundColor: (theme) => theme.palette.background.paper,
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider'
              }}
            >
              <Typography 
                variant="body2" 
                sx={{ 
                  fontSize: { xs: '0.7rem', sm: '0.75rem', md: '0.85rem' }, 
                  fontWeight: 'medium'
                }}
              >
                {item.name}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
    );
  };

  // Empty state illustration
  const renderEmptyState = () => (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 250,
        backgroundColor: (theme) => theme.palette.background.paper,
        borderRadius: 2,
        p: 3,
        mt: 2
      }}
    >
      <Box 
        sx={{ 
          width: '100px', 
          height: '80px', 
          display: 'flex',
          mb: 2,
          opacity: 0.7
        }}
      >
        {/* Simple bar chart illustration */}
        <Box sx={{ width: '20px', height: '60%', backgroundColor: 'primary.light', mx: 0.5, borderRadius: 1 }} />
        <Box sx={{ width: '20px', height: '80%', backgroundColor: 'success.light', mx: 0.5, borderRadius: 1 }} />
        <Box sx={{ width: '20px', height: '40%', backgroundColor: 'warning.light', mx: 0.5, borderRadius: 1 }} />
        <Box sx={{ width: '20px', height: '70%', backgroundColor: 'info.light', mx: 0.5, borderRadius: 1 }} />
      </Box>
      <Typography variant="body1" color="text.secondary" fontWeight="medium">
        No application data available
      </Typography>
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1, maxWidth: '80%' }}>
        Start applying to jobs to see your application trends
      </Typography>
    </Box>
  );

  return (
    <Paper 
      sx={{ 
        p: { xs: 2, sm: 3 }, 
        height: '100%',
        borderRadius: 2,
        boxShadow: (theme) => theme.shadows[2]
      }}
      elevation={3}
    >
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        justifyContent: 'space-between', 
        alignItems: { xs: 'flex-start', sm: 'center' }, 
        gap: { xs: 2, sm: 0 },
        mb: 2 
      }}>
        <Typography 
          variant="h6" 
          fontWeight="bold" 
          color="primary"
          sx={{ mb: { xs: 1, sm: 0 } }}
        >
          Application Trends
        </Typography>
        
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', md: 'row' },
          alignItems: { xs: 'flex-start', md: 'center' },
          gap: 2
        }}>
          <FormControl 
            variant="outlined" 
            size="small" 
            sx={{ 
              minWidth: 120,
              width: { xs: '100%', md: 'auto' } 
            }}
          >
            <InputLabel id="chart-type-label">View By</InputLabel>
            <Select
              labelId="chart-type-label"
              value={chartType}
              onChange={handleChartTypeChange}
              label="View By"
            >
              <MenuItem value="platform">Platform</MenuItem>
              <MenuItem value="status">Success Rate</MenuItem>
              <MenuItem value="type">Application Type</MenuItem>
            </Select>
          </FormControl>
          
          <ToggleButtonGroup
            value={timeframe}
            exclusive
            onChange={handleTimeframeChange}
            size="small"
            aria-label="timeframe selection"
            sx={{ 
              '& .MuiToggleButton-root': {
                px: { xs: 1, sm: 2 },
                py: 0.75
              }
            }}
          >
            <ToggleButton value="weekly">Weekly</ToggleButton>
            <ToggleButton value="monthly">Monthly</ToggleButton>
            <ToggleButton value="all">All Time</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {applicationData.length === 0 ? renderEmptyState() : renderBarChart()}
    </Paper>
  );
};

export default ApplicationTrendsChart;