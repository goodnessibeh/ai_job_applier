import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Box, 
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  Alert,
  IconButton
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';
import SettingsIcon from '@mui/icons-material/Settings';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import LockIcon from '@mui/icons-material/Lock';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import api from '../services/api';

const AdminDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    users: 0,
    applications: 0,
    activeUsers: 0
  });
  const [recentUsers, setRecentUsers] = useState([]);
  
  // Password change dialog state
  const [passwordDialog, setPasswordDialog] = useState({
    open: false,
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    showCurrentPassword: false,
    showNewPassword: false,
    showConfirmPassword: false,
    loading: false
  });
  
  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  useEffect(() => {
    // In a real implementation, these would be API calls
    // Simulating API calls with setTimeout
    setTimeout(() => {
      setStats({
        users: 28,
        applications: 143,
        activeUsers: 15
      });
      
      setRecentUsers([
        { id: 1, username: 'user1', email: 'user1@example.com', lastLogin: '2023-05-14T15:30:45Z', applications: 12 },
        { id: 2, username: 'user2', email: 'user2@example.com', lastLogin: '2023-05-14T14:25:12Z', applications: 8 },
        { id: 3, username: 'user3', email: 'user3@example.com', lastLogin: '2023-05-14T10:15:33Z', applications: 4 },
        { id: 4, username: 'user4', email: 'user4@example.com', lastLogin: '2023-05-13T22:45:18Z', applications: 23 },
        { id: 5, username: 'user5', email: 'user5@example.com', lastLogin: '2023-05-13T18:10:05Z', applications: 0 }
      ]);
      
      setLoading(false);
    }, 1000);
  }, []);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Password dialog handlers
  const handleOpenPasswordDialog = () => {
    setPasswordDialog({
      ...passwordDialog,
      open: true,
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
      showCurrentPassword: false,
      showNewPassword: false,
      showConfirmPassword: false,
      loading: false
    });
  };
  
  const handleClosePasswordDialog = () => {
    setPasswordDialog({
      ...passwordDialog,
      open: false
    });
  };
  
  const handlePasswordChange = (field, value) => {
    setPasswordDialog({
      ...passwordDialog,
      [field]: value
    });
  };
  
  const togglePasswordVisibility = (field) => {
    setPasswordDialog({
      ...passwordDialog,
      [field]: !passwordDialog[field]
    });
  };
  
  const handleChangePassword = async () => {
    // Validate password
    if (passwordDialog.newPassword !== passwordDialog.confirmPassword) {
      setSnackbar({
        open: true,
        message: 'Passwords do not match',
        severity: 'error'
      });
      return;
    }
    
    if (passwordDialog.newPassword.length < 8) {
      setSnackbar({
        open: true,
        message: 'Password must be at least 8 characters long',
        severity: 'error'
      });
      return;
    }
    
    setPasswordDialog({
      ...passwordDialog,
      loading: true
    });
    
    try {
      const response = await api.post('/api/settings/admin/change-password', {
        current_password: passwordDialog.currentPassword,
        new_password: passwordDialog.newPassword
      });
      
      setSnackbar({
        open: true,
        message: 'Password changed successfully',
        severity: 'success'
      });
      
      handleClosePasswordDialog();
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error changing password: ' + (error.response?.data?.error || error.message),
        severity: 'error'
      });
    } finally {
      setPasswordDialog({
        ...passwordDialog,
        loading: false
      });
    }
  };
  
  // Snackbar handlers
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <SupervisorAccountIcon sx={{ mr: 1 }} /> Admin Dashboard
        </Typography>
        
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {/* Stats Cards */}
          <Grid item xs={12} sm={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon sx={{ mr: 1 }} /> Users
                </Typography>
                <Typography variant="h3">{stats.users}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total registered users
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <BusinessCenterIcon sx={{ mr: 1 }} /> Applications
                </Typography>
                <Typography variant="h3">{stats.applications}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total job applications submitted
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon sx={{ mr: 1 }} /> Active Users
                </Typography>
                <Typography variant="h3">{stats.activeUsers}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Users active in the last 24 hours
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Recent Users Table */}
          <Grid item xs={12} sx={{ mt: 2 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Users
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Last Login</TableCell>
                      <TableCell>Applications</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{formatDate(user.lastLogin)}</TableCell>
                        <TableCell>{user.applications}</TableCell>
                        <TableCell>
                          <Button 
                            startIcon={<SettingsIcon />} 
                            size="small" 
                            variant="outlined"
                          >
                            Manage
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          
          {/* Admin Actions */}
          <Grid item xs={12} sx={{ mt: 2 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Admin Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Button variant="contained">View All Users</Button>
                <Button variant="contained">Application Reports</Button>
                <Button variant="contained">System Settings</Button>
                <Button variant="contained" color="secondary">Maintenance Mode</Button>
                <Button 
                  variant="contained" 
                  color="primary" 
                  startIcon={<LockIcon />}
                  onClick={handleOpenPasswordDialog}
                >
                  Change Admin Password
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
      
      {/* Password Change Dialog */}
      <Dialog 
        open={passwordDialog.open} 
        onClose={handleClosePasswordDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Change Admin Password</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter your current password and a new password to change your admin credentials.
          </DialogContentText>
          
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              margin="dense"
              label="Current Password"
              type={passwordDialog.showCurrentPassword ? "text" : "password"}
              value={passwordDialog.currentPassword}
              onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
              InputProps={{
                endAdornment: (
                  <IconButton 
                    onClick={() => togglePasswordVisibility('showCurrentPassword')}
                    edge="end"
                  >
                    {passwordDialog.showCurrentPassword ? 
                      <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                )
              }}
            />
            
            <TextField
              fullWidth
              margin="dense"
              label="New Password"
              type={passwordDialog.showNewPassword ? "text" : "password"}
              value={passwordDialog.newPassword}
              onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
              InputProps={{
                endAdornment: (
                  <IconButton 
                    onClick={() => togglePasswordVisibility('showNewPassword')}
                    edge="end"
                  >
                    {passwordDialog.showNewPassword ? 
                      <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                )
              }}
              helperText="Must be at least 8 characters long"
            />
            
            <TextField
              fullWidth
              margin="dense"
              label="Confirm New Password"
              type={passwordDialog.showConfirmPassword ? "text" : "password"}
              value={passwordDialog.confirmPassword}
              onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
              InputProps={{
                endAdornment: (
                  <IconButton 
                    onClick={() => togglePasswordVisibility('showConfirmPassword')}
                    edge="end"
                  >
                    {passwordDialog.showConfirmPassword ? 
                      <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                )
              }}
              error={passwordDialog.newPassword !== passwordDialog.confirmPassword && 
                     passwordDialog.confirmPassword.length > 0}
              helperText={passwordDialog.newPassword !== passwordDialog.confirmPassword && 
                       passwordDialog.confirmPassword.length > 0 ? 
                       "Passwords don't match" : ""}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePasswordDialog}>Cancel</Button>
          <Button 
            onClick={handleChangePassword} 
            variant="contained" 
            color="primary"
            disabled={passwordDialog.loading || 
                     !passwordDialog.currentPassword ||
                     !passwordDialog.newPassword ||
                     !passwordDialog.confirmPassword ||
                     passwordDialog.newPassword !== passwordDialog.confirmPassword}
          >
            {passwordDialog.loading ? <CircularProgress size={24} /> : "Change Password"}
          </Button>
        </DialogActions>
      </Dialog>
      
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
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminDashboard;