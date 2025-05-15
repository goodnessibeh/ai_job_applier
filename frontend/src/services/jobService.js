import api from './api';

/**
 * Search for jobs matching the given criteria
 * @param {Object} criteria Search parameters (keywords, location, job_type, etc.)
 * @returns {Promise} The list of matching jobs
 */
export const searchJobs = async (criteria) => {
  try {
    // Note: criteria may contain auto_apply: true which will trigger auto-application on the backend
    const response = await api.post('/search-jobs', criteria);
    
    // Mark auto-applied jobs if they were processed by the backend
    const jobs = response.data.jobs || [];
    
    // Inject a flag for any auto-applied jobs for UI display
    jobs.forEach(job => {
      if (job.auto_applied) {
        job.applicationStatus = 'Applied automatically';
      }
    });
    
    return jobs;
  } catch (error) {
    console.error('Error searching jobs:', error);
    throw error;
  }
};

/**
 * Save the job search results to local storage for persistence
 * @param {Array} jobs The list of job results
 */
export const saveJobsToStorage = (jobs) => {
  try {
    localStorage.setItem('recent_job_results', JSON.stringify(jobs));
  } catch (error) {
    console.error('Error saving jobs to storage:', error);
  }
};

/**
 * Get the saved job results from local storage
 * @returns {Array|null} The saved job results or null if not found
 */
export const getJobsFromStorage = () => {
  try {
    const savedJobs = localStorage.getItem('recent_job_results');
    return savedJobs ? JSON.parse(savedJobs) : null;
  } catch (error) {
    console.error('Error retrieving jobs from storage:', error);
    return null;
  }
};

/**
 * Find a specific job by ID from the cached job results
 * @param {string} jobId The job ID to find
 * @returns {Object|null} The job object or null if not found
 */
export const findJobById = (jobId) => {
  const savedJobs = getJobsFromStorage();
  if (!savedJobs) return null;
  
  return savedJobs.find(job => job.id === jobId) || null;
};

/**
 * Save a job to the user's saved/favorite jobs
 * @param {Object} job The job to save
 */
export const saveJobToFavorites = (job) => {
  try {
    const savedFavorites = localStorage.getItem('favorite_jobs');
    const favorites = savedFavorites ? JSON.parse(savedFavorites) : [];
    
    // Check if already saved
    if (!favorites.some(favJob => favJob.id === job.id)) {
      favorites.push(job);
      localStorage.setItem('favorite_jobs', JSON.stringify(favorites));
    }
  } catch (error) {
    console.error('Error saving job to favorites:', error);
  }
};

/**
 * Get the user's saved/favorite jobs
 * @returns {Array} The list of saved jobs
 */
export const getFavoriteJobs = () => {
  try {
    const savedFavorites = localStorage.getItem('favorite_jobs');
    return savedFavorites ? JSON.parse(savedFavorites) : [];
  } catch (error) {
    console.error('Error retrieving favorite jobs:', error);
    return [];
  }
};
