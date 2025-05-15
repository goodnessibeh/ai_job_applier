import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Paper,
  TextField,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Link,
  CircularProgress
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SaveIcon from '@mui/icons-material/Save';
import KeyIcon from '@mui/icons-material/Key';
import InfoIcon from '@mui/icons-material/Info';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EmailIcon from '@mui/icons-material/Email';
import SendIcon from '@mui/icons-material/Send';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { isAdmin } from '../services/authService';

const Settings = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    user: {
      username: '',
      email: '',
      display_name: '',
      current_password: '',
      new_password: '',
      confirm_password: ''
    },
    application: {
      max_applications_per_day: 10,
    },
    system: {
      ai_enabled: true,
      job_portals_enabled: true
    }
  });
  
  const [showPasswords, setShowPasswords] = useState({
    current_password: false,
    new_password: false,
    confirm_password: false
  });
  
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [isLoading, setIsLoading] = useState(false);
  // Load saved settings from API
  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        // Get user settings
        const response = await api.get('/api/settings/get');
        setSettings(response.data);
      } catch (error) {
        console.error('Error loading settings:', error);
        setSnackbarMessage('Error loading settings');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSettings();
  }, []);
  
  const handleChange = (section, field, value) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [section]: {
        ...prevSettings[section],
        [field]: value
      }
    }));
  };
  
  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };
  
  const handleSaveSettings = async () => {
    setIsLoading(true);
    try {
      // Validate password if user is changing it
      if (settings.user.new_password || settings.user.current_password) {
        if (!settings.user.current_password) {
          throw new Error('Current password is required');
        }
        
        if (settings.user.new_password !== settings.user.confirm_password) {
          throw new Error('New passwords do not match');
        }
        
        if (settings.user.new_password && settings.user.new_password.length < 8) {
          throw new Error('Password must be at least 8 characters long');
        }
      }
      
      // Prepare data to save - only include what's needed
      const dataToSave = {
        user: {
          display_name: settings.user.display_name
        },
        application: {
          max_applications_per_day: settings.application.max_applications_per_day
        }
      };
      
      // Add password change if needed
      if (settings.user.new_password && settings.user.current_password) {
        dataToSave.user.current_password = settings.user.current_password;
        dataToSave.user.new_password = settings.user.new_password;
      }
      
      const response = await api.post('/api/settings/save', dataToSave);
      
      // Clear password fields after successful save
      setSettings(prev => ({
        ...prev,
        user: {
          ...prev.user,
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
      }));
      
      setSnackbarMessage('Settings saved successfully!');
      setSnackbarSeverity('success');
    } catch (error) {
      console.error('Error saving settings:', error);
      setSnackbarMessage('Error saving settings: ' + (error.response?.data?.error || error.message));
      setSnackbarSeverity('error');
    } finally {
      setIsLoading(false);
      setSnackbarOpen(true);
    }
  };
  
  // No longer needed - SMTP testing is for admins only
  
  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };
  
  // Check if user is admin
  const userIsAdmin = isAdmin();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      {!isLoading && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            User Settings
          </Typography>
          <Typography variant="body1" paragraph>
            Configure your user profile and application preferences.
          </Typography>
          
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>Your settings are stored securely</strong> - API keys and integration settings are managed by administrators.
          </Alert>
          
          {/* User Profile Settings */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">User Profile</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    Manage your profile information.
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Username"
                    value={settings.user.username}
                    disabled
                    helperText="Your username cannot be changed"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    value={settings.user.email}
                    disabled
                    helperText="Contact an administrator to change your email"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Display Name"
                    value={settings.user.display_name}
                    onChange={(e) => handleChange('user', 'display_name', e.target.value)}
                    helperText="This name will be displayed throughout the application"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* Password Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Change Password</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    Update your account password. For security, you'll need to provide your current password.
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Current Password"
                    value={settings.user.current_password || ''}
                    onChange={(e) => handleChange('user', 'current_password', e.target.value)}
                    type={showPasswords.current_password ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('current_password')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.current_password ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="New Password"
                    value={settings.user.new_password || ''}
                    onChange={(e) => handleChange('user', 'new_password', e.target.value)}
                    type={showPasswords.new_password ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('new_password')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.new_password ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                    helperText="Use a strong password with at least 8 characters"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Confirm New Password"
                    value={settings.user.confirm_password || ''}
                    onChange={(e) => handleChange('user', 'confirm_password', e.target.value)}
                    type={showPasswords.confirm_password ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('confirm_password')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.confirm_password ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                    error={settings.user.new_password !== settings.user.confirm_password && settings.user.confirm_password !== ''}
                    helperText={settings.user.new_password !== settings.user.confirm_password && settings.user.confirm_password !== '' ? 'Passwords do not match' : ''}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* Application Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Application Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    Configure how applications are submitted and set limits.
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Maximum Applications Per Day"
                    type="number"
                    value={settings.application.max_applications_per_day}
                    onChange={(e) => handleChange('application', 'max_applications_per_day', parseInt(e.target.value) || 0)}
                    InputProps={{ inputProps: { min: 1, max: 100 } }}
                    helperText="Limit the number of applications the system can submit in a day"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <strong>System Status:</strong>
                    <Box sx={{ mt: 1 }}>
                      AI Services: {settings.system.ai_enabled ? 
                        <span style={{ color: 'green' }}>Enabled</span> : 
                        <span style={{ color: 'red' }}>Disabled</span>}
                    </Box>
                    <Box>
                      Job Portal Integrations: {settings.system.job_portals_enabled ? 
                        <span style={{ color: 'green' }}>Enabled</span> : 
                        <span style={{ color: 'red' }}>Disabled</span>}
                    </Box>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Contact an administrator if you need system settings changed.
                    </Typography>
                  </Alert>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              onClick={handleSaveSettings}
              size="large"
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Save Settings'}
            </Button>
          </Box>
        </Paper>
      )}
      
      {/* Admin settings section */}
      {userIsAdmin && (
        <Paper sx={{ p: 3, mb: 3, backgroundColor: '#f8f9fa' }}>
          <Typography variant="h5" gutterBottom color="primary">
            Admin Settings
          </Typography>
          <Typography variant="body1" paragraph>
            These settings are only available to administrators.
          </Typography>
          
          <Alert severity="warning" sx={{ mb: 3 }}>
            <strong>Admin privileges detected</strong> - Changes made here will affect all users of the system. Proceed with caution.
          </Alert>
          
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/admin')}
          >
            Go to Admin Dashboard
          </Button>
        </Paper>
      )}
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;