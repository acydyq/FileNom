import os
import re
import sqlite3
import requests
import urllib.parse
from pathlib import Path
from config import load_config

# Load API Keys
config = load_config()
TMDB_API_KEY = config.get("tmdb_api_key", "")
SIMKL_API_KEY = config.get("simkl_api_key", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
SIMKL_BASE_URL = "https://api.simkl.com"

DB_PATH = "renaming_history.db"

def setup_database():
    """Initialize the SQLite database to track renamed files."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS renaming_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_filename TEXT NOT NULL,
            new_filename TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

setup_database()

def clean_filename(filename):
    """
    Remove unnecessary details like uploader names, codecs, resolution, and extra symbols.
    """
    original_filename = filename  # Save original for comparison

    patterns = [
        r"\[.*?\]",           # Remove anything in brackets [YIFY], [BluRay]
        r"\(.*?\)",           # Remove anything in parentheses (YTS)
        r"[-_.]?(1080p|720p|480p|2160p|4K|BluRay|WEBRip|WEB|x264|x265|HEVC|H.264|H.265|AAC|DDP5\.1|DTS|HDR|HDTV|DVDRip|BRRip)",  # Remove resolution & codecs
        r"-[A-Za-z0-9]+$",    # Remove release group at the end (-YIFY, -NTb)
    ]

    for pattern in patterns:
        filename = re.sub(pattern, "", filename, flags=re.IGNORECASE)

    # Replace multiple spaces with a single space
    filename = re.sub(r"\s+", " ", filename).strip()

    # If filename changed, force rename
    return filename, filename != original_filename

def extract_info(filename):
    """
    Extracts TV show or movie details from filename, including episode title if available.
    Returns: (title, year, season, episode, episode_title)
    """
    cleaned_filename, _ = clean_filename(filename)

    # Regex for TV Shows (e.g., S02E05 or 02x05)
    tv_pattern = re.compile(
        r'(?P<title>.+?)\s(?:-|\.|_)?\s?(S(?P<season>\d{1,2})E(?P<episode>\d{1,2})|\b(?P<season_alt>\d{1,2})x(?P<episode_alt>\d{1,2})\b)(?:\s-\s(?P<episode_title>.+?))?',
        re.IGNORECASE
    )

    # Regex for Movies (Handles missing years)
    movie_pattern = re.compile(
        r'(?P<title>.+?)(?:\s(?P<year>\d{4}))?\s?(?:\[\d{3,4}p\])?$',
        re.IGNORECASE
    )

    tv_match = tv_pattern.search(cleaned_filename)
    movie_match = movie_pattern.search(cleaned_filename)

    if tv_match:
        title = tv_match.group("title").strip()
        season = tv_match.group("season") or tv_match.group("season_alt")
        episode = tv_match.group("episode") or tv_match.group("episode_alt")
        episode_title = tv_match.group("episode_title")

        # Ensure episode title is cleaned
        if episode_title:
            episode_title = clean_filename(episode_title)[0]

        # Make sure title is not empty
        if not title or title == "-":
            title = "Unknown Show"

        print(f"📺 Extracted TV Show: {title} - S{season}E{episode} {('- ' + episode_title) if episode_title else ''}")
        return title, None, season, episode, episode_title  # TV Show format

    if movie_match:
        title = movie_match.group("title").strip()
        year = movie_match.group("year")
        print(f"🎬 Extracted Movie: {title} ({year if year else 'Unknown Year'})")
        return title, int(year) if year else None, None, None, None  # Movie format

    print(f"⚠️ No match found for: {filename}")
    return None, None, None, None, None  # No match

def rename_file(file_path):
    """Rename file based on metadata and clean unnecessary details."""
    file_path = Path(file_path)
    original_filename = file_path.stem
    file_extension = file_path.suffix

    # Extract info from filename
    title, year, season, episode, episode_title = extract_info(original_filename)
    
    if not title:
        print(f"❌ Could not extract title from: {file_path.name}")
        return False

    # Clean filename (force renaming if changes)
    cleaned_title, needs_rename = clean_filename(title)

    # Generate new filename
    if season and episode:
        if episode_title:
            new_filename = f"{cleaned_title} - S{season}E{episode} - {episode_title}{file_extension}"
        else:
            new_filename = f"{cleaned_title} - S{season}E{episode}{file_extension}"
    else:
        new_filename = f"{cleaned_title} ({year}){file_extension}" if year else f"{cleaned_title}{file_extension}"

    new_path = file_path.parent / new_filename

    # ✅ **Force rename if filename changed**
    if needs_rename or new_path.name != file_path.name:
        try:
            os.rename(file_path, new_path)
            print(f"✅ Renamed: {file_path.name} → {new_filename}")
            return True
        except Exception as e:
            print(f"⚠️ Error renaming {file_path.name}: {e}")
            return False
    else:
        print(f"⚠️ Skipping: {file_path.name} (already correct)")
        return False
