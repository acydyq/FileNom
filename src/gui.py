import sys
import os
import json
import requests
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QListWidget, QPushButton, QVBoxLayout, QWidget,
    QLabel, QHBoxLayout, QMessageBox, QLineEdit, QDialog, QFormLayout, QListWidgetItem
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

# Constants
CONFIG_FILE = "config.json"
DEFAULT_DIRECTORY = r"G:\My Drive\NZBGet"

# Settings Dialog Class
class SettingsDialog(QDialog):
    """Settings Dialog to input OMDB API key."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - OMDB API Key")
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # API Key Input
        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Enter OMDB API Key")
        self.form_layout.addRow("OMDB API Key:", self.api_key_input)

        # Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.save_button)

        # Load existing API key
        self.load_existing_key()

    def load_existing_key(self):
        """Load API Key from config if available."""
        config = self.load_config()
        if "OMDB_API_KEY" in config:
            self.api_key_input.setText(config["OMDB_API_KEY"])

    def save_settings(self):
        """Save API Key to config file."""
        api_key = self.api_key_input.text().strip()
        if api_key:
            config = {"OMDB_API_KEY": api_key}
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
            QMessageBox.information(self, "Saved", "OMDB API Key has been saved successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid OMDB API key.")

    @staticmethod
    def load_config():
        """Load configuration file."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

