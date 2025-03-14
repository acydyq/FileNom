import os
import re
import sqlite3
import requests
import urllib.parse
from pathlib import Path

# API Keys & Base URLs
from config import load_config

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

def fetch_metadata_simkl(title, season=None, episode=None):
    """Fetch metadata from SIMKL API."""
    headers = {"simkl-api-key": SIMKL_API_KEY}
    
    if season and episode:
        search_url = f"{SIMKL_BASE_URL}/search/tv?q={urllib.parse.quote(title)}"
    else:
        search_url = f"{SIMKL_BASE_URL}/search/movie?q={urllib.parse.quote(title)}"

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200 and "result" in response.json():
        result = response.json()["result"][0]  # Get first match
        return {
            "title": result.get("title"),
            "year": result.get("year"),
            "season": season,
            "episode": episode,
        }
    
    return None

def fetch_metadata(title, year=None, season=None, episode=None):
    """Try TMDb first, then use SIMKL if TMDb fails."""
    metadata = fetch_metadata_simkl(title, season, episode)
    
    if not metadata and TMDB_API_KEY:
        headers = {"Authorization": f"Bearer {TMDB_API_KEY}"}
        search_url = f"{TMDB_BASE_URL}/search/movie?query={urllib.parse.quote(title)}&year={year if year else ''}"
        response = requests.get(search_url, headers=headers)

        if "results" in response.json() and response.json()["results"]:
            movie = response.json()["results"][0]
            return {
                "title": movie["title"],
                "year": movie["release_date"][:4] if "release_date" in movie else year,
            }

    return metadata

def rename_file(file_path):
    """Rename file based on metadata."""
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

    new_filename = f"{metadata['title']} ({metadata['year']}){file_extension}"
    new_path = file_path.parent / new_filename

    try:
        os.rename(file_path, new_path)
        print(f"✅ Renamed: {file_path.name} → {new_filename}")
        return True
    except Exception as e:
        print(f"⚠️ Error renaming {file_path.name}: {e}")
        return False
