#!/usr/bin/env python3
"""
Plex File Name Converter
========================

A tool to make filenames Plex-friendly by removing or replacing 
special characters that might cause issues in Plex media servers.

Features:
- Process individual files or entire directories recursively
- Remove/rename problematic characters for Plex compatibility
- Preserve file extensions
- Dry-run option to preview changes
"""

import os
import sys
import argparse
import re
from pathlib import Path


def sanitize_filename(filename):
    """
    Make a filename Plex-friendly by removing/replacing problematic characters.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: The sanitized filename
    """
    # Remove or replace Windows-invalid characters
    # These are characters that are not allowed in Windows file names
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    
    # Replace invalid characters with underscore
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots (Windows doesn't allow these)
    sanitized = sanitized.strip(' .')
    
    # Replace multiple consecutive underscores with a single underscore
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove trailing underscores
    sanitized = sanitized.rstrip('_')
    
    # Handle edge case of empty filename or just dots
    if not sanitized:
        return "unnamed_file"
        
    return sanitized


def process_file(file_path, dry_run=False):
    """
    Process a single file to make its name Plex-friendly.
    
    Args:
        file_path (Path): Path to the file
        dry_run (bool): If True, only show what would be changed
        
    Returns:
        bool: True if file was processed, False otherwise
    """
    original_name = file_path.name
    sanitized_name = sanitize_filename(original_name)
    
    # If names are the same, no processing needed
    if original_name == sanitized_name:
        return False
    
    if dry_run:
        print(f"Would rename: {original_name} -> {sanitized_name}")
        return True
    
    try:
        new_path = file_path.parent / sanitized_name
        os.rename(file_path, new_path)
        print(f"Renamed: {original_name} -> {sanitized_name}")
        return True
    except OSError as e:
        print(f"Error renaming {original_name}: {e}")
        return False


def process_directory(directory_path, dry_run=False, recursive=True):
    """
    Process all files in a directory to make their names Plex-friendly.
    
    Args:
        directory_path (Path): Path to the directory
        dry_run (bool): If True, only show what would be changed
        recursive (bool): If True, process subdirectories recursively
        
    Returns:
        tuple: (processed_count, error_count)
    """
    processed_count = 0
    error_count = 0
    
    try:
        # Get all files in the directory
        if recursive:
            # Process all files recursively
            for file_path in directory_path.rglob('*'):
                if file_path.is_file():
                    if process_file(file_path, dry_run):
                        processed_count += 1
        else:
            # Process only files in the specified directory (not subdirectories)
            for file_path in directory_path.iterdir():
                if file_path.is_file():
                    if process_file(file_path, dry_run):
                        processed_count += 1
                        
    except PermissionError:
        print(f"Permission denied accessing directory: {directory_path}")
        error_count += 1
    except OSError as e:
        print(f"Error processing directory {directory_path}: {e}")
        error_count += 1
    
    return processed_count, error_count


def main():
    """Main function to handle command-line arguments and process files."""
    parser = argparse.ArgumentParser(
        description="Make filenames Plex-friendly by removing/replacing problematic characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python plex_converter.py file.txt
  python plex_converter.py -d /path/to/directory
  python plex_converter.py -d /path/to/directory --dry-run
  python plex_converter.py -d /path/to/directory --no-recursive
        """
    )
    
    parser.add_argument('input', nargs='?', help='File or directory to process')
    parser.add_argument('-d', '--directory', help='Directory to process (alternative to positional argument)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without actually changing anything')
    parser.add_argument('--no-recursive', action='store_true', help='Do not process subdirectories recursively')
    
    args = parser.parse_args()
    
    # Determine input path
    if args.directory:
        input_path = Path(args.directory)
    elif args.input:
        input_path = Path(args.input)
    else:
        print("Error: No input specified. Use -d or specify a file/directory as argument.")
        parser.print_help()
        sys.exit(1)
    
    # Check if path exists
    if not input_path.exists():
        print(f"Error: Path does not exist: {input_path}")
        sys.exit(1)
    
    # Process based on whether it's a file or directory
    if input_path.is_file():
        print(f"Processing file: {input_path}")
        process_file(input_path, args.dry_run)
    elif input_path.is_dir():
        print(f"Processing directory: {input_path}")
        recursive = not args.no_recursive
        processed_count, error_count = process_directory(input_path, args.dry_run, recursive)
        if not args.dry_run:
            print(f"\nProcessed {processed_count} files. {error_count} errors occurred.")
    else:
        print(f"Error: Invalid path type: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
