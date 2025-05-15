import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Box, 
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';
import SettingsIcon from '@mui/icons-material/Settings';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';

const AdminDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    users: 0,
    applications: 0,
    activeUsers: 0
  });
  const [recentUsers, setRecentUsers] = useState([]);
  
  useEffect(() => {
    // In a real implementation, these would be API calls
    // Simulating API calls with setTimeout
    setTimeout(() => {
      setStats({
        users: 28,
        applications: 143,
        activeUsers: 15
      });
      
      setRecentUsers([
        { id: 1, username: 'user1', email: 'user1@example.com', lastLogin: '2023-05-14T15:30:45Z', applications: 12 },
        { id: 2, username: 'user2', email: 'user2@example.com', lastLogin: '2023-05-14T14:25:12Z', applications: 8 },
        { id: 3, username: 'user3', email: 'user3@example.com', lastLogin: '2023-05-14T10:15:33Z', applications: 4 },
        { id: 4, username: 'user4', email: 'user4@example.com', lastLogin: '2023-05-13T22:45:18Z', applications: 23 },
        { id: 5, username: 'user5', email: 'user5@example.com', lastLogin: '2023-05-13T18:10:05Z', applications: 0 }
      ]);
      
      setLoading(false);
    }, 1000);
  }, []);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <SupervisorAccountIcon sx={{ mr: 1 }} /> Admin Dashboard
        </Typography>
        
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {/* Stats Cards */}
          <Grid item xs={12} sm={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon sx={{ mr: 1 }} /> Users
                </Typography>
                <Typography variant="h3">{stats.users}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total registered users
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <BusinessCenterIcon sx={{ mr: 1 }} /> Applications
                </Typography>
                <Typography variant="h3">{stats.applications}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total job applications submitted
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon sx={{ mr: 1 }} /> Active Users
                </Typography>
                <Typography variant="h3">{stats.activeUsers}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Users active in the last 24 hours
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Recent Users Table */}
          <Grid item xs={12} sx={{ mt: 2 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Users
              </Typography>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Username</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Last Login</TableCell>
                      <TableCell>Applications</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{formatDate(user.lastLogin)}</TableCell>
                        <TableCell>{user.applications}</TableCell>
                        <TableCell>
                          <Button 
                            startIcon={<SettingsIcon />} 
                            size="small" 
                            variant="outlined"
                          >
                            Manage
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          
          {/* Admin Actions */}
          <Grid item xs={12} sx={{ mt: 2 }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Admin Actions
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Button variant="contained">View All Users</Button>
                <Button variant="contained">Application Reports</Button>
                <Button variant="contained">System Settings</Button>
                <Button variant="contained" color="secondary">Maintenance Mode</Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default AdminDashboard;