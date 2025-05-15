import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip,
  CircularProgress,
  InputAdornment,
  Snackbar,
  Alert,
  Divider
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import SupervisorAccountIcon from '@mui/icons-material/SupervisorAccount';
import api from '../../services/api';

const UserManagement = () => {
  // Users data
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // UI State for dialogs
  const [userDialog, setUserDialog] = useState({
    open: false,
    mode: 'create', // 'create' or 'edit'
    userData: {
      id: '',
      username: '',
      email: '',
      password: '',
      display_name: '',
      is_admin: false
    },
    showPassword: false,
    loading: false
  });
  
  const [confirmDialog, setConfirmDialog] = useState({
    open: false,
    userId: null,
    username: ''
  });
  
  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  // Load users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);
  
  // Filter users when search query changes
  useEffect(() => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const filtered = users.filter(user => 
        user.username.toLowerCase().includes(query) || 
        user.email.toLowerCase().includes(query) ||
        (user.display_name && user.display_name.toLowerCase().includes(query))
      );
      setFilteredUsers(filtered);
    } else {
      setFilteredUsers(users);
    }
  }, [searchQuery, users]);
  
  // Fetch users
  const fetchUsers = async () => {
    setLoading(true);
    
    try {
      const response = await api.get('/api/admin/users');
      if (response.data && response.data.users) {
        setUsers(response.data.users);
        setFilteredUsers(response.data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setSnackbar({
        open: true,
        message: 'Error loading users: ' + (error.response?.data?.error || error.message),
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Handle pagination changes
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // User dialog handlers
  const handleOpenCreateDialog = () => {
    setUserDialog({
      open: true,
      mode: 'create',
      userData: {
        id: '',
        username: '',
        email: '',
        password: '',
        display_name: '',
        is_admin: false
      },
      showPassword: false,
      loading: false
    });
  };
  
  const handleOpenEditDialog = (user) => {
    setUserDialog({
      open: true,
      mode: 'edit',
      userData: {
        id: user.id,
        username: user.username,
        email: user.email,
        password: '',
        display_name: user.display_name || '',
        is_admin: user.is_admin
      },
      showPassword: false,
      loading: false
    });
  };
  
  const handleCloseUserDialog = () => {
    setUserDialog({
      ...userDialog,
      open: false
    });
  };
  
  const handleUserDataChange = (e) => {
    const { name, value, checked, type } = e.target;
    
    setUserDialog(prev => ({
      ...prev,
      userData: {
        ...prev.userData,
        [name]: type === 'checkbox' ? checked : value
      }
    }));
  };
  
  const togglePasswordVisibility = () => {
    setUserDialog(prev => ({
      ...prev,
      showPassword: !prev.showPassword
    }));
  };
  
  // Save user (create or update)
  const handleSaveUser = async () => {
    // Validate form
    if (!userDialog.userData.username || !userDialog.userData.email) {
      setSnackbar({
        open: true,
        message: 'Username and email are required',
        severity: 'error'
      });
      return;
    }
    
    if (userDialog.mode === 'create' && !userDialog.userData.password) {
      setSnackbar({
        open: true,
        message: 'Password is required for new users',
        severity: 'error'
      });
      return;
    }
    
    setUserDialog({
      ...userDialog,
      loading: true
    });
    
    try {
      if (userDialog.mode === 'create') {
        // Create new user
        await api.post('/api/admin/users', userDialog.userData);
        
        setSnackbar({
          open: true,
          message: 'User created successfully',
          severity: 'success'
        });
      } else {
        // Update existing user
        await api.put(`/api/admin/users/${userDialog.userData.id}`, userDialog.userData);
        
        setSnackbar({
          open: true,
          message: 'User updated successfully',
          severity: 'success'
        });
      }
      
      // Refresh user list
      fetchUsers();
      
      // Close dialog
      handleCloseUserDialog();
    } catch (error) {
      console.error('Error saving user:', error);
      setSnackbar({
        open: true,
        message: 'Error saving user: ' + (error.response?.data?.error || error.message),
        severity: 'error'
      });
    } finally {
      setUserDialog({
        ...userDialog,
        loading: false
      });
    }
  };
  
  // Delete user dialog handlers
  const handleOpenDeleteDialog = (user) => {
    setConfirmDialog({
      open: true,
      userId: user.id,
      username: user.username
    });
  };
  
  const handleCloseDeleteDialog = () => {
    setConfirmDialog({
      ...confirmDialog,
      open: false
    });
  };
  
  // Delete user
  const handleDeleteUser = async () => {
    try {
      await api.delete(`/api/admin/users/${confirmDialog.userId}`);
      
      // Refresh user list
      fetchUsers();
      
      setSnackbar({
        open: true,
        message: 'User deleted successfully',
        severity: 'success'
      });
      
      handleCloseDeleteDialog();
    } catch (error) {
      console.error('Error deleting user:', error);
      setSnackbar({
        open: true,
        message: 'Error deleting user: ' + (error.response?.data?.error || error.message),
        severity: 'error'
      });
    }
  };
  
  // Handle search
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setPage(0); // Reset to first page when search changes
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Snackbar handler
  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };
  
  // Loading state
  if (loading && users.length === 0) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '80vh' 
      }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
          Loading Users...
        </Typography>
      </Box>
    );
  }
  
  return (
    <Container 
      maxWidth="lg"
      sx={{
        pb: { xs: 8, sm: 4 } // Add bottom padding for mobile navigation
      }}
    >
      <Box sx={{ my: { xs: 3, md: 4 } }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom 
          sx={{ 
            display: 'flex', 
            alignItems: 'center',
            fontSize: { xs: '1.75rem', sm: '2.125rem' },
            fontWeight: 'bold',
            color: 'primary.main',
            pb: 1,
            borderBottom: '2px solid',
            borderColor: 'primary.main',
            width: 'fit-content'
          }}
        >
          <PersonIcon sx={{ mr: 1.5, fontSize: { xs: '1.75rem', sm: '2.125rem' } }} /> 
          User Management
        </Typography>
        
        <Paper 
          sx={{ 
            mt: 3, 
            p: { xs: 2, sm: 3 },
            borderRadius: 2,
            boxShadow: 3
          }}
        >
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'stretch', sm: 'center' },
            mb: 3,
            gap: 2
          }}>
            <TextField
              placeholder="Search users..."
              variant="outlined"
              value={searchQuery}
              onChange={handleSearchChange}
              sx={{ flexGrow: 1, maxWidth: { sm: 400 } }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleOpenCreateDialog}
              sx={{ 
                py: 1.5,
                px: 3,
                fontWeight: 'medium',
                borderRadius: 1,
                boxShadow: 2,
                '&:hover': {
                  boxShadow: 4
                } 
              }}
            >
              Add User
            </Button>
          </Box>
          
          <TableContainer
            sx={{
              borderRadius: 1,
              '& .MuiTableCell-head': {
                fontWeight: 'bold',
                backgroundColor: (theme) => theme.palette.action.hover
              }
            }}
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Display Name</TableCell>
                  <TableCell align="center">Type</TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Created</TableCell>
                  <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>Last Login</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredUsers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                      {searchQuery ? 'No users found matching your search criteria' : 'No users found'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredUsers
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((user) => (
                      <TableRow 
                        key={user.id}
                        sx={{
                          '&:hover': {
                            backgroundColor: (theme) => theme.palette.action.hover
                          }
                        }}
                      >
                        <TableCell sx={{ fontWeight: 'medium' }}>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>
                          {user.display_name || '-'}
                        </TableCell>
                        <TableCell align="center">
                          <Chip 
                            label={user.is_admin ? "Admin" : "User"} 
                            color={user.is_admin ? "primary" : "default"}
                            size="small"
                            sx={{ fontWeight: 'medium' }}
                            icon={user.is_admin ? <SupervisorAccountIcon /> : <PersonIcon />}
                          />
                        </TableCell>
                        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                          {formatDate(user.created_at)}
                        </TableCell>
                        <TableCell sx={{ display: { xs: 'none', md: 'table-cell' } }}>
                          {formatDate(user.last_login)}
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                            <Tooltip title="Edit User">
                              <IconButton 
                                color="primary" 
                                onClick={() => handleOpenEditDialog(user)}
                                size="small"
                              >
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                            
                            <Tooltip title="Delete User">
                              <IconButton 
                                color="error" 
                                onClick={() => handleOpenDeleteDialog(user)}
                                size="small"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={filteredUsers.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      </Box>
      
      {/* Create/Edit User Dialog */}
      <Dialog 
        open={userDialog.open} 
        onClose={handleCloseUserDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: 24
          }
        }}
      >
        <DialogTitle 
          sx={{ 
            backgroundColor: userDialog.mode === 'create' ? 'primary.main' : 'info.main',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            p: 2
          }}
        >
          <PersonIcon sx={{ mr: 1 }} />
          {userDialog.mode === 'create' ? 'Add New User' : 'Edit User'}
        </DialogTitle>
        
        <DialogContent sx={{ p: 3, pt: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={userDialog.userData.username}
                onChange={handleUserDataChange}
                variant="outlined"
                margin="normal"
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Display Name"
                name="display_name"
                value={userDialog.userData.display_name}
                onChange={handleUserDataChange}
                variant="outlined"
                margin="normal"
                helperText="Optional"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={userDialog.userData.email}
                onChange={handleUserDataChange}
                variant="outlined"
                margin="normal"
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={userDialog.mode === 'create' ? 'Password' : 'New Password (leave blank to keep current)'}
                name="password"
                type={userDialog.showPassword ? 'text' : 'password'}
                value={userDialog.userData.password}
                onChange={handleUserDataChange}
                variant="outlined"
                margin="normal"
                required={userDialog.mode === 'create'}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={togglePasswordVisibility}
                        edge="end"
                      >
                        {userDialog.showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={userDialog.userData.is_admin}
                    onChange={handleUserDataChange}
                    name="is_admin"
                    color="primary"
                  />
                }
                label="Admin User"
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <Divider />
        
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button 
            onClick={handleCloseUserDialog}
            variant="outlined"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSaveUser}
            variant="contained" 
            color={userDialog.mode === 'create' ? 'primary' : 'info'}
            disabled={
              !userDialog.userData.username || 
              !userDialog.userData.email || 
              (userDialog.mode === 'create' && !userDialog.userData.password) ||
              userDialog.loading
            }
            startIcon={userDialog.loading ? <CircularProgress size={20} /> : null}
          >
            {userDialog.loading ? 'Saving...' : userDialog.mode === 'create' ? 'Create User' : 'Update User'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={handleCloseDeleteDialog}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: 24
          }
        }}
      >
        <DialogTitle 
          sx={{ 
            backgroundColor: 'error.main',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            p: 2
          }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Confirm Delete
        </DialogTitle>
        
        <DialogContent sx={{ pt: 3, px: 3 }}>
          <DialogContentText>
            Are you sure you want to delete user <strong>{confirmDialog.username}</strong>? 
            This action cannot be undone and will remove all associated data.
          </DialogContentText>
        </DialogContent>
        
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button 
            onClick={handleCloseDeleteDialog}
            variant="outlined"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteUser}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Delete User
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default UserManagement;