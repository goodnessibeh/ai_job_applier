import axios from 'axios';

  // Use port 5001 to match your backend
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

  const api = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // This is critical for sending cookies with requests
  });

  // Add a response interceptor to handle authentication errors
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle 401 Unauthorized errors
      if (error.response && error.response.status === 401) {
        // Clear local storage auth data to match server state
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('user');

        // Redirect to login page if not already there
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );

  export default api;