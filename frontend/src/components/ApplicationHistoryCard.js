import React from 'react';
import { 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Button, 
  Chip,
  Box,
  Stack 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const ApplicationHistoryCard = ({ application }) => {
  const navigate = useNavigate();
  
  // Determine status color
  const getStatusColor = (success) => {
    return success ? 'success' : 'error';
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h5" component="div" gutterBottom>
              {application.position || 'Job Position'}
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {application.company || 'Company'}
            </Typography>
          </Box>
          <Chip 
            icon={application.success ? <CheckCircleIcon /> : <ErrorIcon />}
            label={application.success ? 'Submitted' : 'Failed'}
            color={getStatusColor(application.success)}
          />
        </Box>
        
        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Application ID: {application.application_id || application.job_id}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {formatTimestamp(application.timestamp)}
          </Typography>
        </Stack>
        
        {application.message && (
          <Typography variant="body1">
            {application.message}
          </Typography>
        )}
        
        {application.error && (
          <Typography variant="body1" color="error">
            Error: {application.error}
          </Typography>
        )}
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => navigate(`/job/${application.job_id}`)}>
          View Job
        </Button>
        {application.success ? (
          <Button size="small" color="primary">
            Download Application
          </Button>
        ) : (
          <Button 
            size="small" 
            variant="contained" 
            color="primary"
            onClick={() => navigate(`/apply/${application.job_id}`)}
          >
            Try Again
          </Button>
        )}
      </CardActions>
    </Card>
  );
};

export default ApplicationHistoryCard;
