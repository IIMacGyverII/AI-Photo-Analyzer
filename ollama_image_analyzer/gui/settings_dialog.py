"""Settings dialog for configuring Ollama connection and preferences."""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QFileDialog,
    QSpinBox,
)

from ollama_image_analyzer.core import Config, OllamaAnalyzer

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, config: Config, parent: Optional[QDialog] = None) -> None:
        """
        Initialize the settings dialog.
        
        Args:
            config: Current configuration.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.config = config
        self._setup_ui()
        self._load_settings()
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Ollama settings group
        ollama_group = QGroupBox("Ollama Server")
        ollama_layout = QFormLayout(ollama_group)
        
        # Host input
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("http://localhost:11434")
        ollama_layout.addRow("Host URL:", self.host_input)
        
        # Model selection
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems(["llava", "moondream", "bakllava"])
        model_layout.addWidget(self.model_combo)
        
        # Refresh models button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Refresh available models from server")
        self.refresh_button.setMaximumWidth(40)
        self.refresh_button.clicked.connect(self._refresh_models)
        model_layout.addWidget(self.refresh_button)
        
        ollama_layout.addRow("Model:", model_layout)
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(30)
        self.timeout_spin.setMaximum(600)
        self.timeout_spin.setSuffix(" seconds")
        ollama_layout.addRow("Timeout:", self.timeout_spin)
        
        layout.addWidget(ollama_group)
        
        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        
        # Output directory
        dir_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Same as image (leave empty)")
        dir_layout.addWidget(self.output_dir_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(browse_button)
        
        output_layout.addRow("Output Directory:", dir_layout)
        
        # Overwrite existing files checkbox
        self.overwrite_checkbox = QCheckBox("Overwrite existing files")
        self.overwrite_checkbox.setToolTip(
            "When enabled, new analyses will overwrite existing .txt and .yml files.\n"
            "When disabled, numbered versions will be created (file_1.txt, file_2.txt, etc.)"
        )
        output_layout.addRow("", self.overwrite_checkbox)
        
        layout.addWidget(output_group)
        
        # Test connection button
        self.test_button = QPushButton("🔌 Test Connection")
        self.test_button.setObjectName("primaryButton")
        self.test_button.clicked.connect(self._test_connection)
        layout.addWidget(self.test_button)
        
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_settings(self) -> None:
        """Load current settings into the dialog."""
        self.host_input.setText(self.config.ollama_host)
        self.model_combo.setCurrentText(self.config.ollama_model)
        self.timeout_spin.setValue(self.config.timeout_seconds)
        
        if self.config.output_directory:
            self.output_dir_input.setText(self.config.output_directory)
        
        self.overwrite_checkbox.setChecked(self.config.overwrite_existing_files)
    
    def _browse_output_dir(self) -> None:
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir_input.text() or ""
        )
        
        if directory:
            self.output_dir_input.setText(directory)
    
    def _refresh_models(self) -> None:
        """Refresh the list of available models from Ollama server."""
        host = self.host_input.text() or self.config.ollama_host
        
        try:
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("⏳")
            
            analyzer = OllamaAnalyzer(host=host)
            
            if not analyzer.test_connection():
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    f"Could not connect to Ollama server at:\n{host}\n\n"
                    "Make sure Ollama is running and the host URL is correct."
                )
                return
            
            models = analyzer.get_vision_models()
            
            if not models:
                models = analyzer.list_models()
            
            if models:
                current_text = self.model_combo.currentText()
                self.model_combo.clear()
                self.model_combo.addItems(models)
                
                # Restore previous selection if it exists
                index = self.model_combo.findText(current_text)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Found {len(models)} model(s) on the server."
                )
            else:
                QMessageBox.warning(
                    self,
                    "No Models",
                    "No models found on the server.\n\n"
                    "You may need to pull a vision model first:\n"
                    "ollama pull llava"
                )
        
        except Exception as e:
            logger.error(f"Failed to refresh models: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh models:\n{str(e)}"
            )
        
        finally:
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("🔄")
    
    def _test_connection(self) -> None:
        """Test connection to Ollama server."""
        host = self.host_input.text() or self.config.ollama_host
        
        try:
            self.test_button.setEnabled(False)
            original_text = self.test_button.text()
            self.test_button.setText("Testing...")
            
            analyzer = OllamaAnalyzer(host=host)
            
            if analyzer.test_connection():
                models = analyzer.list_models()
                QMessageBox.information(
                    self,
                    "Connection Successful",
                    f"✓ Connected to Ollama server\n\n"
                    f"Server: {host}\n"
                    f"Available models: {len(models)}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    f"Could not connect to Ollama server at:\n{host}\n\n"
                    "Make sure Ollama is running and the host URL is correct."
                )
        
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Connection test failed:\n{str(e)}"
            )
        
        finally:
            self.test_button.setEnabled(True)
            self.test_button.setText(original_text)
    
    def get_settings(self) -> dict:
        """
        Get the settings from the dialog.
        
        Returns:
            Dictionary of settings.
        """
        return {
            "ollama_host": self.host_input.text().strip() or "http://localhost:11434",
            "ollama_model": self.model_combo.currentText().strip() or "llava",
            "timeout_seconds": self.timeout_spin.value(),
            "output_directory": self.output_dir_input.text().strip() or None,
            "overwrite_existing_files": self.overwrite_checkbox.isChecked(),
        }
