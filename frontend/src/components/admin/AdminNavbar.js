import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import WorkIcon from '@mui/icons-material/Work';
import LogoutIcon from '@mui/icons-material/Logout';
import SettingsIcon from '@mui/icons-material/Settings';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { logout, getCurrentUser } from '../../services/authService';
import ProfilePicture from '../ProfilePicture';

const AdminNavbar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [user, setUser] = useState(null);
  const [profilePicUrl, setProfilePicUrl] = useState('');
  
  useEffect(() => {
    // This effect needs to run whenever localStorage changes
    const handleStorageChange = () => {
      const currentUser = getCurrentUser();
      setUser(currentUser);
      
      // Update profile picture URL if available
      if (currentUser && currentUser.profile_picture_url) {
        // Add timestamp to force refresh
        const timestamp = new Date().getTime();
        const newUrl = currentUser.profile_picture_url.includes('?') 
          ? `${currentUser.profile_picture_url}&t=${timestamp}` 
          : `${currentUser.profile_picture_url}?t=${timestamp}`;
        setProfilePicUrl(newUrl);
      }
    };
    
    // Handler for custom profile picture update event
    const handleProfilePictureUpdate = (event) => {
      console.log('Profile picture updated event received:', event.detail);
      setProfilePicUrl(event.detail.url);
      
      // Also update the user in localStorage to ensure persistence
      const currentUser = getCurrentUser();
      if (currentUser) {
        currentUser.profile_picture_url = event.detail.url.split('?')[0]; // Store without timestamp
        localStorage.setItem('user', JSON.stringify(currentUser));
      }
    };
    
    // Initial load
    handleStorageChange();
    
    // Listen for storage events
    window.addEventListener('storage', handleStorageChange);
    
    // Listen for profile picture update events
    window.addEventListener('profile-picture-updated', handleProfilePictureUpdate);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('profile-picture-updated', handleProfilePictureUpdate);
    };
  }, []);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogout = () => {
    logout();
    setUser(null);
    handleClose();
    navigate('/admin/login');
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: 'secondary.main' }}>
      <Toolbar>
        <IconButton 
          edge="start" 
          color="inherit" 
          onClick={() => navigate('/admin')}
          sx={{ mr: 2 }}
        >
          <AdminPanelSettingsIcon />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI Job Applier - Admin
        </Typography>
        
        {user ? (
          <>
            <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
              <Button 
                color="inherit" 
                onClick={() => navigate('/admin')}
                startIcon={<DashboardIcon />}
              >
                Dashboard
              </Button>
              <Button 
                color="inherit" 
                onClick={() => navigate('/admin/users')}
                startIcon={<PeopleIcon />}
              >
                Users
              </Button>
              <Button 
                color="inherit" 
                onClick={() => navigate('/admin/reports')}
                startIcon={<AssessmentIcon />}
              >
                Reports
              </Button>
              <Button 
                color="inherit" 
                onClick={() => navigate('/admin/settings')}
                startIcon={<SettingsIcon />}
              >
                Settings
              </Button>
              <IconButton 
                color="inherit"
                onClick={handleMenu}
                aria-controls="user-menu"
                aria-haspopup="true"
              >
                <ProfilePicture 
                  userId={user.id}
                  username={user.username || user.display_name}
                  pictureUrl={profilePicUrl}
                  size={32}
                />
              </IconButton>
              <Menu
                id="user-menu"
                anchorEl={anchorEl}
                keepMounted
                open={Boolean(anchorEl)}
                onClose={handleClose}
              >
                <MenuItem disabled>
                  <Typography variant="body2">{user.email}</Typography>
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => { handleClose(); navigate('/'); }}>
                  <WorkIcon fontSize="small" sx={{ mr: 1 }} />
                  User Interface
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
                  Logout
                </MenuItem>
              </Menu>
            </Box>
            
            {/* Mobile navigation */}
            <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
              <IconButton 
                color="inherit"
                onClick={handleMenu}
                aria-controls="user-menu-mobile"
                aria-haspopup="true"
              >
                <ProfilePicture 
                  userId={user.id}
                  username={user.username || user.display_name}
                  pictureUrl={profilePicUrl}
                  size={32}
                />
              </IconButton>
              <Menu
                id="user-menu-mobile"
                anchorEl={anchorEl}
                keepMounted
                open={Boolean(anchorEl)}
                onClose={handleClose}
              >
                <MenuItem disabled>
                  <Typography variant="body2">{user.email}</Typography>
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => { handleClose(); navigate('/admin'); }}>
                  <DashboardIcon fontSize="small" sx={{ mr: 1 }} />
                  Dashboard
                </MenuItem>
                <MenuItem onClick={() => { handleClose(); navigate('/admin/users'); }}>
                  <PeopleIcon fontSize="small" sx={{ mr: 1 }} />
                  Users
                </MenuItem>
                <MenuItem onClick={() => { handleClose(); navigate('/admin/reports'); }}>
                  <AssessmentIcon fontSize="small" sx={{ mr: 1 }} />
                  Reports
                </MenuItem>
                <MenuItem onClick={() => { handleClose(); navigate('/admin/settings'); }}>
                  <SettingsIcon fontSize="small" sx={{ mr: 1 }} />
                  Settings
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => { handleClose(); navigate('/'); }}>
                  <WorkIcon fontSize="small" sx={{ mr: 1 }} />
                  User Interface
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
                  Logout
                </MenuItem>
              </Menu>
            </Box>
          </>
        ) : (
          <Button color="inherit" onClick={() => navigate('/admin/login')}>
            Login
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default AdminNavbar;