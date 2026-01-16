#!/usr/bin/env python3
"""
Create Is - The Ultimate Media Organizer
========================================
A powerful tool for renaming and organizing movies, TV shows, and Anime.
This script uses TMDB and AniList APIs to find metadata for media files
and rename them according to standardized naming conventions.
"""

import os
import sys
import argparse
import requests
import logging
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('create_is.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MediaOrganizer:
    """Handles media file organization using TMDB and AniList APIs."""
    
    def __init__(self, api_key: str = ""):
        """Initialize the Media Organizer with an API key for TMDB.
        
        Args:
            api_key (str): The TMDB API key. If empty, tries to get from environment variable.
        """
        self.api_key = api_key or os.getenv('TMDB_API_KEY')
        self.base_url = "https://api.themoviedb.org/3"
        self.anilist_base_url = "https://graphql.anilist.co"
        
        self.session = requests.Session()
        if self.api_key:
            self.session.params = {'api_key': self.api_key}
            
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'CreateIs/1.0'
        }
        self.cache = {}

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """Search for a movie on TMDB by title and optional year.
        
        Args:
            title (str): The movie title to search for
            year (Optional[int]): The release year of the movie
            
        Returns:
            Optional[Dict]: Movie information from TMDB or None if not found
        """
        cache_key = f"movie_{title}_{year}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            params = {'query': title}
            if year:
                params['release_year'] = str(year)
                
            response = self.session.get(f"{self.base_url}/search/movie", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                self.cache[cache_key] = result
                return result
        except Exception as e:
            logger.error(f"Error searching for movie '{title}': {e}")
        return None

    def search_tv_show(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """Search for a TV show on TMDB by title and optional year.
        
        Args:
            title (str): The TV show title to search for
            year (Optional[int]): The release year of the show
            
        Returns:
            Optional[Dict]: TV show information from TMDB or None if not found
        """
        cache_key = f"tv_{title}_{year}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            params = {'query': title}
            if year:
                params['first_air_date_year'] = str(year)
                
            response = self.session.get(f"{self.base_url}/search/tv", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                self.cache[cache_key] = result
                return result
        except Exception as e:
            logger.error(f"Error searching for TV show '{title}': {e}")
        return None

    def search_anime(self, title: str) -> Optional[Dict]:
        """Search for an anime on AniList by title.
        
        Args:
            title (str): The anime title to search for
            
        Returns:
            Optional[Dict]: Anime information from AniList or None if not found
        """
        cache_key = f"anime_{title}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        query = """
        query ($search: String) {
            Page(perPage: 1) {
                media(search: $search, type: ANIME) {
                    id
                    title { romaji english }
                    startDate { year }
                    coverImage { large }
                    bannerImage
                }
            }
        }
        """
        try:
            response = self.session.post(
                self.anilist_base_url,
                json={'query': query, 'variables': {'search': title}},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            # AniList returns a list under Page -> media
            media_list = data.get('data', {}).get('Page', {}).get('media', [])
            if media_list:
                result = media_list[0]
                self.cache[cache_key] = result
                return result
        except Exception as e:
            logger.error(f"Error searching for anime '{title}': {e}")
        return None

    def extract_title_year(self, filename: str) -> Tuple[str, Optional[int]]:
        """Extract title and year from a filename using regex patterns.
        
        Args:
            filename (str): The filename to process
            
        Returns:
            Tuple[str, Optional[int]]: A tuple of (title, year) where year may be None
        """
        stem = Path(filename).stem
        # Improved regex to find 4-digit years in brackets, parens, or separated by dots
        year_pattern = r'[\(\.\[ ](19|20)\d{2}[\)\.\] ]'
        match = re.search(year_pattern, stem)
        
        if match:
            year_str = re.search(r'\d{4}', match.group()).group() # pyright: ignore[reportOptionalMemberAccess]
            year = int(year_str)
            # Fix: Extract title properly by excluding the matched year part
            title_start = match.start()
            title_end = match.end()
            # Remove the matched year part from the stem to get clean title
            title = stem[:title_start] + stem[title_end:]
            title = title.replace('.', ' ').strip()
            return title, year
        
        return stem.replace('.', ' ').strip(), None

    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from a filename.
        
        Args:
            filename (str): The filename to sanitize
            
        Returns:
            str: A sanitized version of the filename
        """
        return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

    def format_movie_filename(self, movie_info: Dict, original_ext: str) -> str:
        """Format a movie filename with standardized naming convention.
        
        Args:
            movie_info (Dict): Movie information from TMDB
            original_ext (str): The original file extension
            
        Returns:
            str: Formatted filename with title and year
        """
        title = movie_info.get('title', 'Unknown')
        year = movie_info.get('release_date', '0000')[:4]
        safe_title = self.sanitize_filename(title)
        return f"{safe_title} ({year}){original_ext}"

    def download_artwork(self, url: str, save_path: Path):
        """Download artwork from a URL and save it to disk.
        
        Args:
            url (str): The URL of the artwork to download
            save_path (Path): The path where the artwork should be saved
        """
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            save_path.write_bytes(res.content)
            logger.info(f"Saved artwork: {save_path.name}")
        except Exception as e:
            logger.error(f"Artwork failed: {e}")

    def process_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """Process a single media file by renaming it with metadata.
        
        Args:
            file_path (Path): The path to the media file
            dry_run (bool): If True, only print what would be done without actually renaming
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            title, year = self.extract_title_year(file_path.name)
            ext = file_path.suffix
            
            # Search Logic
            movie = self.search_movie(title, year)
            if movie:
                new_name = self.format_movie_filename(movie, ext)
            else:
                # Fallback or TV logic
                tv = self.search_tv_show(title, year)
                if tv:
                    new_name = f"{self.sanitize_filename(tv['name'])} - S01E01{ext}"
                else:
                    logger.info(f"No match for {file_path.name}")
                    return False

            new_path = file_path.parent / new_name
            if dry_run:
                print(f"[DRY RUN] Rename: {file_path.name} -> {new_name}")
                return True

            if not new_path.exists():
                file_path.rename(new_path)
                logger.info(f"Renamed: {new_name}")
                return True
        except Exception as e:
            logger.error(f"Error: {e}")
        return False

    def process_directory(self, path: Path, dry_run: bool, recursive: bool):
        """Process all media files in a directory recursively.
        
        Args:
            path (Path): The directory to process
            dry_run (bool): If True, only print what would be done without actually renaming
            recursive (bool): If True, process subdirectories recursively
        """
        exts = {'.mp4', '.mkv', '.avi', '.mov'}
        files = []
        pattern = "**/*" if recursive else "*"
        for f in path.glob(pattern):
            if f.is_file() and f.suffix.lower() in exts:
                files.append(f)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(lambda f: self.process_file(f, dry_run), files))

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Media Organizer")
    parser.add_argument('input', help='Path to file or folder')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--api-key', help='TMDB API Key')
    args = parser.parse_args()

    organizer = MediaOrganizer(api_key=args.api_key)
    path = Path(args.input)

    if path.is_file():
        organizer.process_file(path, args.dry_run)
    elif path.is_dir():
        organizer.process_directory(path, args.dry_run, recursive=True)

if __name__ == "__main__":
    main()
