import api from './api';

/**
 * Save user settings to the backend
 * @param {Object} settings The settings object to save
 * @returns {Promise} The response from the server
 */
export const saveSettings = async (settings) => {
  try {
    const response = await api.post('/settings/save', settings);
    return response.data;
  } catch (error) {
    console.error('Error saving settings:', error);
    
    // Fallback to local storage if API fails
    try {
      localStorage.setItem('api_settings', JSON.stringify(settings));
      return { success: true, message: 'Settings saved locally (offline mode)' };
    } catch (localError) {
      throw new Error('Failed to save settings: ' + (error.response?.data?.error || error.message));
    }
  }
};

/**
 * Get user settings from the backend
 * @returns {Promise} The settings object
 */
export const getSettings = async () => {
  try {
    const response = await api.get('/settings/get');
    return response.data;
  } catch (error) {
    console.error('Error getting settings:', error);
    
    // Fallback to local storage if API fails
    const savedSettings = localStorage.getItem('api_settings');
    if (savedSettings) {
      return JSON.parse(savedSettings);
    }
    
    // Return default settings if nothing is saved
    return {
      openai: { enabled: false, api_key: '' },
      linkedin: { enabled: false, client_id: '', client_secret: '', redirect_uri: '' },
      indeed: { enabled: false, publisher_id: '', api_key: '' },
      glassdoor: { enabled: false, partner_id: '', api_key: '' },
      monster: { enabled: false, client_id: '', client_secret: '' },
      ziprecruiter: { enabled: false, api_key: '' },
      application: { simulation_mode: true, max_applications_per_day: 10 }
    };
  }
};