import api from './api';

/**
 * Generate a customized application based on resume and job data
 * @param {Object} resumeData The parsed resume data
 * @param {Object} jobData The job details
 * @returns {Promise} The customized application
 */
export const generateCustomizedApplication = async (resumeData, jobData) => {
  try {
    const response = await api.post('/customize-application', {
      resume: resumeData,
      job: jobData
    });
    return response.data.application;
  } catch (error) {
    console.error('Error generating application:', error);
    throw error;
  }
};

/**
 * Submit a job application
 * @param {Object} jobData The job details
 * @param {Object} applicationData The customized application data
 * @returns {Promise} The submission result
 */
export const submitApplication = async (jobData, applicationData) => {
  try {
    const response = await api.post('/submit-application', {
      job: jobData,
      application: applicationData
    });
    
    // If successful, save to application history
    if (response.data.result && response.data.result.success) {
      saveApplicationToHistory(response.data.result);
    }
    
    return response.data.result;
  } catch (error) {
    console.error('Error submitting application:', error);
    throw error;
  }
};

/**
 * Save an application submission result to the application history
 * @param {Object} applicationResult The result of the application submission
 */
export const saveApplicationToHistory = (applicationResult) => {
  try {
    const savedHistory = localStorage.getItem('application_history');
    const history = savedHistory ? JSON.parse(savedHistory) : [];
    
    // Add timestamp if not present
    if (!applicationResult.timestamp) {
      applicationResult.timestamp = new Date().toISOString();
    }
    
    // Add to history and sort by timestamp (newest first)
    history.unshift(applicationResult);
    localStorage.setItem('application_history', JSON.stringify(history));
  } catch (error) {
    console.error('Error saving application to history:', error);
  }
};

/**
 * Get the application submission history
 * @returns {Array} The application history
 */
export const getApplicationHistory = () => {
  try {
    const savedHistory = localStorage.getItem('application_history');
    return savedHistory ? JSON.parse(savedHistory) : [];
  } catch (error) {
    console.error('Error retrieving application history:', error);
    return [];
  }
};

/**
 * Search and filter application history
 * @param {Object} filters The filter criteria
 * @returns {Array} The filtered application history
 */
export const searchApplicationHistory = (filters) => {
  try {
    const history = getApplicationHistory();
    
    return history.filter(app => {
      // Text search
      if (filters.searchText) {
        const searchText = filters.searchText.toLowerCase();
        const position = (app.position || '').toLowerCase();
        const company = (app.company || '').toLowerCase();
        const description = (app.description || '').toLowerCase();
        
        if (!position.includes(searchText) && 
            !company.includes(searchText) && 
            !description.includes(searchText)) {
          return false;
        }
      }
      
      // Status filter
      if (filters.applicationStatus !== 'all') {
        const isSuccess = filters.applicationStatus === 'success';
        if (app.success !== isSuccess) {
          return false;
        }
      }
      
      // Type filter
      if (filters.applicationType !== 'all') {
        if (app.application_type !== filters.applicationType) {
          return false;
        }
      }
      
      // Platform filter
      if (filters.platform !== 'all') {
        if (app.platform !== filters.platform) {
          return false;
        }
      }
      
      // Date range filter
      if (filters.dateRange) {
        const appDate = new Date(app.timestamp);
        
        if (filters.dateRange.startDate) {
          const startDate = new Date(filters.dateRange.startDate);
          if (appDate < startDate) {
            return false;
          }
        }
        
        if (filters.dateRange.endDate) {
          const endDate = new Date(filters.dateRange.endDate);
          // Add 1 day to include the end date
          endDate.setDate(endDate.getDate() + 1);
          if (appDate > endDate) {
            return false;
          }
        }
      }
      
      return true;
    });
  } catch (error) {
    console.error('Error searching application history:', error);
    return [];
  }
};

/**
 * Get application statistics
 * @returns {Object} The application statistics
 */
export const getApplicationStats = () => {
  try {
    const history = getApplicationHistory();
    
    // Calculate general stats
    const totalApplications = history.length;
    const successfulApplications = history.filter(app => app.success).length;
    const failedApplications = totalApplications - successfulApplications;
    const successRate = totalApplications > 0 ? (successfulApplications / totalApplications) * 100 : 0;
    
    // Calculate platform distribution
    const platforms = {};
    history.forEach(app => {
      const platform = app.platform || 'unknown';
      platforms[platform] = (platforms[platform] || 0) + 1;
    });
    
    // Calculate application type distribution
    const types = {
      easy_apply: 0,
      external: 0
    };
    history.forEach(app => {
      const type = app.application_type || 'unknown';
      if (types[type] !== undefined) {
        types[type]++;
      }
    });
    
    // Get date of first application
    const firstAppDate = history.length > 0 
      ? new Date(history[history.length - 1].timestamp) 
      : new Date();
      
    // Calculate applications over time
    const now = new Date();
    const daysSinceFirstApp = Math.ceil((now - firstAppDate) / (24 * 60 * 60 * 1000));
    const avgPerDay = daysSinceFirstApp > 0 ? totalApplications / daysSinceFirstApp : 0;
    
    return {
      totalApplications,
      successfulApplications,
      failedApplications,
      successRate,
      platforms,
      types,
      firstAppDate,
      avgPerDay
    };
  } catch (error) {
    console.error('Error calculating application statistics:', error);
    return {
      totalApplications: 0,
      successfulApplications: 0,
      failedApplications: 0,
      successRate: 0,
      platforms: {},
      types: { easy_apply: 0, external: 0 },
      firstAppDate: new Date(),
      avgPerDay: 0
    };
  }
};

/**
 * Export application history to a CSV file
 * @returns {Blob} The CSV file as a Blob
 */
export const exportApplicationHistory = () => {
  try {
    const history = getApplicationHistory();
    
    if (history.length === 0) {
      return null;
    }
    
    // Define CSV headers
    const headers = [
      'Job Title',
      'Company',
      'Platform',
      'Application Type',
      'Status',
      'Date',
      'Notes'
    ];
    
    // Convert data to CSV rows
    const rows = history.map(app => [
      app.position || '',
      app.company || '',
      app.platform || 'External',
      app.application_type || 'Unknown',
      app.success ? 'Successful' : 'Failed',
      new Date(app.timestamp).toLocaleString(),
      app.message || app.error || ''
    ]);
    
    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');
    
    // Create a Blob with the CSV content
    return new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  } catch (error) {
    console.error('Error exporting application history:', error);
    return null;
  }
};

/**
 * Clear the application submission history
 */
export const clearApplicationHistory = () => {
  try {
    localStorage.removeItem('application_history');
  } catch (error) {
    console.error('Error clearing application history:', error);
  }
};