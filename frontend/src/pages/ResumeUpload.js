import React, { useState } from 'react';
import { 
  Typography, 
  Box, 
  Button, 
  Paper, 
  Alert,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  CardActions,
  Stack,
  Divider 
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ArticleIcon from '@mui/icons-material/Article';
import DeleteIcon from '@mui/icons-material/Delete';

import useResume from '../hooks/useResume';
import ResumeViewer from '../components/ResumeViewer';

const ResumeUpload = () => {
  const { resumeData, loading, error, uploadResume, clearResume } = useResume();
  const [file, setFile] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file type
      const fileExt = selectedFile.name.split('.').pop().toLowerCase();
      if (fileExt !== 'pdf' && fileExt !== 'docx') {
        setUploadError('Please upload a PDF or DOCX file.');
        return;
      }
      
      setFile(selectedFile);
      setUploadError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadError('Please select a file first.');
      return;
    }

    try {
      await uploadResume(file);
      setFile(null);
    } catch (err) {
      setUploadError(err.message || 'Error uploading resume');
    }
  };

  const handleClearResume = () => {
    if (window.confirm('Are you sure you want to clear your resume data?')) {
      clearResume();
      setFile(null);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Resume Management
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              Upload Your Resume
            </Typography>
            <Typography variant="body1" paragraph>
              Upload your resume in PDF or DOCX format. We'll parse it to extract your skills, 
              experience and other information to help you apply for jobs faster.
            </Typography>
            
            {/* File upload section */}
            <Box sx={{ my: 3 }}>
              <input
                accept=".pdf,.docx"
                style={{ display: 'none' }}
                id="resume-file-input"
                type="file"
                onChange={handleFileChange}
                disabled={loading}
              />
              <label htmlFor="resume-file-input">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={<UploadFileIcon />}
                  disabled={loading}
                >
                  Select File
                </Button>
              </label>
              
              {file && (
                <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                  {file.name.endsWith('.pdf') ? (
                    <PictureAsPdfIcon color="error" sx={{ mr: 1 }} />
                  ) : (
                    <ArticleIcon color="primary" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="body2">{file.name}</Typography>
                </Box>
              )}
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleUpload}
                  disabled={!file || loading}
                  sx={{ mr: 2 }}
                >
                  {loading ? 'Uploading...' : 'Parse Resume'}
                </Button>
                
                {resumeData && (
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={handleClearResume}
                    disabled={loading}
                  >
                    Clear Data
                  </Button>
                )}
              </Box>
              
              {loading && <LinearProgress sx={{ mt: 2 }} />}
              
              {uploadError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {uploadError}
                </Alert>
              )}
              
              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </Box>
            
            <Divider sx={{ my: 3 }} />
            
            {/* Tips */}
            <Typography variant="h6" gutterBottom>
              Tips for Better Results
            </Typography>
            <Stack spacing={1}>
              <Typography variant="body2">
                • Make sure your resume is in a standard format without unusual formatting
              </Typography>
              <Typography variant="body2">
                • Include clear section headings (Experience, Education, Skills, etc.)
              </Typography>
              <Typography variant="body2">
                • List your skills explicitly in a dedicated section
              </Typography>
              <Typography variant="body2">
                • Use common job titles that match industry standards
              </Typography>
            </Stack>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          {/* Preview parsed resume */}
          <ResumeViewer resumeData={resumeData} />
          
          {/* Quick actions */}
          {resumeData && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  What's Next?
                </Typography>
                <Typography variant="body2" paragraph>
                  Now that your resume is parsed, you can search for jobs and start applying.
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  variant="contained" 
                  color="primary"
                  href="/search"
                >
                  Find Jobs
                </Button>
              </CardActions>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResumeUpload;