# Main Application Class
class FileNomApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FileNom - TV Show & Movie Renamer")
        self.setGeometry(200, 200, 800, 500)

        # Load API Key
        self.api_key = self.load_api_key()

        # Layouts
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Apply Dark Mode Styling
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: white; }
            QListWidget { background-color: #1e1e1e; color: white; }
            QPushButton { background-color: #444; color: white; padding: 6px; }
            QPushButton:hover { background-color: #666; }
        """)

        # File List Widgets (Dual Pane)
        self.file_list_original = QListWidget()
        self.file_list_preview = QListWidget()
        self.file_list_original.setDragDropMode(QListWidget.InternalMove)
        self.file_list_preview.setDragDropMode(QListWidget.InternalMove)

        # Labels
        self.label_original = QLabel("Original Files")
        self.label_preview = QLabel("Renamed Preview")

        # Buttons
        self.add_files_btn = QPushButton("Add Files")
        self.add_folder_btn = QPushButton("Add Folder")
        self.rename_btn = QPushButton("Rename Files")
        self.clear_btn = QPushButton("Clear List")
        self.settings_btn = QPushButton("Settings")

        # Layout Management
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.label_original)
        file_layout.addWidget(self.label_preview)

        list_layout = QHBoxLayout()
        list_layout.addWidget(self.file_list_original)
        list_layout.addWidget(self.file_list_preview)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_files_btn)
        btn_layout.addWidget(self.add_folder_btn)
        btn_layout.addWidget(self.rename_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.settings_btn)

        self.layout.addLayout(file_layout)
        self.layout.addLayout(list_layout)
        self.layout.addLayout(btn_layout)

        # Button Events
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.rename_btn.clicked.connect(self.rename_files)
        self.clear_btn.clicked.connect(self.clear_list)
        self.settings_btn.clicked.connect(self.open_settings)

        # Warn if API Key is missing
        if not self.api_key:
            QMessageBox.warning(self, "OMDB API Key Missing", "Please enter your OMDB API key in settings.")

    def load_api_key(self):
        """Load API Key from config file."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("OMDB_API_KEY", "")
        return ""

    def open_settings(self):
        """Open Settings Dialog."""
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.api_key = self.load_api_key()

    def rename_files(self):
        """Rename all files based on preview names."""
        for i in range(self.file_list_original.count()):
            original_path = self.file_list_original.item(i).text()
            new_name = self.file_list_preview.item(i).text()
            if original_path and new_name:
                try:
                    directory = os.path.dirname(original_path)
                    new_full_path = os.path.join(directory, new_name)
                    if os.path.exists(new_full_path):
                        QMessageBox.warning(self, "File Exists", f"Skipping: {new_name} already exists.")
                        continue
                    os.rename(original_path, new_full_path)
                    print(f"✅ Renamed: {original_path} → {new_full_path}")
                except Exception as e:
                    print(f"❌ Error renaming {original_path}: {e}")

    def add_files(self):
        """Allow users to add files."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Video Files", DEFAULT_DIRECTORY, "Video Files (*.mkv *.mp4 *.avi)")
        for file in files:
            self.add_to_list(file)

    def add_folder(self):
        """Allow users to add a folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", DEFAULT_DIRECTORY)
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith(('.mkv', '.mp4', '.avi')):
                        self.add_to_list(os.path.join(root, file))

    def add_to_list(self, file_path):
        """Adds files to the UI lists."""
        original_item = QListWidgetItem(file_path)
        self.file_list_original.addItem(original_item)

        preview_filename, color = self.get_preview_filename(file_path)
        preview_item = QListWidgetItem(preview_filename)
        preview_item.setForeground(QColor(color))
        self.file_list_preview.addItem(preview_item)

    def clear_list(self):
        """Clear all files from the UI."""
        self.file_list_original.clear()
        self.file_list_preview.clear()

    def parse_filename(self, filename):
        """Parse a filename to extract TV show or movie metadata."""
        name, ext = os.path.splitext(filename)
        name = re.sub(r'[._]', ' ', name)  # Replace dots and underscores with spaces

        # TV show patterns
        tv_patterns = [
            (r"(.+?)[ ]S(\d{1,2})E(\d{1,2})", "SxxEyy"),  # e.g., "Show S01E02"
            (r"(.+?)[ ](\d{1,2})x(\d{1,2})", "xxyy"),     # e.g., "Show 1x02"
            (r"(.+?)[ ](\d{2,3})\D", "num")               # e.g., "Show 102"
        ]
        for pattern, pat_type in tv_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                show_name = match.group(1).strip()
                if pat_type in ["SxxEyy", "xxyy"]:
                    season = int(match.group(2))
                    episode = int(match.group(3))
                elif pat_type == "num":
                    num_str = match.group(2)
                    if len(num_str) == 2:
                        season = 1
                        episode = int(num_str)
                    elif len(num_str) == 3:
                        season = int(num_str[0])
                        episode = int(num_str[1:])
                return {"type": "tv", "show": show_name, "season": season, "episode": episode, "ext": ext}

        # Movie patterns
        movie_patterns = [
            r"(.+?)\((\d{4})\)",      # e.g., "Movie (2020)"
            r"(.+?)[ ](\d{4})[ ]"     # e.g., "Movie 2020 "
        ]
        for pattern in movie_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                year = int(match.group(2))
                return {"type": "movie", "title": title, "year": year, "ext": ext}

        # Unknown format
        return {"type": "unknown", "filename": filename}

    def get_preview_filename(self, file_path):
        """Generate a preview filename using OMDB API data."""
        filename = os.path.basename(file_path)
        parsed = self.parse_filename(filename)

        if parsed["type"] == "tv":
            show = parsed["show"]
            season = parsed["season"]
            episode = parsed["episode"]
            ext = parsed["ext"]
            params = {"t": show, "Season": season, "Episode": episode, "apikey": self.api_key}
            try:
                response = requests.get("http://www.omdbapi.com/", params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("Response") == "True":
                        episode_title = data.get("Title", "Unknown")
                        new_filename = f"{show} - S{season:02d}E{episode:02d} - {episode_title}{ext}"
                        return new_filename, "green"
                    else:
                        return filename, "red"
                else:
                    return filename, "red"
            except Exception as e:
                print(f"Error querying OMDB API: {e}")
                return filename, "red"

        elif parsed["type"] == "movie":
            title = parsed["title"]
            year = parsed["year"]
            ext = parsed["ext"]
            params = {"t": title, "y": year, "apikey": self.api_key}
            try:
                response = requests.get("http://www.omdbapi.com/", params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("Response") == "True":
                        official_title = data.get("Title", title)
                        official_year = data.get("Year", year)
                        new_filename = f"{official_title} ({official_year}){ext}"
                        return new_filename, "green"
                    else:
                        return filename, "red"
                else:
                    return filename, "red"
            except Exception as e:
                print(f"Error querying OMDB API: {e}")
                return filename, "red"

        else:
            return parsed["filename"], "orange"

# Main Execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileNomApp()
    window.show()
    sys.exit(app.exec_())