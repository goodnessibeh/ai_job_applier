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
    openai: {
      api_key: '',
      enabled: false
    },
    anthropic: {
      api_key: '',
      enabled: true  // Default to enabled
    },
    linkedin: {
      client_id: '',
      client_secret: '',
      redirect_uri: 'http://localhost:3000/auth/linkedin/callback',
      enabled: false
    },
    indeed: {
      publisher_id: '',
      api_key: '',
      enabled: false
    },
    glassdoor: {
      partner_id: '',
      api_key: '',
      enabled: false
    },
    smtp: {
      server: '',
      port: 587,
      username: '',
      password: '',
      from_email: '',
      enabled: false
    },
    application: {
      max_applications_per_day: 10,
    }
  });
  
  const [showPasswords, setShowPasswords] = useState({
    openai_key: false,
    anthropic_key: false,
    linkedin_secret: false,
    indeed_key: false,
    glassdoor_key: false,
    smtp_password: false
  });
  
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [isLoading, setIsLoading] = useState(false);
  const [testEmailStatus, setTestEmailStatus] = useState({ loading: false, success: false, error: null });
  
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
      const response = await api.post('/api/settings/save', settings);
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
  
  const handleTestEmailSettings = async () => {
    setTestEmailStatus({ loading: true, success: false, error: null });
    try {
      const response = await api.post('/api/settings/test-smtp', settings.smtp);
      setTestEmailStatus({ loading: false, success: true, error: null });
      setSnackbarMessage('Test email sent successfully!');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Email test failed:', error);
      setTestEmailStatus({ 
        loading: false, 
        success: false, 
        error: error.response?.data?.error || error.message 
      });
      setSnackbarMessage('Test email failed: ' + (error.response?.data?.error || error.message));
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };
  
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
            Configure your settings to connect to job portals, enable AI features, and set up notifications.
          </Typography>
          
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>Your settings are stored securely</strong> - Keep your API keys and credentials safe by not sharing them with others.
          </Alert>
          
          {/* Email Notification Settings */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Email Notification Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    Configure email notifications for job applications. When enabled, you'll receive an email notification whenever an application is submitted.
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="SMTP Server"
                    value={settings.smtp.server}
                    onChange={(e) => handleChange('smtp', 'server', e.target.value)}
                    helperText="e.g. smtp.gmail.com"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="SMTP Port"
                    type="number"
                    value={settings.smtp.port}
                    onChange={(e) => handleChange('smtp', 'port', parseInt(e.target.value) || 587)}
                    helperText="Common ports: 587 (TLS), 465 (SSL)"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="SMTP Username"
                    value={settings.smtp.username}
                    onChange={(e) => handleChange('smtp', 'username', e.target.value)}
                    helperText="Usually your email address"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="SMTP Password"
                    value={settings.smtp.password}
                    onChange={(e) => handleChange('smtp', 'password', e.target.value)}
                    type={showPasswords.smtp_password ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('smtp_password')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.smtp_password ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                    helperText="For Gmail, you may need to use an app password"
                  />
                </Grid>
                
                <Grid item xs={12} md={8}>
                  <TextField
                    fullWidth
                    label="From Email Address"
                    value={settings.smtp.from_email}
                    onChange={(e) => handleChange('smtp', 'from_email', e.target.value)}
                    helperText="The email address that will appear as the sender"
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.smtp.enabled}
                        onChange={(e) => handleChange('smtp', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable Email Notifications"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="outlined"
                      startIcon={<SendIcon />}
                      onClick={handleTestEmailSettings}
                      disabled={
                        testEmailStatus.loading || 
                        !settings.smtp.server || 
                        !settings.smtp.username || 
                        !settings.smtp.password || 
                        !settings.smtp.from_email
                      }
                      sx={{ mr: 2 }}
                    >
                      {testEmailStatus.loading ? <CircularProgress size={24} /> : 'Test Email Settings'}
                    </Button>
                  </Box>
                  
                  {testEmailStatus.error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {testEmailStatus.error}
                    </Alert>
                  )}
                  
                  {testEmailStatus.success && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      Test email sent successfully!
                    </Alert>
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* Anthropic API Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Anthropic Claude API Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    The Anthropic Claude API is used to generate high-quality, detailed cover letters that better match your experience to job requirements.
                    <Link 
                      href="https://console.anthropic.com/settings/keys" 
                      target="_blank" 
                      sx={{ ml: 1 }}
                    >
                      Get your Anthropic API key here
                    </Link>
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={8}>
                  <TextField
                    fullWidth
                    label="Anthropic API Key"
                    value={settings.anthropic.api_key}
                    onChange={(e) => handleChange('anthropic', 'api_key', e.target.value)}
                    type={showPasswords.anthropic_key ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('anthropic_key')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.anthropic_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.anthropic.enabled}
                        onChange={(e) => handleChange('anthropic', 'enabled', e.target.checked)}
                      />
                    }
                    label="Use Anthropic for Cover Letters"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* OpenAI API Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">OpenAI API Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    The OpenAI API is used as a fallback for generating cover letters if Anthropic is not configured.
                    <Link 
                      href="https://platform.openai.com/api-keys" 
                      target="_blank" 
                      sx={{ ml: 1 }}
                    >
                      Get your API key here
                    </Link>
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={8}>
                  <TextField
                    fullWidth
                    label="OpenAI API Key"
                    value={settings.openai.api_key}
                    onChange={(e) => handleChange('openai', 'api_key', e.target.value)}
                    type={showPasswords.openai_key ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('openai_key')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.openai_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.openai.enabled}
                        onChange={(e) => handleChange('openai', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable OpenAI Features"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* LinkedIn API Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">LinkedIn API Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    LinkedIn API credentials are used to search for jobs on LinkedIn.
                    <Link 
                      href="https://www.linkedin.com/developers/apps" 
                      target="_blank"
                      sx={{ ml: 1 }}
                    >
                      Create a LinkedIn Developer App
                    </Link>
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Client ID"
                    value={settings.linkedin.client_id}
                    onChange={(e) => handleChange('linkedin', 'client_id', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Client Secret"
                    value={settings.linkedin.client_secret}
                    onChange={(e) => handleChange('linkedin', 'client_secret', e.target.value)}
                    type={showPasswords.linkedin_secret ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('linkedin_secret')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.linkedin_secret ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Redirect URI"
                    value={settings.linkedin.redirect_uri}
                    onChange={(e) => handleChange('linkedin', 'redirect_uri', e.target.value)}
                    helperText="This must match the redirect URI in your LinkedIn app settings"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.linkedin.enabled}
                        onChange={(e) => handleChange('linkedin', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable LinkedIn Integration"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* Indeed API Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Indeed API Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    Indeed API credentials are used to search for jobs on Indeed.
                    <Link 
                      href="https://developer.indeed.com/" 
                      target="_blank"
                      sx={{ ml: 1 }}
                    >
                      Get Indeed API credentials
                    </Link>
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Publisher ID"
                    value={settings.indeed.publisher_id}
                    onChange={(e) => handleChange('indeed', 'publisher_id', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="API Key"
                    value={settings.indeed.api_key}
                    onChange={(e) => handleChange('indeed', 'api_key', e.target.value)}
                    type={showPasswords.indeed_key ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('indeed_key')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.indeed_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.indeed.enabled}
                        onChange={(e) => handleChange('indeed', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable Indeed Integration"
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
          
          {/* Glassdoor API Settings */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Glassdoor API Settings</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" gutterBottom>
                    Glassdoor API credentials are used to search for jobs on Glassdoor.
                    <Link 
                      href="https://www.glassdoor.com/developer/register_input.htm" 
                      target="_blank"
                      sx={{ ml: 1 }}
                    >
                      Register for Glassdoor API
                    </Link>
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Partner ID"
                    value={settings.glassdoor.partner_id}
                    onChange={(e) => handleChange('glassdoor', 'partner_id', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="API Key"
                    value={settings.glassdoor.api_key}
                    onChange={(e) => handleChange('glassdoor', 'api_key', e.target.value)}
                    type={showPasswords.glassdoor_key ? 'text' : 'password'}
                    InputProps={{
                      endAdornment: (
                        <Button 
                          onClick={() => togglePasswordVisibility('glassdoor_key')}
                          sx={{ minWidth: 'auto' }}
                        >
                          {showPasswords.glassdoor_key ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </Button>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.glassdoor.enabled}
                        onChange={(e) => handleChange('glassdoor', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable Glassdoor Integration"
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