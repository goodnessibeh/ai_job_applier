import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import WorkIcon from '@mui/icons-material/Work';
import LogoutIcon from '@mui/icons-material/Logout';
import SettingsIcon from '@mui/icons-material/Settings';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonIcon from '@mui/icons-material/Person';
import { logout, getCurrentUser, isAdmin } from '../services/authService';
import ProfilePicture from './ProfilePicture';

const Navbar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [user, setUser] = useState(null);
  const [userIsAdmin, setUserIsAdmin] = useState(false);
  const [profilePicUrl, setProfilePicUrl] = useState('');
  
  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    setUserIsAdmin(isAdmin());
    
    // Set initial profile picture URL if available
    if (currentUser && currentUser.profile_picture_url) {
      setProfilePicUrl(currentUser.profile_picture_url);
    }
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
    setUserIsAdmin(false);
    handleClose();
    navigate('/login');
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton 
          edge="start" 
          color="inherit" 
          onClick={() => navigate('/')}
          sx={{ mr: 2 }}
        >
          <WorkIcon />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI Job Applier
        </Typography>
        {user && (
          <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
            <IconButton
              color="inherit"
              aria-label="menu"
              onClick={() => navigate('/')}
              size="small"
            >
              <PersonIcon />
            </IconButton>
          </Box>
        )}
        {user ? (
          <>
            <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
              <Button color="inherit" onClick={() => navigate('/')}>
                Dashboard
              </Button>
              <Button color="inherit" onClick={() => navigate('/resume')}>
                Resume
              </Button>
              <Button color="inherit" onClick={() => navigate('/search')}>
                Find Jobs
              </Button>
              <Button color="inherit" onClick={() => navigate('/history')}>
                History
              </Button>
              <Button color="inherit" onClick={() => navigate('/settings')}>
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
                <MenuItem onClick={() => { handleClose(); navigate('/profile'); }}>
                  <PersonIcon fontSize="small" sx={{ mr: 1 }} />
                  My Profile
                </MenuItem>
                <MenuItem onClick={() => { handleClose(); navigate('/settings'); }}>
                  <SettingsIcon fontSize="small" sx={{ mr: 1 }} />
                  Account Settings
                </MenuItem>
                {userIsAdmin && (
                  <MenuItem onClick={() => { handleClose(); navigate('/admin'); }}>
                    <AdminPanelSettingsIcon fontSize="small" sx={{ mr: 1 }} />
                    Admin Panel
                  </MenuItem>
                )}
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
                  Logout
                </MenuItem>
              </Menu>
            </Box>
          </>
        ) : (
          <Box>
            <Button color="inherit" onClick={() => navigate('/login')}>
              Login
            </Button>
            <Button color="inherit" onClick={() => navigate('/register')}>
              Register
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
