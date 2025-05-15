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
    
    // Count applications by platform
    applicationData.forEach(app => {
      const platform = (app.platform || 'external').toLowerCase();
      if (platforms[platform]) {
        platforms[platform].count++;
      } else {
        platforms['external'].count++;
      }
    });
    
    return Object.entries(platforms).map(([name, data]) => ({
      name,
      value: data.count,
      color: data.color
    }));
  };
  
  const generateStatusChartData = () => {
    // Count applications by status (success/failure)
    const success = applicationData.filter(app => app.success).length;
    const failure = applicationData.filter(app => !app.success).length;
    
    return [
      { name: 'Successful', value: success, color: '#4CAF50' },
      { name: 'Failed', value: failure, color: '#F44336' }
    ];
  };
  
  const generateTypeChartData = () => {
    // Count applications by type (easy apply/external)
    const easyApply = applicationData.filter(app => app.application_type === 'easy_apply').length;
    const external = applicationData.filter(app => app.application_type === 'external').length;
    
    return [
      { name: 'Easy Apply', value: easyApply, color: '#2196F3' },
      { name: 'External', value: external, color: '#FF9800' }
    ];
  };

  const handleTimeframeChange = (event, newTimeframe) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };
  
  const handleChartTypeChange = (event) => {
    setChartType(event.target.value);
  };

  // Basic bar chart rendering
  // In a real implementation, we would use a library like Chart.js, Recharts, or Victory
  const renderBarChart = () => {
    const maxValue = Math.max(...chartData.map(item => item.value));
    
    return (
      <Box sx={{ display: 'flex', mt: 3, height: 250, alignItems: 'flex-end' }}>
        {chartData.map((item, index) => (
          <Box 
            key={index} 
            sx={{ 
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mx: 1,
              flexGrow: 1
            }}
          >
            <Box 
              sx={{ 
                width: '100%', 
                maxWidth: 60,
                backgroundColor: item.color,
                height: `${maxValue > 0 ? (item.value / maxValue) * 200 : 0}px`,
                minHeight: item.value > 0 ? 20 : 0,
                borderRadius: 1,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'flex-start',
                color: 'white',
                fontWeight: 'bold',
                pt: 0.5
              }}
            >
              {item.value}
            </Box>
            <Typography variant="body2" sx={{ mt: 1, fontSize: '0.75rem', textAlign: 'center' }}>
              {item.name}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Application Trends</Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 150, mr: 2 }}>
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
          >
            <ToggleButton value="weekly">Weekly</ToggleButton>
            <ToggleButton value="monthly">Monthly</ToggleButton>
            <ToggleButton value="all">All Time</ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>
      
      {applicationData.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
          <Typography variant="body1" color="text.secondary">No application data available</Typography>
        </Box>
      ) : (
        renderBarChart()
      )}
    </Paper>
  );
};

export default ApplicationTrendsChart;