import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QLabel, QMessageBox
from renamer import rename_file

class FileRenamerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("FileNom - TV Show & Movie Renamer")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Select files to rename:")
        layout.addWidget(self.label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self.add_files)
        layout.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)
        layout.addWidget(self.add_folder_btn)

        self.rename_btn = QPushButton("Rename Files")
        self.rename_btn.clicked.connect(self.rename_files)
        layout.addWidget(self.rename_btn)

        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.clicked.connect(self.clear_list)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if files:
            for file in files:
                self.file_list.addItem(file)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                        self.file_list.addItem(os.path.join(root, file))

    def rename_files(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "No files selected for renaming.")
            return

        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item is not None:
                file_path = item.text()
                success = rename_file(file_path)
                if success:
                    print(f"✅ Renamed: {file_path} → {success}")
                else:
                    print(f"❌ Skipping renaming for: {file_path}")

        QMessageBox.information(self, "Renaming Complete", "All selected files have been processed.")

    def clear_list(self):
        self.file_list.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileRenamerGUI()
    window.show()
    sys.exit(app.exec_())
