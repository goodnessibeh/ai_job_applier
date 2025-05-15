import { useState, useEffect } from 'react';
import { parseResume, saveResumeToStorage, getResumeFromStorage } from '../services/resumeService';

/**
 * Custom hook for managing resume data
 * @returns {Object} Resume state and functions
 */
const useResume = () => {
  const [resumeData, setResumeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load resume data from local storage on initial mount
  useEffect(() => {
    const savedResume = getResumeFromStorage();
    if (savedResume) {
      setResumeData(savedResume);
    }
  }, []);

  /**
   * Upload and parse a resume file
   * @param {File} file The resume file to upload
   */
  const uploadResume = async (file) => {
    setLoading(true);
    setError(null);

    try {
      const response = await parseResume(file);
      const parsedData = response.data;
      
      // Save to state and local storage
      setResumeData(parsedData);
      saveResumeToStorage(parsedData);
      
      setLoading(false);
      return parsedData;
    } catch (err) {
      setError(err.message || 'Error parsing resume');
      setLoading(false);
      throw err;
    }
  };

  /**
   * Clear the resume data
   */
  const clearResume = () => {
    setResumeData(null);
    localStorage.removeItem('resume_data');
  };

  return {
    resumeData,
    loading,
    error,
    uploadResume,
    clearResume,
  };
};

export default useResume;
