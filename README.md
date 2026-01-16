# Create Is - The Ultimate Media Organizer

Create Is is the ultimate tool for renaming and organizing your movies, TV shows, and Anime. Match and rename media files against online databases, download artwork and cover images, fetch subtitles, write metadata, and more, all at once in matter of seconds. It's smart and just works.

## Features

- **Database Integration**: Match media files against TheMovieDB, TVDB, and AniList
- **Smart Renaming**: Automatically rename files based on database information
- **Artwork Downloading**: Download posters, backdrops, and fanart for movies and TV shows
- **Batch Processing**: Process entire directories with progress indicators
- **Metadata Writing**: Fetch and write metadata to media files
- **Subtitle Support**: Automatic subtitle downloading (planned)
- **Plex Compatibility**: Sanitize filenames for Plex media servers

## Installation

No installation required. Just download the script and run it with Python 3.

```bash
# Make sure you have Python 3 installed
python --version

# Install required dependencies (if needed)
pip install requests
```

## Usage

### Basic Usage

```bash
# Process a single file
python create_is.py movie.mp4

# Process a directory (recursively)
python create_is.py -d /path/to/media/directory

# Preview changes without actually renaming files
python create_is.py -d /path/to/media/directory --dry-run

# Process directory without recursion
python create_is.py -d /path/to/media/directory --no-recursive
```

### Advanced Usage

```bash
# Process with specific API key
python create_is.py -d /path/to/media/directory --api-key YOUR_TMDB_API_KEY

# Preview changes in a specific directory
python create_is.py -d /media/videos --dry-run
```

## How It Works

Create Is works by:

1. **Matching**: Extracts title and year from filenames, then searches online databases (TheMovieDB, TVDB, AniList) to find matching media
2. **Renaming**: Automatically renames files using standardized formats (e.g., "Movie.Title.2023.mp4")
3. **Artwork**: Downloads posters and backdrops for movies and TV shows
4. **Organization**: Processes entire directories recursively with progress indicators

## Requirements

- Python 3.x
- `requests` library (install with `pip install requests`)
- Internet connection for database access

## API Keys

To use Create Is effectively, you can obtain a free API key from [TheMovieDB](https://www.themoviedb.org/settings/api) and set it as an environment variable:

```bash
# Set the API key as an environment variable
export TMDB_API_KEY="your_api_key_here"

# Or pass it directly to the script
python create_is.py -d /path/to/media --api-key your_api_key_here
```

## Examples

### Process a single file:
```bash
python create_is.py "The Matrix [1999].mp4"
```

### Process a directory recursively:
```bash
python create_is.py -d "/home/user/Media/Movies"
```

### Preview changes without renaming:
```bash
python create_is.py -d "/home/user/Media/TV" --dry-run
```

## Logging

Create Is generates a log file `create_is.log` with detailed information about its operations.

## License

MIT
