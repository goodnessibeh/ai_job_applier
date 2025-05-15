import api from './api';

/**
 * Upload and parse a resume file
 * @param {File} file The resume file to upload (PDF or DOCX)
 * @returns {Promise} The parsed resume data
 */
export const parseResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/parse-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error parsing resume:', error);
    throw error;
  }
};

/**
 * Save the parsed resume data to local storage for persistence
 * @param {Object} resumeData The parsed resume data
 */
export const saveResumeToStorage = (resumeData) => {
  try {
    localStorage.setItem('resume_data', JSON.stringify(resumeData));
  } catch (error) {
    console.error('Error saving resume to storage:', error);
  }
};

/**
 * Get the saved resume data from local storage
 * @returns {Object|null} The saved resume data or null if not found
 */
export const getResumeFromStorage = () => {
  try {
    const savedResume = localStorage.getItem('resume_data');
    return savedResume ? JSON.parse(savedResume) : null;
  } catch (error) {
    console.error('Error retrieving resume from storage:', error);
    return null;
  }
};
