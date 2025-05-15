import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Paper, 
  Button, 
  Divider,
  Alert,
  AlertTitle,
  Grid,
  Tab,
  Tabs
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DeleteIcon from '@mui/icons-material/Delete';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import BarChartIcon from '@mui/icons-material/BarChart';
import ListIcon from '@mui/icons-material/List';

import ApplicationHistoryCard from '../components/ApplicationHistoryCard';
import ApplicationHistorySearch from '../components/ApplicationHistorySearch';
import ApplicationTrendsChart from '../components/ApplicationTrendsChart';
import ApplicationAnalytics from '../components/ApplicationAnalytics';
import { 
  getApplicationHistory, 
  clearApplicationHistory, 
  searchApplicationHistory, 
  exportApplicationHistory 
} from '../services/applicationService';

const ApplicationHistory = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [filteredApplications, setFilteredApplications] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  
  useEffect(() => {
    loadApplications();
  }, []);
  
  const loadApplications = () => {
    const history = getApplicationHistory();
    setApplications(history);
    setFilteredApplications(history);
  };
  
  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear your application history? This cannot be undone.')) {
      clearApplicationHistory();
      setApplications([]);
      setFilteredApplications([]);
    }
  };
  
  const handleSearch = (filters) => {
    const results = searchApplicationHistory(filters);
    setFilteredApplications(results);
  };
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const handleExportHistory = () => {
    const csvBlob = exportApplicationHistory();
    if (csvBlob) {
      const url = URL.createObjectURL(csvBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `application_history_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Application History
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Paper sx={{ p: 0 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            textColor="primary"
            indicatorColor="primary"
          >
            <Tab icon={<ListIcon />} label="Applications" />
            <Tab icon={<BarChartIcon />} label="Analytics" />
          </Tabs>
        </Paper>
      </Box>
      
      {activeTab === 0 && (
        <>
          <ApplicationHistorySearch onSearch={handleSearch} />
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">
                Applications ({filteredApplications.length} of {applications.length})
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button 
                  variant="outlined" 
                  startIcon={<FileDownloadIcon />}
                  onClick={handleExportHistory}
                  disabled={applications.length === 0}
                >
                  Export
                </Button>
                <Button 
                  variant="outlined" 
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleClearHistory}
                  disabled={applications.length === 0}
                >
                  Clear History
                </Button>
              </Box>
            </Box>
            
            <Divider sx={{ mb: 3 }} />
            
            {applications.length === 0 ? (
              <Alert severity="info">
                <AlertTitle>No Applications</AlertTitle>
                You haven't submitted any job applications yet. Start by searching for jobs and applying!
                <Box sx={{ mt: 2 }}>
                  <Button 
                    variant="contained" 
                    color="primary"
                    onClick={() => navigate('/search')}
                  >
                    Find Jobs
                  </Button>
                </Box>
              </Alert>
            ) : filteredApplications.length === 0 ? (
              <Alert severity="info">
                <AlertTitle>No Matching Applications</AlertTitle>
                No applications match your current filter criteria. Try changing the filters or clearing them.
              </Alert>
            ) : (
              <Grid container spacing={3}>
                {filteredApplications.map((application, index) => (
                  <Grid item xs={12} key={index}>
                    <ApplicationHistoryCard application={application} />
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </>
      )}
      
      {activeTab === 1 && (
        <>
          <Box sx={{ mb: 3 }}>
            <ApplicationAnalytics applications={applications} />
          </Box>
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <ApplicationTrendsChart applicationData={applications} />
          </Paper>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Platform Distribution
                </Typography>
                
                {applications.length === 0 ? (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    No application data available
                  </Alert>
                ) : (
                  <Box sx={{ mt: 2 }}>
                    {/* Simple bar chart showing platform distribution */}
                    <Box sx={{ display: 'flex', height: 200, alignItems: 'flex-end' }}>
                      {Object.entries(
                        applications.reduce((acc, app) => {
                          const platform = (app.platform || 'external').toLowerCase();
                          acc[platform] = (acc[platform] || 0) + 1;
                          return acc;
                        }, {})
                      ).map(([platform, count], index) => {
                        const colors = {
                          linkedin: '#0077B5',
                          indeed: '#003A9B',
                          glassdoor: '#0CAA41',
                          google: '#4285F4',
                          external: '#FF6B6B'
                        };
                        
                        return (
                          <Box 
                            key={platform} 
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
                                backgroundColor: colors[platform] || '#999',
                                height: `${(count / applications.length) * 180}px`,
                                borderRadius: 1,
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'flex-start',
                                color: 'white',
                                fontWeight: 'bold',
                                pt: 0.5
                              }}
                            >
                              {count}
                            </Box>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              {platform.charAt(0).toUpperCase() + platform.slice(1)}
                            </Typography>
                          </Box>
                        );
                      })}
                    </Box>
                  </Box>
                )}
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Application Types
                </Typography>
                
                {applications.length === 0 ? (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    No application data available
                  </Alert>
                ) : (
                  <Box sx={{ mt: 2 }}>
                    {/* Simple bar chart showing application type distribution */}
                    <Box sx={{ display: 'flex', height: 200, alignItems: 'flex-end', justifyContent: 'center', gap: 4 }}>
                      {(() => {
                        const types = applications.reduce((acc, app) => {
                          const type = app.application_type || 'unknown';
                          acc[type] = (acc[type] || 0) + 1;
                          return acc;
                        }, {});
                        
                        const easyApply = types.easy_apply || 0;
                        const external = types.external || 0;
                        const total = applications.length;
                        
                        return [
                          {
                            type: 'Easy Apply',
                            count: easyApply,
                            color: '#2196F3'
                          },
                          {
                            type: 'External',
                            count: external,
                            color: '#FF9800'
                          }
                        ].map((item, index) => (
                          <Box 
                            key={index} 
                            sx={{ 
                              display: 'flex',
                              flexDirection: 'column',
                              alignItems: 'center'
                            }}
                          >
                            <Box 
                              sx={{ 
                                width: 80,
                                backgroundColor: item.color,
                                height: `${(item.count / total) * 180}px`,
                                borderRadius: 1,
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'flex-start',
                                color: 'white',
                                fontWeight: 'bold',
                                pt: 0.5
                              }}
                            >
                              {item.count}
                            </Box>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              {item.type}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {total > 0 ? Math.round((item.count / total) * 100) : 0}%
                            </Typography>
                          </Box>
                        ));
                      })()}
                    </Box>
                  </Box>
                )}
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
      
      {applications.length > 0 && (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button 
            variant="contained" 
            onClick={() => navigate('/search')}
          >
            Find More Jobs
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ApplicationHistory;