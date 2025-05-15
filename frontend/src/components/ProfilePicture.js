import React, { useState, useRef } from 'react';
import { Avatar, IconButton, Badge, CircularProgress, Tooltip, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import AddAPhotoIcon from '@mui/icons-material/AddAPhoto';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../services/api';

// Styled components for the profile picture
const StyledBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    width: 32,
    height: 32,
    borderRadius: '50%',
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: theme.palette.primary.dark,
    },
  },
}));

const HiddenInput = styled('input')({
  display: 'none',
});

/**
 * ProfilePicture Component
 * 
 * @param {Object} props
 * @param {string} props.userId - User ID
 * @param {string} props.username - Username for the avatar letter
 * @param {string} props.pictureUrl - URL to the profile picture
 * @param {boolean} props.editable - Whether the user can edit the profile picture
 * @param {number} props.size - Size of the avatar (default: 40)
 * @param {function} props.onUpdate - Callback when the profile picture is updated
 */
const ProfilePicture = ({ 
  userId, 
  username = '', 
  pictureUrl,
  editable = false,
  size = 40,
  onUpdate
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [imageUrl, setImageUrl] = useState(pictureUrl);
  const fileInputRef = useRef(null);

  // Handle clicking the upload icon
  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Handle file selection
  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image file (JPEG, PNG, or GIF)');
      return;
    }

    // Check file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size should be less than 5MB');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/user/profile-picture', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data && response.data.profile_picture_url) {
        // Add a timestamp to force browser to reload the image
        const updatedUrl = response.data.profile_picture_url + '?t=' + new Date().getTime();
        setImageUrl(updatedUrl);
        if (onUpdate) {
          onUpdate(updatedUrl);
        }
      }
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      setError('Error uploading profile picture. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle delete profile picture
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to remove your profile picture?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await api.delete('/api/user/profile-picture');
      if (response.data && response.data.profile_picture_url) {
        setImageUrl(response.data.profile_picture_url);
        if (onUpdate) {
          onUpdate(response.data.profile_picture_url);
        }
      }
    } catch (error) {
      console.error('Error deleting profile picture:', error);
      setError('Error deleting profile picture');
    } finally {
      setLoading(false);
    }
  };

  // Determine avatar source and fallback
  const getAvatarContent = () => {
    if (loading) {
      return <CircularProgress size={size * 0.7} />;
    }
    
    // If we have a valid image URL (not the default one)
    if (imageUrl && !imageUrl.includes('default-profile.png')) {
      return null; // Will use the src prop
    }
    
    // Fallback to first letter of username
    return username ? username.charAt(0).toUpperCase() : 'U';
  };

  // Get proper avatar props based on the state
  const getAvatarProps = () => {
    const props = {
      sx: { 
        width: size, 
        height: size,
        bgcolor: 'secondary.main',
        fontSize: size / 2
      }
    };

    // Add src only if we have a real image URL
    if (imageUrl && !imageUrl.includes('default-profile.png')) {
      props.src = imageUrl;
      props.alt = username || 'User avatar';
    }

    return props;
  };

  // Render the final component
  if (!editable) {
    // Simple avatar for non-editable view
    return <Avatar {...getAvatarProps()}>{getAvatarContent()}</Avatar>;
  }

  // Editable version with upload badge
  return (
    <Box position="relative">
      <Tooltip title={error || ''} open={!!error} arrow placement="top">
        <StyledBadge
          overlap="circular"
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          badgeContent={
            <IconButton 
              size="small" 
              onClick={handleUploadClick} 
              disabled={loading}
              sx={{ p: 0 }}
            >
              <AddAPhotoIcon fontSize="small" />
            </IconButton>
          }
        >
          <Avatar {...getAvatarProps()}>{getAvatarContent()}</Avatar>
        </StyledBadge>
      </Tooltip>
      
      {/* Hidden file input */}
      <HiddenInput
        ref={fileInputRef}
        accept="image/jpeg,image/png,image/gif"
        type="file"
        onChange={handleFileSelect}
      />
      
      {/* Delete button (only shown when has custom profile picture) */}
      {imageUrl && !imageUrl.includes('default-profile.png') && (
        <IconButton 
          size="small" 
          onClick={handleDelete}
          disabled={loading}
          sx={{ 
            position: 'absolute',
            top: -8,
            right: -8,
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
            },
            width: 24,
            height: 24
          }}
        >
          <DeleteIcon fontSize="small" color="error" sx={{ fontSize: 16 }} />
        </IconButton>
      )}
    </Box>
  );
};

export default ProfilePicture;