import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Tabs,
  Tab,
  Snackbar,
  IconButton
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import EmailIcon from '@mui/icons-material/Email';
import ApiIcon from '@mui/icons-material/Api';
import SaveIcon from '@mui/icons-material/Save';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import TelegramIcon from '@mui/icons-material/Telegram';
import api from '../../services/api';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdminSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    // SMTP Settings
    smtp_server: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_from_email: '',
    notifications_enabled: false,
    
    // API Keys
    anthropic_api_key: '',
    openai_api_key: '',
    
    // Preferences
    use_anthropic: true,
    use_openai: false,
    
    // App Settings
    max_applications_per_day: 10
  });
  
  // UI State
  const [tabValue, setTabValue] = useState(0);
  const [showPasswords, setShowPasswords] = useState({
    smtp: false,
    anthropic: false,
    openai: false
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  // Load settings
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await api.get('/api/settings/admin');
        if (response.data && response.data.settings) {
          setSettings(response.data.settings);
        }
      } catch (error) {
        console.error('Error loading settings:', error);
        setSnackbar({
          open: true,
          message: 'Error loading settings: ' + (error.response?.data?.error || error.message),
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    };
    
    loadSettings();
  }, []);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Handle input change
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  // Toggle password visibility
  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };
  
  // Save settings
  const handleSaveSettings = async () => {
    setSaving(true);
    
    try {
      await api.post('/api/settings/admin', { settings });
      
      setSnackbar({
        open: true,
        message: 'Settings saved successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      setSnackbar({
        open: true,
        message: 'Error saving settings: ' + (error.response?.data?.error || error.message),
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };
  
  // Test SMTP connection
  const handleTestSMTP = async () => {
    if (!settings.smtp_server || !settings.smtp_port || !settings.smtp_username || 
        !settings.smtp_password || !settings.smtp_from_email) {
      setSnackbar({
        open: true,
        message: 'Please fill in all SMTP fields',
        severity: 'warning'
      });
      return;
    }
    
    setLoading(true);
    
    try {
      await api.post('/api/settings/admin/test-smtp', { 
        smtp_settings: {
          server: settings.smtp_server,
          port: settings.smtp_port,
          username: settings.smtp_username,
          password: settings.smtp_password,
          from_email: settings.smtp_from_email
        }
      });
      
      setSnackbar({
        open: true,
        message: 'SMTP connection test successful',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error testing SMTP:', error);
      setSnackbar({
        open: true,
        message: 'SMTP test failed: ' + (error.response?.data?.error || error.message),
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Test API keys
  const handleTestAPIKey = async (provider) => {
    const apiKey = provider === 'anthropic' ? settings.anthropic_api_key : settings.openai_api_key;
    
    if (!apiKey) {
      setSnackbar({
        open: true,
        message: `Please enter an API key for ${provider}`,
        severity: 'warning'
      });
      return;
    }
    
    setLoading(true);
    
    try {
      await api.post('/api/settings/admin/test-api-key', { 
        provider,
        api_key: apiKey
      });
      
      setSnackbar({
        open: true,
        message: `${provider} API key validation successful`,
        severity: 'success'
      });
    } catch (error) {
      console.error(`Error testing ${provider} API key:`, error);
      setSnackbar({
        open: true,
        message: `API key test failed: ${error.response?.data?.error || error.message}`,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Close snackbar
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };
  
  if (loading && !settings.smtp_server) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '80vh' 
      }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
          Loading Settings...
        </Typography>
      </Box>
    );
  }
  
  return (
    <Container 
      maxWidth="lg"
      sx={{
        pb: { xs: 8, sm: 4 } // Add bottom padding for mobile navigation
      }}
    >
      <Box sx={{ my: { xs: 3, md: 4 } }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom 
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            fontSize: { xs: '1.75rem', sm: '2.125rem' },
            fontWeight: 'bold',
            color: 'primary.main',
            pb: 1,
            borderBottom: '2px solid',
            borderColor: 'primary.main',
            width: 'fit-content'
          }}
        >
          <SettingsIcon sx={{ mr: 1.5, fontSize: { xs: '1.75rem', sm: '2.125rem' } }} /> 
          System Settings
        </Typography>
        
        <Paper 
          sx={{ 
            mt: 3, 
            borderRadius: 2,
            boxShadow: 3
          }}
        >
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              aria-label="settings tabs"
              sx={{ px: 2 }}
            >
              <Tab 
                icon={<ApiIcon />} 
                iconPosition="start" 
                label="API Keys" 
                id="settings-tab-0"
                aria-controls="settings-tabpanel-0"
              />
              <Tab 
                icon={<EmailIcon />} 
                iconPosition="start" 
                label="Email Settings" 
                id="settings-tab-1"
                aria-controls="settings-tabpanel-1"
              />
              <Tab 
                icon={<SettingsIcon />} 
                iconPosition="start" 
                label="Application Settings" 
                id="settings-tab-2" 
                aria-controls="settings-tabpanel-2" 
              />
            </Tabs>
          </Box>
          
          {/* API Keys Tab */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  mb: 3,
                  color: 'primary.main',
                  fontWeight: 'bold'
                }}
              >
                <ApiIcon sx={{ mr: 1 }} /> API Key Configuration
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                Configure AI providers for resume improvement suggestions and cover letter generation.
                By default, OpenAI is used if no keys are set. If both keys are set, you can select which provider to use as default.
              </Alert>
              
              <Grid container spacing={3}>
                {/* Anthropic API Key */}
                <Grid item xs={12}>
                  <Card sx={{ borderRadius: 2, mb: 3 }}>
                    <CardContent>
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        mb: 2,
                        pb: 1,
                        borderBottom: '1px solid',
                        borderColor: 'divider'
                      }}>
                        <SmartToyIcon 
                          sx={{ 
                            mr: 1.5, 
                            color: 'secondary.main'
                          }} 
                        />
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            fontWeight: 'bold', 
                            color: 'secondary.main'
                          }}
                        >
                          Anthropic Claude
                        </Typography>
                      </Box>
                      
                      <TextField 
                        fullWidth
                        variant="outlined"
                        label="Anthropic API Key"
                        name="anthropic_api_key"
                        value={settings.anthropic_api_key}
                        onChange={handleChange}
                        type={showPasswords.anthropic ? "text" : "password"}
                        sx={{ mb: 2 }}
                        InputProps={{
                          endAdornment: (
                            <IconButton 
                              onClick={() => togglePasswordVisibility('anthropic')}
                              edge="end"
                            >
                              {showPasswords.anthropic ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          )
                        }}
                      />
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.use_anthropic} 
                              onChange={handleChange} 
                              name="use_anthropic"
                              color="secondary"
                            />
                          }
                          label="Use Anthropic as default AI provider"
                        />
                        
                        <Button 
                          variant="outlined" 
                          color="secondary"
                          onClick={() => handleTestAPIKey('anthropic')}
                          disabled={!settings.anthropic_api_key || loading}
                          startIcon={<ApiIcon />}
                        >
                          Test API Key
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                
                {/* OpenAI API Key */}
                <Grid item xs={12}>
                  <Card sx={{ borderRadius: 2, mb: 3 }}>
                    <CardContent>
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        mb: 2,
                        pb: 1,
                        borderBottom: '1px solid',
                        borderColor: 'divider'
                      }}>
                        <SmartToyIcon 
                          sx={{ 
                            mr: 1.5, 
                            color: 'primary.main'
                          }} 
                        />
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            fontWeight: 'bold', 
                            color: 'primary.main'
                          }}
                        >
                          OpenAI GPT-4
                        </Typography>
                      </Box>
                      
                      <TextField 
                        fullWidth
                        variant="outlined"
                        label="OpenAI API Key"
                        name="openai_api_key"
                        value={settings.openai_api_key}
                        onChange={handleChange}
                        type={showPasswords.openai ? "text" : "password"}
                        sx={{ mb: 2 }}
                        InputProps={{
                          endAdornment: (
                            <IconButton 
                              onClick={() => togglePasswordVisibility('openai')}
                              edge="end"
                            >
                              {showPasswords.openai ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          )
                        }}
                      />
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.use_openai} 
                              onChange={handleChange} 
                              name="use_openai"
                            />
                          }
                          label="Use OpenAI as default AI provider"
                        />
                        
                        <Button 
                          variant="outlined" 
                          color="primary"
                          onClick={() => handleTestAPIKey('openai')}
                          disabled={!settings.openai_api_key || loading}
                          startIcon={<ApiIcon />}
                        >
                          Test API Key
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          </TabPanel>
          
          {/* Email Settings Tab */}
          <TabPanel value={tabValue} index={1}>
            <Box sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  mb: 3,
                  color: 'primary.main',
                  fontWeight: 'bold'
                }}
              >
                <EmailIcon sx={{ mr: 1 }} /> Email Notification Settings
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                Configure SMTP settings for sending application notifications to users.
                All emails will be sent from the specified account.
              </Alert>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField 
                    fullWidth
                    variant="outlined"
                    label="SMTP Server"
                    name="smtp_server"
                    value={settings.smtp_server}
                    onChange={handleChange}
                    helperText="e.g., smtp.gmail.com"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField 
                    fullWidth
                    variant="outlined"
                    label="SMTP Port"
                    name="smtp_port"
                    type="number"
                    value={settings.smtp_port}
                    onChange={handleChange}
                    helperText="e.g., 587 for TLS, 465 for SSL"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField 
                    fullWidth
                    variant="outlined"
                    label="SMTP Username"
                    name="smtp_username"
                    value={settings.smtp_username}
                    onChange={handleChange}
                    helperText="Usually your email address"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField 
                    fullWidth
                    variant="outlined"
                    label="SMTP Password"
                    name="smtp_password"
                    value={settings.smtp_password}
                    onChange={handleChange}
                    type={showPasswords.smtp ? "text" : "password"}
                    helperText="For Gmail, use an app password"
                    InputProps={{
                      endAdornment: (
                        <IconButton 
                          onClick={() => togglePasswordVisibility('smtp')}
                          edge="end"
                        >
                          {showPasswords.smtp ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      )
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField 
                    fullWidth
                    variant="outlined"
                    label="From Email Address"
                    name="smtp_from_email"
                    value={settings.smtp_from_email}
                    onChange={handleChange}
                    helperText="The email address that will appear in the 'From' field"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <FormControlLabel
                      control={
                        <Switch 
                          checked={settings.notifications_enabled} 
                          onChange={handleChange} 
                          name="notifications_enabled"
                        />
                      }
                      label="Enable Email Notifications"
                    />
                    
                    <Button 
                      variant="outlined" 
                      color="primary"
                      onClick={handleTestSMTP}
                      disabled={!settings.smtp_server || !settings.smtp_port || 
                                !settings.smtp_username || !settings.smtp_password || 
                                !settings.smtp_from_email || loading}
                      startIcon={<TelegramIcon />}
                    >
                      Test SMTP Connection
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </TabPanel>
          
          {/* Application Settings Tab */}
          <TabPanel value={tabValue} index={2}>
            <Box sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  mb: 3,
                  color: 'primary.main',
                  fontWeight: 'bold'
                }}
              >
                <SettingsIcon sx={{ mr: 1 }} /> Application Settings
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                Configure global application settings that apply to all users.
              </Alert>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField 
                    fullWidth
                    variant="outlined"
                    label="Maximum Applications Per Day"
                    name="max_applications_per_day"
                    type="number"
                    value={settings.max_applications_per_day}
                    onChange={handleChange}
                    helperText="Limit how many applications a user can submit per day"
                    InputProps={{ inputProps: { min: 1, max: 100 } }}
                  />
                </Grid>
              </Grid>
            </Box>
          </TabPanel>
          
          <Divider />
          
          <Box sx={{ p: { xs: 2, sm: 3 }, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleSaveSettings}
              disabled={saving}
              startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
              sx={{ px: 4, py: 1.5 }}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Box>
        </Paper>
      </Box>
      
      {/* Snackbar for notifications */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminSettings;