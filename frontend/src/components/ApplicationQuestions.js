import React, { useState } from 'react';
import { 
  Paper, 
  Typography, 
  Box, 
  TextField, 
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const ApplicationQuestions = ({ applicationAnswers, onUpdateAnswers }) => {
  const [customAnswers, setCustomAnswers] = useState({});
  const [expanded, setExpanded] = useState(false);

  const handleAnswerChange = (question, answer) => {
    const updatedAnswers = { ...customAnswers, [question]: answer };
    setCustomAnswers(updatedAnswers);
    onUpdateAnswers(updatedAnswers);
  };

  if (!applicationAnswers || Object.keys(applicationAnswers).length === 0) {
    return (
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6">No application answers available</Typography>
        <Typography>Generate application answers first</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Application Questions & Answers
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="body1" gutterBottom>
          Review and edit the AI-generated answers for common application questions.
        </Typography>
      </Box>
      
      <List>
        {Object.entries(applicationAnswers).map(([question, answer], index) => (
          <ListItem key={index} sx={{ display: 'block', pl: 0, pr: 0 }}>
            <Accordion 
              expanded={expanded === `panel${index}`}
              onChange={() => setExpanded(expanded === `panel${index}` ? false : `panel${index}`)}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls={`panel${index}-content`}
                id={`panel${index}-header`}
              >
                <Typography>{question}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  variant="outlined"
                  defaultValue={answer}
                  onChange={(e) => handleAnswerChange(question, e.target.value)}
                />
              </AccordionDetails>
            </Accordion>
          </ListItem>
        ))}
      </List>
      
      <Box sx={{ mt: 3 }}>
        <Button variant="contained" color="primary">
          Save All Answers
        </Button>
      </Box>
    </Paper>
  );
};

export default ApplicationQuestions;
