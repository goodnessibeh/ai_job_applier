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
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

const JobCard = ({ job }) => {
  const navigate = useNavigate();

  return (
    <Card sx={{ mb: 2, position: 'relative' }}>
      <CardContent>
        <Typography variant="h5" component="div" gutterBottom>
          {job.title}
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {job.company}
        </Typography>
        
        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <LocationOnIcon fontSize="small" sx={{ mr: 0.5 }} />
            <Typography variant="body2">{job.location}</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <WorkIcon fontSize="small" sx={{ mr: 0.5 }} />
            <Typography variant="body2">{job.job_type}</Typography>
          </Box>
          {job.salary && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AttachMoneyIcon fontSize="small" sx={{ mr: 0.5 }} />
              <Typography variant="body2">{job.salary}</Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccessTimeIcon fontSize="small" sx={{ mr: 0.5 }} />
            <Typography variant="body2">{job.posted_date}</Typography>
          </Box>
        </Stack>
        
        <Typography variant="body1" sx={{ mb: 2 }}>
          {job.description ? job.description.split('\n')[0] : 'No description available'}
        </Typography>
        
        <Box sx={{ position: 'absolute', top: 16, right: 16, display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Chip 
            label={job.source} 
            color="primary" 
            size="small" 
            variant="outlined" 
          />
          <Chip 
            label={job.is_demo ? "Demo" : "Real"} 
            color={job.is_demo ? "default" : "success"} 
            size="small" 
            variant={job.is_demo ? "outlined" : "filled"} 
          />
          {job.application_type && (
            <Chip 
              label={job.application_type === "easy_apply" ? "Easy Apply" : "External"} 
              color={job.application_type === "easy_apply" ? "info" : "warning"} 
              size="small" 
            />
          )}
          {job.applicationStatus && (
            <Chip 
              label={job.applicationStatus}
              color="success"
              size="small"
              sx={{ mt: 1 }}
            />
          )}
        </Box>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => navigate(`/job/${job.id}`)}>
          View Details
        </Button>
        <Button 
          size="small" 
          variant="contained" 
          color="primary"
          onClick={() => navigate(`/apply/${job.id}`)}
        >
          Apply Now
        </Button>
      </CardActions>
    </Card>
  );
};

export default JobCard;
