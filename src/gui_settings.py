import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from config import load_config, save_config, validate_tmdb_key, validate_simkl_key

class APISettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Labels & Input Fields
        self.tmdb_label = QLabel("TMDb API Key:")
        self.tmdb_input = QLineEdit()
        self.simkl_label = QLabel("SIMKL API Key:")
        self.simkl_input = QLineEdit()

        # Load saved API keys
        config = load_config()
        self.tmdb_input.setText(config.get("tmdb_api_key", ""))
        self.simkl_input.setText(config.get("simkl_api_key", ""))

        # Buttons
        self.save_button = QPushButton("Save API Keys")
        self.validate_button = QPushButton("Validate Keys")

        self.save_button.clicked.connect(self.save_keys)
        self.validate_button.clicked.connect(self.validate_keys)

        # Add Widgets
        layout.addWidget(self.tmdb_label)
        layout.addWidget(self.tmdb_input)
        layout.addWidget(self.simkl_label)
        layout.addWidget(self.simkl_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.validate_button)

        self.setLayout(layout)

    def save_keys(self):
        """Save API keys to config.json."""
        tmdb_key = self.tmdb_input.text().strip()
        simkl_key = self.simkl_input.text().strip()
        save_config(tmdb_key, simkl_key)
        QMessageBox.information(self, "Success", "API keys saved successfully!")

    def validate_keys(self):
        """Validate TMDb & SIMKL API keys."""
        tmdb_key = self.tmdb_input.text().strip()
        simkl_key = self.simkl_input.text().strip()

        tmdb_valid = validate_tmdb_key(tmdb_key)
        simkl_valid = validate_simkl_key(simkl_key)

        msg = "Validation Results:\n"
        msg += f"✅ TMDb Key: {'Valid' if tmdb_valid else 'Invalid'}\n"
        msg += f"✅ SIMKL Key: {'Valid' if simkl_valid else 'Invalid'}"

        QMessageBox.information(self, "API Key Validation", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = APISettingsTab()
    window.show()
    sys.exit(app.exec())
