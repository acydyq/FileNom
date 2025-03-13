import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QLabel, QMessageBox
)
from renamer import rename_file

class FileRenamerGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("ArchiTek FileBot Clone")
        self.setGeometry(100, 100, 600, 400)

        # Layout
        layout = QVBoxLayout()

        # File list
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Load files button
        self.load_button = QPushButton("Load Files")
        self.load_button.clicked.connect(self.load_files)
        layout.addWidget(self.load_button)

        # Rename button
        self.rename_button = QPushButton("Rename Files")
        self.rename_button.clicked.connect(self.rename_files)
        layout.addWidget(self.rename_button)

        # Log label
        self.log_label = QLabel("Status: Ready")
        layout.addWidget(self.log_label)

        self.setLayout(layout)

    def load_files(self):
        """
        Opens a file dialog to select video files for renaming.
        """
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "", "Video Files (*.mkv *.mp4 *.avi *.mov)"
        )

        if files:
            self.file_list.addItems(files)
            self.log_label.setText(f"Loaded {len(files)} files.")

    def rename_files(self):
        """
        Renames selected files using renamer.py logic.
        """
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please load files first.")
            return

        success_count = 0
        fail_count = 0

        for i in range(self.file_list.count()):
            file_path = self.file_list.item(i).text()
            if rename_file(file_path):
                success_count += 1
            else:
                fail_count += 1

        self.log_label.setText(f"Renamed: {success_count}, Failed: {fail_count}")

        if success_count > 0:
            QMessageBox.information(self, "Renaming Complete", f"Successfully renamed {success_count} files!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamerGUI()
    window.show()
    sys.exit(app.exec())
