import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Paper, 
  Button, 
  Stepper,
  Step,
  StepLabel,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Breadcrumbs,
  Link
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SendIcon from '@mui/icons-material/Send';

import { findJobById } from '../services/jobService';
import { getResumeFromStorage } from '../services/resumeService';
import { generateCustomizedApplication, submitApplication } from '../services/applicationService';
import ResumeViewer from '../components/ResumeViewer';
import CoverLetterViewer from '../components/CoverLetterViewer';
import ApplicationQuestions from '../components/ApplicationQuestions';

const steps = ['Review Resume', 'Generate Application', 'Submit Application'];

const ApplicationForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [activeStep, setActiveStep] = useState(0);
  const [job, setJob] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [application, setApplication] = useState(null);
  const [customAnswers, setCustomAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitResult, setSubmitResult] = useState(null);

  // Load job and resume data on initial mount
  useEffect(() => {
    const loadInitialData = () => {
      // Get job details
      const jobData = findJobById(id);
      if (!jobData) {
        setError('Job not found. It may have been removed or expired.');
        return;
      }
      setJob(jobData);
      
      // Get resume data
      const savedResume = getResumeFromStorage();
      if (!savedResume) {
        setError('Resume not found. Please upload your resume first.');
        return;
      }
      setResumeData(savedResume);
    };
    
    loadInitialData();
  }, [id]);
  
  const handleNext = () => {
    if (activeStep === 0) {
      // Move from step 1 to step 2 - Generate application
      handleGenerateApplication();
    } else if (activeStep === 1) {
      // Move from step 2 to step 3
      setActiveStep(2);
    } else if (activeStep === 2) {
      // Submit application
      handleSubmitApplication();
    }
  };
  
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  const handleGenerateApplication = async () => {
    if (!resumeData || !job) {
      setError('Missing resume or job data');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await generateCustomizedApplication(resumeData, job);
      setApplication(result);
      setActiveStep(1);
    } catch (err) {
      setError(err.message || 'Error generating application');
    } finally {
      setLoading(false);
    }
  };
  
  const handleUpdateAnswers = (answers) => {
    setCustomAnswers(answers);
  };
  
  const handleSubmitApplication = async () => {
    if (!application || !job) {
      setError('Missing application or job data');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Prepare final application with any custom answers
      const finalApplication = {
        ...application,
        application_answers: {
          ...application.application_answers,
          ...customAnswers
        }
      };
      
      const result = await submitApplication(job, finalApplication);
      setSubmitResult(result);
      setActiveStep(3); // Move to completed state
    } catch (err) {
      setError(err.message || 'Error submitting application');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Review Your Resume
              </Typography>
              <Typography variant="body1" paragraph>
                Review your resume below. Make sure it's up to date before generating your application.
              </Typography>
              <ResumeViewer resumeData={resumeData} />
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Customized Application
              </Typography>
              <Typography variant="body1" paragraph>
                We've customized your application materials based on your resume and the job description.
                Review and edit as needed before submitting.
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <CoverLetterViewer coverLetter={application?.cover_letter} />
            </Grid>
            <Grid item xs={12}>
              <ApplicationQuestions 
                applicationAnswers={application?.application_answers} 
                onUpdateAnswers={handleUpdateAnswers}
              />
            </Grid>
          </Grid>
        );
      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Ready to Submit
              </Typography>
              <Typography variant="body1" paragraph>
                Your application is ready to be submitted for the position of <strong>{job?.title}</strong> at <strong>{job?.company}</strong>.
              </Typography>
              <Alert severity="info">
                By clicking "Submit Application", our AI will attempt to automatically submit your application to the job portal.
                In some cases, manual steps might be required due to CAPTCHA, login requirements, or other verification processes.
              </Alert>
            </Grid>
          </Grid>
        );
      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Alert severity={submitResult?.success ? "success" : "error"} sx={{ mb: 3 }}>
                {submitResult?.success 
                  ? `Application successfully submitted! Application ID: ${submitResult.application_id}` 
                  : `Application submission failed: ${submitResult?.error || 'Unknown error'}`}
              </Alert>
              
              {submitResult?.success ? (
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Application Submitted Successfully
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Your application for <strong>{job?.title}</strong> at <strong>{job?.company}</strong> has been submitted successfully.
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Button 
                      variant="contained" 
                      color="primary"
                      onClick={() => navigate('/history')}
                    >
                      View Application History
                    </Button>
                  </Box>
                </Paper>
              ) : (
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Application Submission Failed
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Your application could not be submitted automatically. You may want to try applying directly on the job site.
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Button 
                      variant="contained" 
                      color="primary"
                      href={job?.url} 
                      target="_blank"
                    >
                      Apply Manually
                    </Button>
                  </Box>
                </Paper>
              )}
            </Grid>
          </Grid>
        );
      default:
        return 'Unknown step';
    }
  };

  if (error && (!resumeData || !job)) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          {error}
        </Typography>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/search')}
          sx={{ mr: 1 }}
        >
          Back to Search
        </Button>
        {!resumeData && (
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/resume')}
          >
            Upload Resume
          </Button>
        )}
      </Paper>
    );
  }

  return (
    <Box>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link 
          underline="hover" 
          color="inherit" 
          onClick={() => navigate('/')}
          sx={{ cursor: 'pointer' }}
        >
          Dashboard
        </Link>
        <Link 
          underline="hover" 
          color="inherit" 
          onClick={() => navigate('/search')}
          sx={{ cursor: 'pointer' }}
        >
          Job Search
        </Link>
        <Link 
          underline="hover" 
          color="inherit" 
          onClick={() => navigate(`/job/${id}`)}
          sx={{ cursor: 'pointer' }}
        >
          {job?.title}
        </Link>
        <Typography color="text.primary">Apply</Typography>
      </Breadcrumbs>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Apply to {job?.title}
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {job?.company}
        </Typography>
        
        <Box sx={{ mt: 4 }}>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>
        
        <Box sx={{ mt: 4 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 4 }}>
              <CircularProgress />
              <Typography variant="body1" sx={{ ml: 2 }}>
                {activeStep === 0 ? 'Generating application...' : 'Submitting application...'}
              </Typography>
            </Box>
          ) : (
            <Box>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}
              
              {renderStepContent(activeStep)}
              
              {activeStep !== 3 && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button
                    disabled={activeStep === 0}
                    onClick={handleBack}
                    startIcon={<ArrowBackIcon />}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNext}
                    endIcon={activeStep === 2 ? <SendIcon /> : <ArrowForwardIcon />}
                  >
                    {activeStep === 2 ? 'Submit Application' : 'Next'}
                  </Button>
                </Box>
              )}
              
              {activeStep === 3 && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button
                    onClick={() => navigate('/search')}
                    startIcon={<ArrowBackIcon />}
                  >
                    Back to Search
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => navigate('/')}
                  >
                    Dashboard
                  </Button>
                </Box>
              )}
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default ApplicationForm;
