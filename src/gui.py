import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget
from gui_settings import APISettingsTab  # Import API Settings Tab

class RenamerTab(QWidget):
    """Main renaming tab where users select files & rename them."""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Select files to rename:")
        self.file_list = QListWidget()

        self.select_button = QPushButton("Select Files")
        self.rename_button = QPushButton("Rename Files")

        self.select_button.clicked.connect(self.select_files)
        self.rename_button.clicked.connect(self.rename_files)

        layout.addWidget(self.label)
        layout.addWidget(self.file_list)
        layout.addWidget(self.select_button)
        layout.addWidget(self.rename_button)

        self.setLayout(layout)

    def select_files(self):
        """Allow users to select multiple files for renaming."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Video Files", "", "Video Files (*.mp4 *.mkv *.avi)")
        if files:
            self.file_list.addItems(files)

    def rename_files(self):
        """Placeholder function for renaming logic (to be implemented)."""
        print("Renaming files... (Feature coming soon)")
        # Future: Call rename_file() for each selected file

class ArchiTekGUI(QMainWindow):
    """Main GUI with tabs for renaming and settings."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchiTek - Video Renamer")
        self.setGeometry(100, 100, 800, 500)

        self.tabs = QTabWidget()
        self.rename_tab = RenamerTab()
        self.api_settings_tab = APISettingsTab()

        self.tabs.addTab(self.rename_tab, "File Renamer")
        self.tabs.addTab(self.api_settings_tab, "API Settings")

        self.setCentralWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArchiTekGUI()
    window.show()
    sys.exit(app.exec())
