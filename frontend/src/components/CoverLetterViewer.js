import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const CoverLetterViewer = ({ coverLetter }) => {
  if (!coverLetter) {
    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6">No cover letter available</Typography>
        <Typography>Generate a cover letter first</Typography>
      </Paper>
    );
  }

  // Process the cover letter text to maintain formatting
  const formattedText = coverLetter.split('\n').map((line, index) => (
    <React.Fragment key={index}>
      {line}
      <br />
    </React.Fragment>
  ));

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Cover Letter
      </Typography>
      <Box sx={{ p: 2, backgroundColor: '#f9f9f9', borderRadius: 1 }}>
        <Typography variant="body1" component="div">
          {formattedText}
        </Typography>
      </Box>
    </Paper>
  );
};

export default CoverLetterViewer;
