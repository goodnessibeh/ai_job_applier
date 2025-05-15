import React, { useMemo } from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  Grid,
  Divider 
} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import RemoveIcon from '@mui/icons-material/Remove';

const AnalyticCard = ({ title, value, icon, trend, trendValue, color }) => {
  const getTrendIcon = () => {
    if (trend === 'up') return <ArrowUpwardIcon fontSize="small" sx={{ color: 'success.main' }} />;
    if (trend === 'down') return <ArrowDownwardIcon fontSize="small" sx={{ color: 'error.main' }} />;
    return <RemoveIcon fontSize="small" sx={{ color: 'text.secondary' }} />;
  };

  return (
    <Paper 
      sx={{ 
        p: { xs: 2, sm: 3 }, 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          boxShadow: (theme) => theme.shadows[4],
          transform: 'translateY(-4px)'
        }
      }}
      elevation={2}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box sx={{ 
          mr: 2, 
          backgroundColor: `${color}.light`, 
          borderRadius: '50%', 
          p: 1.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {icon}
        </Box>
        <Typography variant="body1" color="text.secondary" fontWeight="medium">
          {title}
        </Typography>
      </Box>
      <Typography 
        variant="h4" 
        sx={{ 
          fontWeight: 'bold', 
          mb: 2,
          mt: 1,
          fontSize: { xs: '1.75rem', sm: '2rem', md: '2.25rem' } 
        }}
      >
        {value}
      </Typography>
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center',
          mt: 'auto',
          pt: 1, 
          borderTop: '1px solid',
          borderColor: 'divider' 
        }}
      >
        {getTrendIcon()}
        <Typography 
          variant="body2" 
          color={
            trend === 'up' ? 'success.main' : 
            trend === 'down' ? 'error.main' : 
            'text.secondary'
          }
          fontWeight="medium"
        >
          {trendValue} 
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
          vs last week
        </Typography>
      </Box>
    </Paper>
  );
};

const ApplicationAnalytics = ({ applications }) => {
  // Calculate analytics metrics
  const analytics = useMemo(() => {
    // Prepare data
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
    
    // Filter applications from this week and last week
    const thisWeekApps = applications.filter(app => new Date(app.timestamp) >= oneWeekAgo);
    const lastWeekApps = applications.filter(app => {
      const date = new Date(app.timestamp);
      return date >= twoWeeksAgo && date < oneWeekAgo;
    });
    
    // Total applications
    const totalApps = applications.length;
    const thisWeekTotal = thisWeekApps.length;
    const lastWeekTotal = lastWeekApps.length;
    const totalTrend = thisWeekTotal > lastWeekTotal ? 'up' : thisWeekTotal < lastWeekTotal ? 'down' : 'neutral';
    const totalTrendValue = `${Math.abs(thisWeekTotal - lastWeekTotal)} applications`;
    
    // Success rate
    const successfulApps = applications.filter(app => app.success).length;
    const successRate = totalApps > 0 ? Math.round((successfulApps / totalApps) * 100) : 0;
    const thisWeekSuccessRate = thisWeekApps.length > 0 
      ? Math.round((thisWeekApps.filter(app => app.success).length / thisWeekApps.length) * 100) 
      : 0;
    const lastWeekSuccessRate = lastWeekApps.length > 0 
      ? Math.round((lastWeekApps.filter(app => app.success).length / lastWeekApps.length) * 100) 
      : 0;
    const successTrend = thisWeekSuccessRate > lastWeekSuccessRate ? 'up' : thisWeekSuccessRate < lastWeekSuccessRate ? 'down' : 'neutral';
    const successTrendValue = `${Math.abs(thisWeekSuccessRate - lastWeekSuccessRate)}%`;
    
    // Average applications per day
    const days = totalApps > 0 
      ? Math.ceil((now - new Date(applications[applications.length - 1].timestamp)) / (24 * 60 * 60 * 1000)) + 1 
      : 1;
    const avgPerDay = Math.round((totalApps / days) * 10) / 10;
    const thisWeekAvg = thisWeekApps.length > 0 ? thisWeekApps.length / 7 : 0;
    const lastWeekAvg = lastWeekApps.length > 0 ? lastWeekApps.length / 7 : 0;
    const avgTrend = thisWeekAvg > lastWeekAvg ? 'up' : thisWeekAvg < lastWeekAvg ? 'down' : 'neutral';
    const avgTrendValue = `${Math.abs(Math.round((thisWeekAvg - lastWeekAvg) * 10) / 10)} per day`;
    
    // Most active platform
    const platforms = {};
    applications.forEach(app => {
      const platform = (app.platform || 'external').toLowerCase();
      platforms[platform] = (platforms[platform] || 0) + 1;
    });
    
    let mostActivePlatform = 'None';
    let maxCount = 0;
    Object.entries(platforms).forEach(([platform, count]) => {
      if (count > maxCount) {
        mostActivePlatform = platform.charAt(0).toUpperCase() + platform.slice(1);
        maxCount = count;
      }
    });
    
    return {
      totalApps,
      totalTrend,
      totalTrendValue,
      successRate,
      successTrend,
      successTrendValue,
      avgPerDay,
      avgTrend,
      avgTrendValue,
      mostActivePlatform
    };
  }, [applications]);

  return (
    <Box sx={{ mb: { xs: 2, md: 4 } }}>
      <Paper
        sx={{
          p: { xs: 2, sm: 3 },
          mb: 2,
          borderRadius: 2,
          backgroundColor: (theme) => theme.palette.background.default
        }}
        elevation={0}
      >
        <Typography variant="h6" gutterBottom fontWeight="medium" color="primary">
          Application Statistics
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <AnalyticCard 
              title="Total Applications" 
              value={analytics.totalApps} 
              icon={<BusinessIcon sx={{ color: 'primary.main' }} />}
              trend={analytics.totalTrend}
              trendValue={analytics.totalTrendValue}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <AnalyticCard 
              title="Success Rate" 
              value={`${analytics.successRate}%`} 
              icon={<CheckCircleIcon sx={{ color: 'success.main' }} />}
              trend={analytics.successTrend}
              trendValue={analytics.successTrendValue}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <AnalyticCard 
              title="Avg. Applications / Day" 
              value={analytics.avgPerDay} 
              icon={<AccessTimeIcon sx={{ color: 'info.main' }} />}
              trend={analytics.avgTrend}
              trendValue={analytics.avgTrendValue}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <AnalyticCard 
              title="Most Active Platform" 
              value={analytics.mostActivePlatform} 
              icon={<BusinessIcon sx={{ color: 'warning.main' }} />}
              trend="neutral"
              trendValue="No change"
              color="warning"
            />
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ApplicationAnalytics;