import React from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  List, 
  ListItem, 
  ListItemText,
  Divider,
  Chip,
  Stack
} from '@mui/material';

const ResumeViewer = ({ resumeData }) => {
  if (!resumeData) {
    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6">No resume data available</Typography>
        <Typography>Please upload your resume first</Typography>
      </Paper>
    );
  }

  const { contact_info, education, experience, skills } = resumeData;
  
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h4" gutterBottom>
        {contact_info?.name || 'Your Resume'}
      </Typography>
      
      {/* Contact Information */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Contact Information
        </Typography>
        <Typography>
          {contact_info?.email && `Email: ${contact_info.email}`}
        </Typography>
        <Typography>
          {contact_info?.phone && `Phone: ${contact_info.phone}`}
        </Typography>
      </Box>
      
      {/* Skills */}
      {skills && skills.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Skills
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {skills.map((skill, index) => (
              <Chip 
                key={index} 
                label={skill} 
                variant="outlined" 
                sx={{ mb: 1 }}
              />
            ))}
          </Stack>
        </Box>
      )}
      
      {/* Experience */}
      {experience && experience.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Experience
          </Typography>
          <List>
            {experience.map((exp, index) => (
              <React.Fragment key={index}>
                <ListItem alignItems="flex-start" sx={{ display: 'block' }}>
                  <ListItemText
                    primary={exp}
                    secondary={' '}
                  />
                </ListItem>
                {index < experience.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Box>
      )}
      
      {/* Education */}
      {education && education.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Education
          </Typography>
          <List>
            {education.map((edu, index) => (
              <React.Fragment key={index}>
                <ListItem alignItems="flex-start" sx={{ display: 'block' }}>
                  <ListItemText
                    primary={edu}
                    secondary={' '}
                  />
                </ListItem>
                {index < education.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default ResumeViewer;
