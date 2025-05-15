import api from './api';

/**
 * Set or clear authentication token
 */
export const setAuthToken = (authenticated) => {
  if (authenticated) {
    localStorage.setItem('isAuthenticated', 'true');
  } else {
    localStorage.removeItem('isAuthenticated');
  }
};

/**
 * Check if user is authenticated
 */
export const isUserAuthenticated = () => {
  return localStorage.getItem('isAuthenticated') === 'true' && 
         localStorage.getItem('user') !== null;
};

/**
 * Register a new user
 * @param {Object} userData - User registration data
 */
export const register = async (userData) => {
  try {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Login a regular user
 * @param {Object} credentials - User login credentials
 */
export const login = async (credentials) => {
  try {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Login an admin user
 * @param {Object} credentials - Admin login credentials
 */
export const adminLogin = async (credentials) => {
  try {
    const response = await api.post('/api/admin/login', credentials);
    setAuthToken(true); // Set auth token on successful login
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Logout the current user
 */
export const logout = async () => {
  try {
    await api.post('/api/auth/logout');
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    setAuthToken(false);
    return { success: true };
  } catch (error) {
    // Even if the API call fails, clear local storage
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    setAuthToken(false);
    throw error;
  }
};

/**
 * Get current user's profile
 */
export const getProfile = async () => {
  try {
    const response = await api.get('/api/auth/profile');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Change user password
 * @param {Object} passwordData - Password data
 */
export const changePassword = async (passwordData) => {
  try {
    const response = await api.post('/api/auth/change-password', passwordData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Send a password reset request
 * @param {string} email - User email
 */
export const forgotPassword = async (email) => {
  try {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Reset password with token
 * @param {Object} resetData - Reset data
 */
export const resetPassword = async (resetData) => {
  try {
    const response = await api.post('/api/auth/reset-password', resetData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Check authentication status
 */
export const checkAuth = async () => {
  try {
    const response = await api.get('/api/auth/check-auth');
    
    if (response.data.authenticated) {
      localStorage.setItem('isAuthenticated', 'true');
      // Update user data if we got fresh data from the server
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return { authenticated: true, user: response.data.user };
    } else {
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('user');
      return { authenticated: false };
    }
  } catch (error) {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    return { authenticated: false, error: error.message };
  }
};

/**
 * Get current user data from local storage
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Check if current user is admin
 */
export const isAdmin = () => {
  const user = getCurrentUser();
  return user && user.is_admin;
};