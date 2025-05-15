import React, { useState, useEffect, createContext } from 'react';
  import { Routes, Route, Navigate } from 'react-router-dom';
  import { Box, CircularProgress, Typography } from '@mui/material';

  // Pages
  import Dashboard from './pages/Dashboard';
  import ResumeUpload from './pages/ResumeUpload';
  import JobSearch from './pages/JobSearch';
  import JobDetails from './pages/JobDetails';
  import ApplicationForm from './pages/ApplicationForm';
  import ApplicationHistory from './pages/ApplicationHistory';
  import Settings from './pages/Settings';
  import UserProfile from './pages/UserProfile';
  import Login from './pages/Login';
  import Register from './pages/Register';
  // Admin Pages
  import AdminDashboard from './pages/admin/Dashboard';
  import AdminSettings from './pages/admin/Settings';
  import UserManagement from './pages/admin/UserManagement';
  import AdminLogin from './pages/admin/Login';

  // Components
  import Navbar from './components/Navbar';
  import Sidebar from './components/Sidebar';
  import AdminLayout from './components/admin/AdminLayout';

  // Services
  import { checkAuth } from './services/authService';

  // Create Auth Context
  export const AuthContext = createContext(null);

  function App() {
    const [isLoading, setIsLoading] = useState(true);
    const [authState, setAuthState] = useState({
      isAuthenticated: false,
      isAdmin: false,
      user: null,
      isChecking: true
    });

    // Function to check auth status - can be called from login components
    const verifyAuth = async () => {
      try {
        setAuthState(prev => ({ ...prev, isChecking: true }));
        const result = await checkAuth();

        // Only update if component is still mounted
        setAuthState({
          isAuthenticated: result.authenticated,
          isAdmin: result.user?.is_admin || false,
          user: result.user || null,
          isChecking: false
        });

        return result.authenticated;
      } catch (error) {
        console.error('Authentication check failed:', error);
        setAuthState({
          isAuthenticated: false,
          isAdmin: false,
          user: null,
          isChecking: false
        });
        return false;
      }
    };

    // Check auth on initial load
    useEffect(() => {
      const initialAuthCheck = async () => {
        await verifyAuth();
        setIsLoading(false);
      };

      initialAuthCheck();
    }, []);

    if (isLoading) {
      return (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            flexDirection: 'column'
          }}
        >
          <CircularProgress />
          <Typography variant="body1" sx={{ mt: 2 }}>Loading...</Typography>
        </Box>
      );
    }

    return (
      <AuthContext.Provider value={{ ...authState, refreshAuth: verifyAuth }}>
        <Box sx={{ display: 'flex' }}>
          {/* Only show Navbar and Sidebar for non-admin authenticated pages */}
          {authState.isAuthenticated && !window.location.pathname.startsWith('/admin') && <Navbar />}
          {authState.isAuthenticated && !window.location.pathname.startsWith('/admin') && <Sidebar />}

          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: { xs: 2, sm: 3 },
              mt: authState.isAuthenticated && !window.location.pathname.startsWith('/admin') ? 8 : 0,
              ml: authState.isAuthenticated && !window.location.pathname.startsWith('/admin') ? { xs: 0, sm: 30 } : 0,
              width: authState.isAuthenticated && !window.location.pathname.startsWith('/admin') ? 'auto' : '100%'
            }}
          >
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={authState.isAuthenticated ? <Navigate to="/" /> : <Login />} />
              <Route path="/register" element={authState.isAuthenticated ? <Navigate to="/" /> : <Register />} />
              <Route path="/admin/login" element={
                authState.isAuthenticated && authState.isAdmin ? <Navigate to="/admin" /> : <AdminLogin />
              } />

              {/* Protected routes */}
              <Route path="/" element={
                authState.isAuthenticated ? <Dashboard /> : <Navigate to="/login" />
              } />
              <Route path="/resume" element={
                authState.isAuthenticated ? <ResumeUpload /> : <Navigate to="/login" />
              } />
              <Route path="/search" element={
                authState.isAuthenticated ? <JobSearch /> : <Navigate to="/login" />
              } />
              <Route path="/job/:id" element={
                authState.isAuthenticated ? <JobDetails /> : <Navigate to="/login" />
              } />
              <Route path="/apply/:id" element={
                authState.isAuthenticated ? <ApplicationForm /> : <Navigate to="/login" />
              } />
              <Route path="/history" element={
                authState.isAuthenticated ? <ApplicationHistory /> : <Navigate to="/login" />
              } />
              <Route path="/settings" element={
                authState.isAuthenticated ? <Settings /> : <Navigate to="/login" />
              } />
              <Route path="/profile" element={
                authState.isAuthenticated ? <UserProfile /> : <Navigate to="/login" />
              } />

              {/* Admin Protected Routes with Layout */}
              <Route element={<AdminLayout />}>
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/settings" element={<AdminSettings />} />
                <Route path="/admin/users" element={<UserManagement />} />
              </Route>

              {/* Redirects */}
              <Route path="*" element={<Navigate to={authState.isAuthenticated ? "/" : "/login"} />} />
            </Routes>
          </Box>
        </Box>
      </AuthContext.Provider>
    );
  }

  export default App;