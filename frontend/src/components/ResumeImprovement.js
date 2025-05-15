import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Divider,
  Alert,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { getResumeImprovement } from '../services/userService';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import WorkIcon from '@mui/icons-material/Work';
import SchoolIcon from '@mui/icons-material/School';
import FormatAlignLeftIcon from '@mui/icons-material/FormatAlignLeft';
import SearchIcon from '@mui/icons-material/Search';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';

/**
 * Resume Improvement Component
 * 
 * Displays AI-powered improvement suggestions for a resume
 * 
 * @param {Object} props
 * @param {Object} props.resumeData - Parsed resume data to analyze
 */
const ResumeImprovement = ({ resumeData }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [step, setStep] = useState(0);
  const [aiProvider, setAiProvider] = useState(null);
  
  const handleGetSuggestions = async (customApiKey = null) => {
    if (!resumeData) {
      setError('No resume data available. Please upload or parse a resume first.');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Get improvement suggestions from the API - don't use apiKeyInput anymore
      const result = await getResumeImprovement(resumeData, customApiKey);
      
      if (result.success) {
        // Set the AI provider used for suggestions
        if (result.provider) {
          setAiProvider(result.provider);
        }
        
        if (result.suggestions) {
          setSuggestions(result.suggestions);
        } else if (result.raw_response) {
          // Handle case where JSON parsing failed but we got a raw response
          setError(`We received a response but couldn't parse it properly. Error: ${result.parsing_error}`);
          // Try to display the raw response in a structured way
          const formattedResponse = { 
            overall_impression: result.raw_response,
            critical_changes: ['Unable to parse structured suggestions'] 
          };
          setSuggestions(formattedResponse);
        }
      } else {
        setError(result.error || 'Failed to get resume improvement suggestions');
      }
    } catch (error) {
      console.error('Error getting resume suggestions:', error);
      setError(error.response?.data?.error || error.message || 'An error occurred');
    } finally {
      setLoading(false);
      setStep(1); // Move to suggestions view
    }
  };
  
  const handleReset = () => {
    setStep(0);
    setSuggestions(null);
    setError(null);
  };
  
  // Step 1 - API Key Input and Disclaimer
  const renderSetupStep = () => (
    <Paper sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Get AI-Powered Resume Improvement Suggestions
      </Typography>
      
      <Alert severity="info" sx={{ my: 2 }}>
        This feature uses AI to analyze your resume and provide personalized improvement suggestions.
        The system will use OpenAI GPT-4 by default, or Anthropic Claude if configured by an administrator.
        {error && <Box sx={{ mt: 1, fontWeight: 'medium', color: 'error.main' }}>{error}</Box>}
      </Alert>
      
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleGetSuggestions()}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <LightbulbIcon />}
            fullWidth
            sx={{ py: 1.5 }}
          >
            {loading ? 'Analyzing Resume...' : 'Analyze My Resume'}
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );
  
  // Step 2 - Display Suggestions
  const renderSuggestions = () => {
    if (!suggestions) return null;
    
    return (
      <Box>
        <Paper sx={{ p: 3, borderRadius: 2, mb: 3 }}>
          <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
            Resume Analysis Results
          </Typography>
          
          {aiProvider && (
            <Chip 
              label={aiProvider === 'anthropic' ? 'Powered by Anthropic Claude' : 'Powered by OpenAI GPT-4'} 
              size="small" 
              color={aiProvider === 'anthropic' ? 'secondary' : 'primary'} 
              variant="outlined"
              sx={{ mb: 2 }}
            />
          )}
          
          <Divider sx={{ my: 2 }} />
          
          {/* Overall Impression */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="medium">
              Overall Impression
            </Typography>
            <Typography variant="body1">
              {suggestions.overall_impression}
            </Typography>
          </Box>
          
          {/* Critical Changes */}
          <Box sx={{ mb: 3, mt: 4 }}>
            <Typography variant="h6" gutterBottom fontWeight="medium" color="error">
              Most Critical Changes Needed
            </Typography>
            
            <List>
              {suggestions.critical_changes && suggestions.critical_changes.map((change, index) => (
                <ListItem key={index} sx={{ py: 1 }}>
                  <ListItemIcon>
                    <PriorityHighIcon color="error" />
                  </ListItemIcon>
                  <ListItemText primary={change} />
                </ListItem>
              ))}
            </List>
          </Box>
          
          <Button
            variant="outlined"
            onClick={handleReset}
            sx={{ mt: 2 }}
          >
            Start Over
          </Button>
        </Paper>
        
        {/* Detailed Suggestions */}
        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          Detailed Improvement Suggestions
        </Typography>
        
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center">
              <FormatAlignLeftIcon sx={{ mr: 1.5 }} color="primary" />
              <Typography variant="subtitle1" fontWeight="medium">Content & Structure</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">
              {suggestions.content_structure}
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center">
              <FormatListBulletedIcon sx={{ mr: 1.5 }} color="primary" />
              <Typography variant="subtitle1" fontWeight="medium">Skills Presentation</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">
              {suggestions.skills_presentation}
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center">
              <WorkIcon sx={{ mr: 1.5 }} color="primary" />
              <Typography variant="subtitle1" fontWeight="medium">Experience Descriptions</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">
              {suggestions.experience_descriptions}
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center">
              <SchoolIcon sx={{ mr: 1.5 }} color="primary" />
              <Typography variant="subtitle1" fontWeight="medium">Education Section</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">
              {suggestions.education_section}
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center">
              <FormatAlignLeftIcon sx={{ mr: 1.5 }} color="primary" />
              <Typography variant="subtitle1" fontWeight="medium">Formatting & Readability</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">
              {suggestions.formatting_readability}
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center">
              <SearchIcon sx={{ mr: 1.5 }} color="primary" />
              <Typography variant="subtitle1" fontWeight="medium">Keywords & ATS Optimization</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1">
              {suggestions.keywords_ats}
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Box>
    );
  };
  
  // Main Render
  return (
    <Box>
      {/* Progress Stepper */}
      <Stepper activeStep={step} sx={{ mb: 4 }}>
        <Step>
          <StepLabel>Start Analysis</StepLabel>
        </Step>
        <Step>
          <StepLabel>View Suggestions</StepLabel>
        </Step>
      </Stepper>
      
      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Current Step Content */}
      {step === 0 ? renderSetupStep() : renderSuggestions()}
    </Box>
  );
};

export default ResumeImprovement;