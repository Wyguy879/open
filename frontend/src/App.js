import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  TextField,
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  CardHeader,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import { UploadFile as UploadIcon, Settings as SettingsIcon } from '@mui/icons-material';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedDirectory, setSelectedDirectory] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [dryRun, setDryRun] = useState(false);
  const [recursive, setRecursive] = useState(true);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleDirectoryChange = (event) => {
    setSelectedDirectory(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!selectedFile && !selectedDirectory) {
      setError('Please select a file or directory');
      return;
    }
    
    setIsProcessing(true);
    setError('');
    
    try {
      // In a real app, this would call your Python backend
      // For now, we'll simulate processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setResults({
        processed: selectedFile ? 1 : Math.floor(Math.random() * 50) + 1,
        errors: 0,
        status: 'success'
      });
    } catch (err) {
      setError('Failed to process files');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Create Is - Media Organizer
        </Typography>
        
        <Card sx={{ mb: 3 }}>
          <CardHeader 
            title="Media Processing" 
            subheader="Rename and organize your movies, TV shows, and Anime"
            action={<SettingsIcon />}
          />
          <CardContent>
            <form onSubmit={handleSubmit}>
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="File or Directory Path"
                  variant="outlined"
                  value={selectedDirectory}
                  onChange={handleDirectoryChange}
                  InputProps={{
                    inputProps: {
                      accept: '.mp4,.mkv,.avi,.mov'
                    }
                  }}
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <input
                  accept="*"
                  style={{ display: 'none' }}
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                />
                <label htmlFor="file-upload">
                  <Button variant="contained" component="span" startIcon={<UploadIcon />}>
                    {selectedFile ? selectedFile.name : 'Select File'}
                  </Button>
                </label>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={dryRun} 
                      onChange={(e) => setDryRun(e.target.checked)} 
                    />
                  }
                  label="Dry Run (Preview Changes)"
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={recursive} 
                      onChange={(e) => setRecursive(e.target.checked)} 
                    />
                  }
                  label="Recursive Processing"
                />
              </Box>
              
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              
              <Button
                type="submit"
                variant="contained"
                disabled={isProcessing}
                startIcon={isProcessing ? <CircularProgress size={16} /> : null}
              >
                {isProcessing ? 'Processing...' : 'Start Processing'}
              </Button>
            </form>
          </CardContent>
        </Card>
        
        {results && (
          <Card>
            <CardHeader title="Processing Results" />
            <CardContent>
              <Typography variant="body1">
                Processed: {results.processed} files
              </Typography>
              <Typography variant="body1">
                Errors: {results.errors}
              </Typography>
              <Typography variant="body1">
                Status: {results.status}
              </Typography>
            </CardContent>
          </Card>
        )}
        
        <Divider sx={{ my: 3 }} />
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Features
          </Typography>
          <ul style={{ textAlign: 'left', margin: '0 auto', maxWidth: '600px' }}>
            <li>Database Integration: Match media files against TheMovieDB, TVDB, and AniList</li>
            <li>Smart Renaming: Automatically rename files based on database information</li>
            <li>Artwork Downloading: Download posters, backdrops, and fanart for movies and TV shows</li>
            <li>Batch Processing: Process entire directories with progress indicators</li>
            <li>Metadata Writing: Fetch and write metadata to media files</li>
            <li>Plex Compatibility: Sanitize filenames for Plex media servers</li>
          </ul>
        </Box>
      </Box>
    </Container>
  );
}

export default App;
