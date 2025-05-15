import React, { useContext } from 'react';
import { 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Toolbar,
  Divider,
  Box,
  Typography
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';
import PersonIcon from '@mui/icons-material/Person';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { AuthContext } from '../App';

const drawerWidth = 240;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAdmin } = useContext(AuthContext);
  
  // Different menu items for regular users vs admin users
  const userMenuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Resume', icon: <DescriptionIcon />, path: '/resume' },
    { text: 'Find Jobs', icon: <SearchIcon />, path: '/search' },
    { text: 'Application History', icon: <HistoryIcon />, path: '/history' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];
  
  const adminMenuItems = [
    { text: 'Admin Dashboard', icon: <AdminPanelSettingsIcon />, path: '/admin' },
    { text: 'Manage Users', icon: <PersonIcon />, path: '/admin/users' },
    { text: 'System Settings', icon: <SettingsIcon />, path: '/admin/settings' },
  ];
  
  // Use appropriate menu items based on user role
  const menuItems = isAdmin ? adminMenuItems : userMenuItems;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        display: { xs: 'none', sm: 'block' },
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      
      {/* Menu header */}
      <Box sx={{ px: 3, py: 2 }}>
        <Typography 
          variant="subtitle1" 
          fontWeight="bold" 
          color="primary"
        >
          {isAdmin ? 'Admin Menu' : 'Main Menu'}
        </Typography>
      </Box>
      
      <List>
        {menuItems.map((item) => (
          <ListItem 
            button 
            key={item.text}
            onClick={() => navigate(item.path)}
            selected={location.pathname === item.path || 
                     (item.path !== '/' && location.pathname.startsWith(item.path))}
          >
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
    </Drawer>
  );
};

export default Sidebar;
