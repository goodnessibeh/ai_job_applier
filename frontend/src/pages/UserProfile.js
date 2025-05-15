import React, { useState, useEffect } from 'react';
import {
  Container, 
  Paper, 
  Typography, 
  Grid, 
  TextField, 
  Button, 
  Box, 
  Card,
  CardContent,
  Snackbar,
  Alert,
  Divider,
  CircularProgress,
  Switch,
  FormControlLabel,
  Chip,
  Slider,
  FormGroup,
  IconButton,
  Tooltip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { getUserProfile, updateUserProfile } from '../services/userService';
import { getCurrentUser } from '../services/authService';
import ProfilePicture from '../components/ProfilePicture';

const UserProfile = () => {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    display_name: '',
    job_titles: [],
    min_salary: 0,
    max_commute_distance: 25,
    preferred_locations: [],
    remote_only: false,
    auto_apply_enabled: false,
    minimum_match_score: 70
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const [saving, setSaving] = useState(false);
  const [newJobTitle, setNewJobTitle] = useState('');
  const [newLocation, setNewLocation] = useState('');
  
  useEffect(() => {
    fetchUserProfile();
  }, []);
  
  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const userProfile = await getUserProfile();
      setProfile(userProfile);
      setFormData({
        display_name: userProfile.display_name || '',
        job_titles: userProfile.job_titles || [],
        min_salary: userProfile.min_salary || 0,
        max_commute_distance: userProfile.max_commute_distance || 25,
        preferred_locations: userProfile.preferred_locations || [],
        remote_only: userProfile.remote_only || false,
        auto_apply_enabled: userProfile.auto_apply_enabled || false,
        minimum_match_score: userProfile.minimum_match_score || 70
      });
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setSnackbar({
        open: true,
        message: 'Error loading profile data',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setFormData({
      ...formData,
      [name]: checked
    });
  };
  
  const handleSliderChange = (name) => (event, newValue) => {
    setFormData({
      ...formData,
      [name]: newValue
    });
  };
  
  const handleAddJobTitle = () => {
    if (newJobTitle.trim() !== '' && !formData.job_titles.includes(newJobTitle.trim())) {
      setFormData({
        ...formData,
        job_titles: [...formData.job_titles, newJobTitle.trim()]
      });
      setNewJobTitle('');
    }
  };
  
  const handleRemoveJobTitle = (title) => {
    setFormData({
      ...formData,
      job_titles: formData.job_titles.filter(t => t !== title)
    });
  };
  
  const handleAddLocation = () => {
    if (newLocation.trim() !== '' && !formData.preferred_locations.includes(newLocation.trim())) {
      setFormData({
        ...formData,
        preferred_locations: [...formData.preferred_locations, newLocation.trim()]
      });
      setNewLocation('');
    }
  };
  
  const handleRemoveLocation = (location) => {
    setFormData({
      ...formData,
      preferred_locations: formData.preferred_locations.filter(l => l !== location)
    });
  };
  
  const handleKeyPress = (e, addFunction) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      addFunction();
    }
  };
  
  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      const result = await updateUserProfile(formData);
      
      // Update profile state
      setProfile(result.user);
      
      // Update local storage
      const currentUser = getCurrentUser();
      if (currentUser) {
        const updatedUser = {
          ...currentUser,
          display_name: result.user.display_name,
          profile_picture_url: result.user.profile_picture_url
        };
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
      
      setSnackbar({
        open: true,
        message: 'Profile updated successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error saving profile:', error);
      setSnackbar({
        open: true,
        message: 'Error saving profile data',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };
  
  const handleProfilePictureUpdate = (newUrl) => {
    // Update the profile with new picture URL
    setProfile({
      ...profile,
      profile_picture_url: newUrl
    });
    
    // Also update user in local storage
    const currentUser = getCurrentUser();
    if (currentUser) {
      const updatedUser = {
        ...currentUser,
        profile_picture_url: newUrl
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };
  
  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main', mb: 3 }}>
        My Profile
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            boxShadow: (theme) => theme.shadows[3],
            borderRadius: 2,
            height: '100%'
          }}>
            <CardContent sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              p: 3
            }}>
              <Box sx={{ mb: 2 }}>
                <ProfilePicture 
                  userId={profile.id}
                  username={profile.display_name || profile.username}
                  pictureUrl={profile.profile_picture_url}
                  editable={true}
                  size={120}
                  onUpdate={handleProfilePictureUpdate}
                />
              </Box>
              
              <Typography variant="h5" sx={{ mt: 2, fontWeight: 'medium' }}>
                {profile.display_name || profile.username}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {profile.email}
              </Typography>
              
              <Divider sx={{ width: '100%', my: 2 }} />
              
              <Typography variant="body2" color="text.secondary">
                Member since: {new Date(profile.created_at).toLocaleDateString()}
              </Typography>
              
              {profile.last_login && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Last login: {new Date(profile.last_login).toLocaleString()}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={8}>
          {/* Basic Profile Information */}
          <Paper sx={{ 
            p: 3, 
            borderRadius: 2,
            boxShadow: (theme) => theme.shadows[3],
            mb: 3
          }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              Basic Information
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Username"
                  value={profile.username}
                  disabled
                  variant="outlined"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  value={profile.email}
                  disabled
                  variant="outlined"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="display_name"
                  label="Display Name"
                  value={formData.display_name}
                  onChange={handleInputChange}
                  variant="outlined"
                  helperText="This name will be shown throughout the application"
                />
              </Grid>
            </Grid>
          </Paper>
          
          {/* Job Preferences */}
          <Paper sx={{ 
            p: 3, 
            borderRadius: 2,
            boxShadow: (theme) => theme.shadows[3],
            mb: 3
          }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              Job Preferences
            </Typography>
            
            <Grid container spacing={3}>
              {/* Job Titles */}
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Job Titles You're Interested In
                </Typography>
                <Box sx={{ display: 'flex', mb: 2 }}>
                  <TextField
                    fullWidth
                    value={newJobTitle}
                    onChange={(e) => setNewJobTitle(e.target.value)}
                    onKeyPress={(e) => handleKeyPress(e, handleAddJobTitle)}
                    placeholder="Add a job title (e.g., Software Engineer)"
                    variant="outlined"
                    size="small"
                  />
                  <Button 
                    variant="contained" 
                    color="primary" 
                    startIcon={<AddIcon />}
                    onClick={handleAddJobTitle}
                    sx={{ ml: 1 }}
                  >
                    Add
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {formData.job_titles.map((title, index) => (
                    <Chip
                      key={index}
                      label={title}
                      onDelete={() => handleRemoveJobTitle(title)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                  {formData.job_titles.length === 0 && (
                    <Typography variant="body2" color="text.secondary">
                      Add job titles you're interested in to improve job matching
                    </Typography>
                  )}
                </Box>
              </Grid>
              
              {/* Minimum Salary */}
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Minimum Salary (USD/year)
                </Typography>
                <TextField
                  fullWidth
                  name="min_salary"
                  type="number"
                  value={formData.min_salary}
                  onChange={handleInputChange}
                  variant="outlined"
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                  }}
                />
              </Grid>
              
              {/* Max Commute Distance */}
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Maximum Commute Distance (miles)
                </Typography>
                <Slider
                  value={formData.max_commute_distance}
                  onChange={handleSliderChange('max_commute_distance')}
                  aria-labelledby="max-commute-slider"
                  valueLabelDisplay="auto"
                  step={5}
                  marks
                  min={0}
                  max={100}
                  disabled={formData.remote_only}
                />
                <Typography variant="body2" color="text.secondary" align="right">
                  {formData.remote_only ? 'Remote only' : `${formData.max_commute_distance} miles`}
                </Typography>
              </Grid>
              
              {/* Preferred Locations */}
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Preferred Locations
                </Typography>
                <Box sx={{ display: 'flex', mb: 2 }}>
                  <TextField
                    fullWidth
                    value={newLocation}
                    onChange={(e) => setNewLocation(e.target.value)}
                    onKeyPress={(e) => handleKeyPress(e, handleAddLocation)}
                    placeholder="Add a location (e.g., New York, NY)"
                    variant="outlined"
                    size="small"
                    disabled={formData.remote_only}
                  />
                  <Button 
                    variant="contained" 
                    color="primary" 
                    startIcon={<AddIcon />}
                    onClick={handleAddLocation}
                    sx={{ ml: 1 }}
                    disabled={formData.remote_only}
                  >
                    Add
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {formData.preferred_locations.map((location, index) => (
                    <Chip
                      key={index}
                      label={location}
                      onDelete={() => handleRemoveLocation(location)}
                      color="primary"
                      variant="outlined"
                      disabled={formData.remote_only}
                    />
                  ))}
                  {formData.preferred_locations.length === 0 && !formData.remote_only && (
                    <Typography variant="body2" color="text.secondary">
                      Add locations where you'd like to work
                    </Typography>
                  )}
                  {formData.remote_only && (
                    <Typography variant="body2" color="text.secondary">
                      Remote only selected - location preferences disabled
                    </Typography>
                  )}
                </Box>
              </Grid>
              
              {/* Remote Only Toggle */}
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.remote_only}
                      onChange={handleSwitchChange}
                      name="remote_only"
                      color="primary"
                    />
                  }
                  label="Remote Jobs Only"
                />
              </Grid>
            </Grid>
          </Paper>
          
          {/* Auto-Apply Preferences */}
          <Paper sx={{ 
            p: 3, 
            borderRadius: 2,
            boxShadow: (theme) => theme.shadows[3],
            mb: 3
          }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              Auto-Apply Settings
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.auto_apply_enabled}
                      onChange={handleSwitchChange}
                      name="auto_apply_enabled"
                      color="primary"
                    />
                  }
                  label="Enable Automatic Job Applications"
                />
                <Typography variant="body2" color="text.secondary">
                  When enabled, the system will automatically apply to jobs that match your preferences above the minimum match score.
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Minimum Match Score for Auto-Apply ({formData.minimum_match_score}%)
                </Typography>
                <Slider
                  value={formData.minimum_match_score}
                  onChange={handleSliderChange('minimum_match_score')}
                  aria-labelledby="match-score-slider"
                  valueLabelDisplay="auto"
                  step={5}
                  marks
                  min={0}
                  max={100}
                  disabled={!formData.auto_apply_enabled}
                />
                <Typography variant="body2" color="text.secondary">
                  Only jobs with a match score at or above this percentage will be auto-applied to.
                </Typography>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Save Button */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleSaveProfile}
              disabled={saving}
              size="large"
            >
              {saving ? <CircularProgress size={24} /> : 'Save All Changes'}
            </Button>
          </Box>
        </Grid>
      </Grid>
      
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

export default UserProfile;