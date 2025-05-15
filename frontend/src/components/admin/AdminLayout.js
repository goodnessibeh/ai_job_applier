import React from 'react';
import { Box, Toolbar } from '@mui/material';
import { Navigate, Outlet } from 'react-router-dom';
import { getCurrentUser } from '../../services/authService';
import AdminNavbar from './AdminNavbar';

const AdminLayout = () => {
  const user = getCurrentUser();
  
  // Check if user is admin
  if (!user || user.role !== 'admin') {
    return <Navigate to="/admin/login" />;
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <AdminNavbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar /> {/* This empty Toolbar creates space below the AppBar */}
        <Outlet />
      </Box>
    </Box>
  );
};

export default AdminLayout;