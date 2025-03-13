import os
import re
import sqlite3
import requests
import urllib.parse
from pathlib import Path
from tvdb_api import Tvdb

# TMDb API Setup (Replace with your own API Key)
TMDB_API_KEY = "865235ff7997022ab64b1c540811d004"
TVDB_API_KEY = "78fd5c27-61cd-4a95-a862-d48c01598915"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TVDB_BASE_URL = "https://api.thetvdb.com"

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

def sanitize_filename(filename):
    """
    Removes invalid characters for Windows filenames.
    """
    return filename.replace(":", "").replace("/", "").replace("\\", "").strip()

def normalize_title(title):
    """
    Auto-corrects common TV show and movie title errors before searching.
    """
    corrections = {
        "Its Alway Sunny In Philadelphia": "It's Always Sunny in Philadelphia",
        "Amercan Horror Story": "American Horror Story",
        "Rick And Morty": "Rick and Morty",
        "The Office Us": "The Office (US)",
        "The Office Uk": "The Office (UK)",
        "Game Of Thrones": "Game of Thrones",
        "13 Hours Secret Soldiers Benghazi": "13 Hours: The Secret Soldiers of Benghazi",
    }
    return corrections.get(title, title)  # Return corrected title if found

def extract_info(filename):
    """
    Extracts TV show or movie details from filename.
    Returns: (title, year, season, episode)
    """
    clean_filename = filename.replace(".", " ").replace("_", " ").replace("-", " ").strip()

    # Improved regex for TV Shows (e.g., S02E05 or 02x05)
    tv_pattern = re.compile(r'(?P<title>.+?)[\s](S(?P<season>\d{1,2})E(?P<episode>\d{1,2})|\b(?P<season_alt>\d{1,2})x(?P<episode_alt>\d{1,2})\b)', re.IGNORECASE)
    
    # Improved regex for Movies (Handles missing years & multi-word titles)
    movie_pattern = re.compile(r'(?P<title>.+?)(?:\s(?P<year>\d{4}))?\s?(?:\[\d{3,4}p\])?$', re.IGNORECASE)

    tv_match = tv_pattern.search(clean_filename)
    movie_match = movie_pattern.search(clean_filename)

    if tv_match:
        title = tv_match.group("title").strip()
        season = tv_match.group("season") or tv_match.group("season_alt")
        episode = tv_match.group("episode") or tv_match.group("episode_alt")
        corrected_title = normalize_title(title)
        print(f"📺 Extracted TV Show: {corrected_title} - S{season}E{episode}")
        return corrected_title, None, season, episode  # TV Show format

    if movie_match:
        title = movie_match.group("title").strip()
        year = movie_match.group("year")
        corrected_title = normalize_title(title)
        print(f"🎬 Extracted Movie: {corrected_title} ({year if year else 'Unknown Year'})")
        return corrected_title, int(year) if year else None, None, None  # Movie format

    print(f"⚠️ No match found for: {filename}")
    return None, None, None, None  # No match

def fetch_metadata_tmdb(title, year=None, season=None, episode=None):
    """
    Queries TMDb for metadata.
    - If season/episode is provided, fetch as TV show.
    - Otherwise, fetch as a movie.
    """
    headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}

    title = title.title()  # Ensure correct capitalization
    encoded_title = urllib.parse.quote(title)

    if season and episode:
        search_url = f"https://api.themoviedb.org/3/search/tv?query={encoded_title}&api_key={TMDB_API_KEY}"
        print(f"🔍 Searching TMDb for TV Show: {search_url}")
        response = requests.get(search_url, headers=headers).json()

        if "results" in response and response["results"]:
            show_id = response["results"][0]["id"]
            episode_url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{season}/episode/{episode}?api_key={TMDB_API_KEY}"
            print(f"📡 Fetching episode: {episode_url}")
            episode_response = requests.get(episode_url, headers=headers).json()

            if "name" in episode_response:
                return {
                    "title": response["results"][0]["name"],
                    "season": season,
                    "episode": episode,
                    "episode_title": episode_response["name"],
                }

    else:
        search_url = f"https://api.themoviedb.org/3/search/movie?query={encoded_title}&year={year if year else ''}&api_key={TMDB_API_KEY}"
        print(f"🔍 Searching TMDb for Movie: {search_url}")
        response = requests.get(search_url, headers=headers).json()

        if "results" in response and response["results"]:
            movie = response["results"][0]
            return {
                "title": movie["title"],
                "year": movie["release_date"][:4] if "release_date" in movie else year,
            }

    print(f"❌ TMDb could not find: {title}")
    return None

def fetch_metadata(title, year=None, season=None, episode=None):
    """
    Uses TMDb for both movies and TV shows.
    """
    return fetch_metadata_tmdb(title, year, season, episode)

def format_new_filename(metadata, extension, is_tv_show):
    """
    Formats the new filename based on metadata.
    - TV Shows: "Show Name - SxxEyy - Episode Title.ext"
    - Movies: "Title (Year).ext"
    """
    if not metadata:
        return None

    new_filename = ""
    if is_tv_show:
        new_filename = f"{metadata['title']} - S{metadata['season']}E{metadata['episode']} - {metadata['episode_title']}{extension}"
    else:
        new_filename = f"{metadata['title']} ({metadata['year'] if metadata['year'] else 'Unknown Year'}){extension}"

    return sanitize_filename(new_filename)

def rename_file(file_path):
    """
    Main function to rename a file based on extracted metadata.
    """
    file_path = Path(file_path)
    original_filename = file_path.stem
    file_extension = file_path.suffix

    title, year, season, episode = extract_info(original_filename)
    
    if not title:
        print(f"❌ Could not extract title from: {file_path.name}")
        return False
    
    metadata = fetch_metadata(title, year, season, episode)
    
    if not metadata:
        print(f"❌ Skipping renaming for: {file_path.name}")
        return False
    
    new_filename = format_new_filename(metadata, file_extension, is_tv_show=(season is not None))
    
    if not new_filename:
        print(f"❌ Could not generate new filename for: {file_path.name}")
        return False

    new_path = file_path.parent / new_filename

    try:
        os.rename(file_path, new_path)
        print(f"✅ Renamed: {file_path.name} → {new_filename}")
        return True
    except Exception as e:
        print(f"⚠️ Error renaming {file_path.name}: {e}")
        return False
