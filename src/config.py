import json
import os
import requests

CONFIG_FILE = "config.json"
TMDB_API_BASE = "https://api.themoviedb.org/3"
SIMKL_API_BASE = "https://api.simkl.com"

def load_config():
    """Load API keys from config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"tmdb_api_key": "", "simkl_api_key": ""}

def save_config(tmdb_key, simkl_key):
    """Save API keys to config.json."""
    config = {"tmdb_api_key": tmdb_key, "simkl_api_key": simkl_key}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def validate_tmdb_key(tmdb_key):
    """Validate the TMDb API key by making a test request."""
    url = f"{TMDB_API_BASE}/movie/550?api_key={tmdb_key}"
    response = requests.get(url)
    return response.status_code == 200

def validate_simkl_key(simkl_key):
    """Validate the SIMKL API key by making a test request."""
    headers = {"simkl-api-key": simkl_key}
    response = requests.get(f"{SIMKL_API_BASE}/movies/trending", headers=headers)

    return response.status_code == 200
