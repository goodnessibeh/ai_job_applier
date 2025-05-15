import api from './api';

/**
 * Get user profile information
 * @returns {Promise} User profile data
 */
export const getUserProfile = async () => {
  try {
    const response = await api.get('/api/user/profile');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Update user profile information
 * @param {Object} profileData - User profile data to update
 * @returns {Promise} Updated user profile
 */
export const updateUserProfile = async (profileData) => {
  try {
    const response = await api.put('/api/user/profile', profileData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Upload a profile picture
 * @param {File} file - The image file to upload
 * @returns {Promise} Result with profile picture URL
 */
export const uploadProfilePicture = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/user/profile-picture', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Delete user's profile picture
 * @returns {Promise} Result with default profile picture URL
 */
export const deleteProfilePicture = async () => {
  try {
    const response = await api.delete('/api/user/profile-picture');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get improvement suggestions for a resume
 * @param {Object} resumeData - Resume data to analyze
 * @param {string} apiKey - Optional API key (can be Anthropic or OpenAI)
 * @param {string} provider - Optional provider name ('openai' or 'anthropic')
 * @returns {Promise} Resume improvement suggestions
 */
export const getResumeImprovement = async (resumeData, apiKey = null, provider = null) => {
  try {
    const payload = {
      resume_data: resumeData
    };
    
    // Include API key based on provider if specified
    if (apiKey) {
      if (provider === 'openai' || (provider === null && apiKey.startsWith('sk-'))) {
        payload.openai_api_key = apiKey;
      } else {
        payload.anthropic_api_key = apiKey;
      }
    }
    
    const response = await api.post('/api/improve-resume', payload);
    return response.data;
  } catch (error) {
    throw error;
  }
};