import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Avatar, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import WorkIcon from '@mui/icons-material/Work';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import SettingsIcon from '@mui/icons-material/Settings';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { logout, getCurrentUser, isAdmin } from '../services/authService';

const Navbar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [user, setUser] = useState(null);
  const [userIsAdmin, setUserIsAdmin] = useState(false);
  
  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    setUserIsAdmin(isAdmin());
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
        {user ? (
          <>
            <Box>
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
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  {user.username ? user.username.charAt(0).toUpperCase() : 'U'}
                </Avatar>
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
