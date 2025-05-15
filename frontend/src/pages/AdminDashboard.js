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
  IconButton,
  Divider,
  Chip
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
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '80vh' 
      }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
          Loading Admin Dashboard...
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
          <SupervisorAccountIcon sx={{ mr: 1.5, fontSize: { xs: '1.75rem', sm: '2.125rem' } }} /> 
          Admin Dashboard
        </Typography>
        
        <Grid container spacing={{ xs: 2, md: 3 }} sx={{ mt: { xs: 2, md: 3 } }}>
          {/* Stats Cards */}
          <Grid item xs={12} sm={4}>
            <Card 
              sx={{ 
                height: '100%', 
                borderRadius: 2,
                boxShadow: 3,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 5
                }
              }}
            >
              <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    color: 'primary.main',
                    fontWeight: 'bold'
                  }}
                >
                  <Box 
                    sx={{ 
                      backgroundColor: 'primary.light', 
                      borderRadius: '50%', 
                      width: 40, 
                      height: 40, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mr: 1.5
                    }}
                  >
                    <PersonIcon sx={{ color: 'primary.main' }} />
                  </Box>
                  Users
                </Typography>
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontWeight: 'bold', 
                    my: 2,
                    fontSize: { xs: '2.5rem', sm: '3rem' }
                  }}
                >
                  {stats.users}
                </Typography>
                <Typography 
                  variant="body1" 
                  color="text.secondary"
                  sx={{
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    pt: 1
                  }}
                >
                  Total registered users
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card 
              sx={{ 
                height: '100%', 
                borderRadius: 2,
                boxShadow: 3,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 5
                }
              }}
            >
              <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    color: 'success.main',
                    fontWeight: 'bold'
                  }}
                >
                  <Box 
                    sx={{ 
                      backgroundColor: 'success.light', 
                      borderRadius: '50%', 
                      width: 40, 
                      height: 40, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mr: 1.5
                    }}
                  >
                    <BusinessCenterIcon sx={{ color: 'success.main' }} />
                  </Box>
                  Applications
                </Typography>
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontWeight: 'bold', 
                    my: 2,
                    fontSize: { xs: '2.5rem', sm: '3rem' }
                  }}
                >
                  {stats.applications}
                </Typography>
                <Typography 
                  variant="body1" 
                  color="text.secondary"
                  sx={{
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    pt: 1
                  }}
                >
                  Total job applications submitted
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card 
              sx={{ 
                height: '100%', 
                borderRadius: 2,
                boxShadow: 3,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: 5
                }
              }}
            >
              <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    color: 'info.main',
                    fontWeight: 'bold'
                  }}
                >
                  <Box 
                    sx={{ 
                      backgroundColor: 'info.light', 
                      borderRadius: '50%', 
                      width: 40, 
                      height: 40, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      mr: 1.5
                    }}
                  >
                    <PersonIcon sx={{ color: 'info.main' }} />
                  </Box>
                  Active Users
                </Typography>
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontWeight: 'bold', 
                    my: 2,
                    fontSize: { xs: '2.5rem', sm: '3rem' }
                  }}
                >
                  {stats.activeUsers}
                </Typography>
                <Typography 
                  variant="body1" 
                  color="text.secondary"
                  sx={{
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    pt: 1
                  }}
                >
                  Users active in the last 24 hours
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Admin Actions */}
          <Grid item xs={12} md={4} sx={{ mt: { xs: 2, md: 0 } }}>
            <Paper 
              sx={{ 
                p: { xs: 2, sm: 3 },
                height: '100%',
                borderRadius: 2,
                boxShadow: 3
              }}
              elevation={3}
            >
              <Typography 
                variant="h6" 
                gutterBottom
                color="primary"
                fontWeight="bold"
                sx={{
                  mb: 2,
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <SettingsIcon sx={{ mr: 1 }} />
                Admin Actions
              </Typography>
              
              <Divider sx={{ mb: 3 }} />
              
              <Box 
                sx={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  gap: 2
                }}
              >
                <Button 
                  variant="contained"
                  fullWidth
                  size="large"
                  sx={{
                    py: 1.5,
                    fontWeight: 'medium',
                    boxShadow: 2,
                    '&:hover': {
                      boxShadow: 4
                    }
                  }}
                  startIcon={<PersonIcon />}
                  onClick={() => navigate('/admin/users')}
                >
                  Manage Users
                </Button>
                
                <Button 
                  variant="contained"
                  fullWidth
                  size="large"
                  sx={{
                    py: 1.5,
                    fontWeight: 'medium',
                    boxShadow: 2,
                    '&:hover': {
                      boxShadow: 4
                    }
                  }}
                  startIcon={<BusinessCenterIcon />}
                  onClick={() => navigate('/admin/reports')}
                >
                  Application Reports
                </Button>
                
                <Button 
                  variant="contained"
                  fullWidth
                  size="large"
                  sx={{
                    py: 1.5,
                    fontWeight: 'medium',
                    boxShadow: 2,
                    '&:hover': {
                      boxShadow: 4
                    }
                  }}
                  startIcon={<SettingsIcon />}
                  onClick={() => navigate('/admin/settings')}
                >
                  System Settings
                </Button>
                
                <Button 
                  variant="contained" 
                  color="secondary"
                  fullWidth
                  size="large"
                  sx={{
                    py: 1.5,
                    fontWeight: 'medium',
                    boxShadow: 2,
                    '&:hover': {
                      boxShadow: 4
                    }
                  }}
                  startIcon={<SettingsIcon />}
                >
                  Maintenance Mode
                </Button>
                
                <Button 
                  variant="contained" 
                  color="warning"
                  fullWidth
                  size="large"
                  sx={{
                    py: 1.5,
                    fontWeight: 'medium',
                    boxShadow: 2,
                    '&:hover': {
                      boxShadow: 4
                    }
                  }}
                  startIcon={<LockIcon />}
                  onClick={handleOpenPasswordDialog}
                >
                  Change Admin Password
                </Button>
              </Box>
            </Paper>
          </Grid>
          
          {/* Recent Users Table */}
          <Grid item xs={12} md={8} sx={{ mt: { xs: 2, md: 0 } }}>
            <Paper 
              sx={{ 
                p: { xs: 2, sm: 3 },
                borderRadius: 2,
                boxShadow: 3,
                overflowX: 'auto'
              }}
              elevation={3}
            >
              <Typography 
                variant="h6" 
                gutterBottom
                color="primary"
                fontWeight="bold"
                sx={{
                  mb: 2,
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <PersonIcon sx={{ mr: 1 }} />
                Recent Users
              </Typography>
              
              <Divider sx={{ mb: 3 }} />
              
              <TableContainer
                sx={{
                  borderRadius: 1,
                  '& .MuiTableCell-head': {
                    fontWeight: 'bold',
                    backgroundColor: (theme) => theme.palette.action.hover
                  }
                }}
              >
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Last Login</TableCell>
                      <TableCell align="center">Applications</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentUsers.map((user) => (
                      <TableRow 
                        key={user.id}
                        sx={{
                          '&:hover': {
                            backgroundColor: (theme) => theme.palette.action.hover
                          }
                        }}
                      >
                        <TableCell sx={{ fontWeight: 'medium' }}>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>
                          {formatDate(user.lastLogin)}
                        </TableCell>
                        <TableCell align="center">
                          <Chip 
                            label={user.applications} 
                            color={user.applications > 0 ? "primary" : "default"}
                            size="small"
                            sx={{ fontWeight: 'bold' }}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Button 
                            startIcon={<SettingsIcon />} 
                            size="small" 
                            variant="outlined"
                            sx={{
                              borderRadius: 1
                            }}
                            onClick={() => navigate(`/admin/users`)}
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
        </Grid>
      </Box>
      
      {/* Password Change Dialog */}
      <Dialog 
        open={passwordDialog.open} 
        onClose={handleClosePasswordDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: 4,
            overflow: 'hidden'
          }
        }}
      >
        <DialogTitle 
          sx={{ 
            background: (theme) => theme.palette.primary.main,
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            p: 2,
            fontWeight: 'bold'
          }}
        >
          <LockIcon /> Change Admin Password
        </DialogTitle>
        
        <DialogContent sx={{ p: { xs: 2.5, sm: 3 }, pt: { xs: 2.5, sm: 3 } }}>
          <DialogContentText sx={{ mb: 2.5, color: 'text.secondary' }}>
            Enter your current password and a new password to change your admin credentials.
          </DialogContentText>
          
          <Divider sx={{ mb: 3 }} />
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              label="Current Password"
              type={passwordDialog.showCurrentPassword ? "text" : "password"}
              value={passwordDialog.currentPassword}
              onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
              InputProps={{
                startAdornment: (
                  <LockIcon color="action" sx={{ mr: 1 }} />
                ),
                endAdornment: (
                  <IconButton 
                    onClick={() => togglePasswordVisibility('showCurrentPassword')}
                    edge="end"
                    aria-label={passwordDialog.showCurrentPassword ? "Hide password" : "Show password"}
                  >
                    {passwordDialog.showCurrentPassword ? 
                      <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                ),
                sx: { 
                  borderRadius: 1,
                  py: 0.5
                }
              }}
            />
            
            <TextField
              fullWidth
              variant="outlined"
              label="New Password"
              type={passwordDialog.showNewPassword ? "text" : "password"}
              value={passwordDialog.newPassword}
              onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
              InputProps={{
                startAdornment: (
                  <LockIcon color="action" sx={{ mr: 1 }} />
                ),
                endAdornment: (
                  <IconButton 
                    onClick={() => togglePasswordVisibility('showNewPassword')}
                    edge="end"
                    aria-label={passwordDialog.showNewPassword ? "Hide password" : "Show password"}
                  >
                    {passwordDialog.showNewPassword ? 
                      <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                ),
                sx: { 
                  borderRadius: 1,
                  py: 0.5
                }
              }}
              helperText="Must be at least 8 characters long"
              FormHelperTextProps={{
                sx: { mt: 0.5 }
              }}
            />
            
            <TextField
              fullWidth
              variant="outlined"
              label="Confirm New Password"
              type={passwordDialog.showConfirmPassword ? "text" : "password"}
              value={passwordDialog.confirmPassword}
              onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
              InputProps={{
                startAdornment: (
                  <LockIcon color="action" sx={{ mr: 1 }} />
                ),
                endAdornment: (
                  <IconButton 
                    onClick={() => togglePasswordVisibility('showConfirmPassword')}
                    edge="end"
                    aria-label={passwordDialog.showConfirmPassword ? "Hide password" : "Show password"}
                  >
                    {passwordDialog.showConfirmPassword ? 
                      <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                ),
                sx: { 
                  borderRadius: 1,
                  py: 0.5
                }
              }}
              error={passwordDialog.newPassword !== passwordDialog.confirmPassword && 
                     passwordDialog.confirmPassword.length > 0}
              helperText={passwordDialog.newPassword !== passwordDialog.confirmPassword && 
                       passwordDialog.confirmPassword.length > 0 ? 
                       "Passwords don't match" : ""}
              FormHelperTextProps={{
                sx: { mt: 0.5 }
              }}
            />
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 2.5, pt: 0, justifyContent: 'flex-end', gap: 1 }}>
          <Button 
            onClick={handleClosePasswordDialog}
            variant="outlined"
            sx={{ 
              borderRadius: 1,
              fontWeight: 'medium',
              px: 2
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleChangePassword} 
            variant="contained" 
            color="primary"
            disabled={passwordDialog.loading || 
                     !passwordDialog.currentPassword ||
                     !passwordDialog.newPassword ||
                     !passwordDialog.confirmPassword ||
                     passwordDialog.newPassword !== passwordDialog.confirmPassword}
            startIcon={passwordDialog.loading ? null : <LockIcon />}
            sx={{ 
              borderRadius: 1,
              fontWeight: 'medium',
              boxShadow: 2,
              px: 2,
              '&:hover': {
                boxShadow: 4
              }
            }}
            aria-label="Change password"
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
        sx={{ mb: { xs: 7, sm: 2 } }} // Adjusted for mobile bottom navigation
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ 
            width: '100%',
            boxShadow: 3,
            borderRadius: 1
          }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminDashboard;