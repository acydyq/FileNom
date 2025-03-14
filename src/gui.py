import sys
import os
import json
import requests
import re
import unicodedata
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QListWidget, QLabel

# Load API keys from config.json
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        SIMKL_API_KEY = config.get("simkl_api_key", "")
        TMDB_API_KEY = config.get("tmdb_api_key", "")
else:
    SIMKL_API_KEY = ""
    TMDB_API_KEY = ""

def sanitize_filename(filename):
    """ Remove invalid characters and normalize for Windows compatibility. """
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, "", filename)  # Remove invalid characters
    filename = filename.replace("  ", " ").strip()  # Remove double spaces
    filename = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode("ascii")  # Remove accents
    return filename

def extract_show_info(filename):
    """ Extracts show name, season, and episode number from filename. """
    pattern = re.compile(r"(.*?)\s*[-.]\s*[Ss](\d{2})[Ee](\d{2})")
    match = pattern.search(filename)

    if match:
        show_name = match.group(1).replace(".", " ").strip()
        season = int(match.group(2))
        episode = int(match.group(3))
        return show_name, season, episode
    return None, None, None

def fetch_episode_title(show_name, season, episode):
    """ Fetches episode title from TMDB or SIMKL. """
    try:
        search_url = f"https://api.themoviedb.org/3/search/tv?query={show_name}&api_key={TMDB_API_KEY}"
        search_response = requests.get(search_url).json()

        if search_response.get("results"):
            show_id = search_response["results"][0]["id"]

            episode_url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{season}/episode/{episode}?api_key={TMDB_API_KEY}"
            episode_response = requests.get(episode_url).json()

            if "name" in episode_response:
                return episode_response["name"]

        simkl_url = f"https://api.simkl.com/tv/episodes/{show_name}/s{season:02}e{episode:02}?client_id={SIMKL_API_KEY}"
        simkl_response = requests.get(simkl_url).json()

        if "title" in simkl_response:
            return simkl_response["title"]

    except Exception as e:
        print(f"⚠️ Error fetching episode title: {e}")

    return None  # Return None if no title found

def rename_file(file_path):
    """ Renames file using extracted metadata. """
    directory, filename = os.path.split(file_path)
    clean_name = sanitize_filename(filename)

    show_name, season, episode = extract_show_info(clean_name)
    if not show_name or season is None or episode is None:
        print(f"⚠️ Skipping: {filename} (Could not extract show info)")
        return False

    episode_title = fetch_episode_title(show_name, season, episode)
    if not episode_title:
        episode_title = f"Episode {episode:02}"  # Fallback title

    new_filename = f"{show_name} - S{season:02}E{episode:02} - {sanitize_filename(episode_title)}.mkv"

    # Ensure Windows-compatible path
    new_path = os.path.join(directory, new_filename)
    if len(new_path) > 255:
        new_filename = f"{show_name} - S{season:02}E{episode:02}.mkv"  # Shorten long filenames
        new_path = os.path.join(directory, new_filename)

    if os.path.exists(new_path):
        print(f"⚠️ Skipping: {new_filename} (already correct)")
        return False

    os.rename(file_path, new_path)
    print(f"✅ Renamed: {filename} → {new_filename}")
    return True

class FileRenamerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("FileNom - TV Show Renamer")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Select TV show files or folders to rename:")
        layout.addWidget(self.label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.add_files_button = QPushButton("Add Files")
        self.add_files_button.clicked.connect(self.add_files)
        layout.addWidget(self.add_files_button)

        self.add_folder_button = QPushButton("Add Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        layout.addWidget(self.add_folder_button)

        self.rename_button = QPushButton("Rename Files")
        self.rename_button.clicked.connect(self.rename_files)
        layout.addWidget(self.rename_button)

        self.setLayout(layout)

    def add_files(self):
        """ Adds individual files to the renaming list. """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Video Files (*.mkv *.mp4 *.avi)")
        for file in files:
            self.file_list.addItem(file)

    def add_folder(self):
        """ Adds all supported video files from a selected folder. """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith((".mkv", ".mp4", ".avi")):
                        self.file_list.addItem(os.path.join(root, file))

    def rename_files(self):
        """ Processes all selected files and renames them. """
        for i in range(self.file_list.count()):
            file_path = self.file_list.item(i).text()
            rename_file(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    renamer = FileRenamerApp()
    renamer.show()
    sys.exit(app.exec_())
