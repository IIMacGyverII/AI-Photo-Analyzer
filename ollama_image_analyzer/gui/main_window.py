"""Main window for Ollama Image Analyzer GUI."""

import logging
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

from ollama_image_analyzer.core import (
    Config,
    OllamaAnalyzer,
    AnalysisResult,
    get_config,
    save_config,
)
from ollama_image_analyzer.resources import ICON_PATH
from .image_viewer import ImageViewer
from .prompt_editor import PromptEditor
from .settings_dialog import SettingsDialog
from .worker import AnalysisWorker
from .batch_worker import BatchAnalysisWorker
from .theme import DARK_THEME

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        self.config = get_config()
        self.analyzer: Optional[OllamaAnalyzer] = None
        self.current_worker: Optional[AnalysisWorker] = None
        self.batch_worker: Optional[BatchAnalysisWorker] = None
        self.batch_total_count: int = 0  # Track total for batch operations
        
        # Batch performance tracking
        self.batch_metrics_count: int = 0
        self.batch_total_tokens: int = 0
        self.batch_total_prompt_tokens: int = 0
        self.batch_total_duration: int = 0
        self.batch_total_eval_duration: int = 0
        self.batch_total_load_duration: int = 0
        
        # Batch time tracking for ETA
        self.batch_start_time: float = 0.0
        self.batch_completed_count: int = 0
        
        # Batch error tracking
        self.batch_failed_items: list[tuple[Path, str, str]] = []  # (path, filename, error_message)
        
        self._setup_ui()
        self._setup_menu()
        self._apply_theme()
        self._restore_geometry()
        self._update_analyzer()
        
        self.setWindowTitle("Ollama Image Analyzer")
        
        # Set window icon
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title = QLabel("🤖 Ollama Image Analyzer")
        title.setObjectName("titleLabel")
        main_layout.addWidget(title)
        
        # Status panel
        status_panel = QWidget()
        status_panel.setObjectName("statusPanel")
        status_panel_layout = QHBoxLayout(status_panel)
        status_panel_layout.setContentsMargins(12, 8, 12, 8)
        
        # Connection status
        connection_label = QLabel("Status:")
        connection_label.setObjectName("subtitleLabel")
        status_panel_layout.addWidget(connection_label)
        
        self.connection_status = QLabel("⚫ Disconnected")
        self.connection_status.setObjectName("statusLabel")
        status_panel_layout.addWidget(self.connection_status)
        
        status_panel_layout.addSpacing(20)
        
        # Current model selector
        model_label = QLabel("Model:")
        model_label.setObjectName("subtitleLabel")
        status_panel_layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        self.model_selector.setMinimumWidth(200)
        self.model_selector.setToolTip("Select the Ollama model to use for analysis")
        self.model_selector.currentTextChanged.connect(self._on_model_changed)
        status_panel_layout.addWidget(self.model_selector)
        
        status_panel_layout.addStretch()
        
        # Version label
        from ollama_image_analyzer import __version__
        version_label = QLabel(f"v{__version__}")
        version_label.setStyleSheet("color: #6c7086; font-size: 11px;")
        status_panel_layout.addWidget(version_label)
        
        main_layout.addWidget(status_panel)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Image viewer
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_viewer = ImageViewer()
        self.image_viewer.image_loaded.connect(self._on_image_loaded)
        left_layout.addWidget(self.image_viewer)
        
        # Import button
        self.import_button = QPushButton("📁 Import Image")
        self.import_button.setObjectName("primaryButton")
        self.import_button.clicked.connect(self._import_image)
        left_layout.addWidget(self.import_button)
        
        # Batch analyze button
        self.batch_button = QPushButton("📂 Batch Analyze Folder")
        self.batch_button.setToolTip("Analyze all images in a folder")
        self.batch_button.clicked.connect(self._batch_analyze_folder)
        left_layout.addWidget(self.batch_button)
        
        splitter.addWidget(left_widget)
        
        # Right side: Prompt editor and controls
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Prompt editor
        self.prompt_editor = PromptEditor()
        self.prompt_editor.preset_changed.connect(self._on_preset_changed)
        right_layout.addWidget(self.prompt_editor)
        
        # Response preview
        response_group = QGroupBox("Response Preview")
        response_layout = QVBoxLayout(response_group)
        
        self.response_preview = QTextEdit()
        self.response_preview.setReadOnly(True)
        self.response_preview.setPlaceholderText(
            "Analysis results will appear here...\n\n"
            "The full response is automatically saved as a .txt file "
            "next to the image."
        )
        self.response_preview.setMinimumHeight(150)
        response_layout.addWidget(self.response_preview)
        
        right_layout.addWidget(response_group)
        
        # Performance metrics panel
        perf_group = QGroupBox("⚡ Performance Metrics")
        perf_layout = QVBoxLayout(perf_group)
        
        # Current image metrics
        current_label = QLabel("Current:")
        current_label.setObjectName("subtitleLabel")
        perf_layout.addWidget(current_label)
        
        # Create a grid for current metrics
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(8)
        
        # Row 1: Tokens/sec and Total time
        metrics_grid.addWidget(QLabel("Speed:"), 0, 0)
        self.tokens_per_sec_label = QLabel("—")
        self.tokens_per_sec_label.setObjectName("statusLabel")
        metrics_grid.addWidget(self.tokens_per_sec_label, 0, 1)
        
        metrics_grid.addWidget(QLabel("Total Time:"), 0, 2)
        self.total_time_label = QLabel("—")
        self.total_time_label.setObjectName("statusLabel")
        metrics_grid.addWidget(self.total_time_label, 0, 3)
        
        # Row 2: Response tokens and Prompt tokens
        metrics_grid.addWidget(QLabel("Response:"), 1, 0)
        self.response_tokens_label = QLabel("—")
        self.response_tokens_label.setObjectName("statusLabel")
        metrics_grid.addWidget(self.response_tokens_label, 1, 1)
        
        metrics_grid.addWidget(QLabel("Prompt:"), 1, 2)
        self.prompt_tokens_label = QLabel("—")
        self.prompt_tokens_label.setObjectName("statusLabel")
        metrics_grid.addWidget(self.prompt_tokens_label, 1, 3)
        
        # Row 3: Eval time and Load time
        metrics_grid.addWidget(QLabel("Eval Time:"), 2, 0)
        self.eval_time_label = QLabel("—")
        self.eval_time_label.setObjectName("statusLabel")
        metrics_grid.addWidget(self.eval_time_label, 2, 1)
        
        metrics_grid.addWidget(QLabel("Load Time:"), 2, 2)
        self.load_time_label = QLabel("—")
        self.load_time_label.setObjectName("statusLabel")
        metrics_grid.addWidget(self.load_time_label, 2, 3)
        
        # Set column stretch to make it look better
        metrics_grid.setColumnStretch(1, 1)
        metrics_grid.setColumnStretch(3, 1)
        
        perf_layout.addLayout(metrics_grid)
        
        # Average metrics (for batch mode)
        self.avg_label = QLabel("Average (Batch):")
        self.avg_label.setObjectName("subtitleLabel")
        self.avg_label.setVisible(False)
        perf_layout.addWidget(self.avg_label)
        
        # Create a grid for average metrics
        avg_metrics_grid = QGridLayout()
        avg_metrics_grid.setSpacing(8)
        
        # Average row 1: Tokens/sec and Total time
        avg_metrics_grid.addWidget(QLabel("Avg Speed:"), 0, 0)
        self.avg_tokens_per_sec_label = QLabel("—")
        self.avg_tokens_per_sec_label.setObjectName("statusLabel")
        avg_metrics_grid.addWidget(self.avg_tokens_per_sec_label, 0, 1)
        
        avg_metrics_grid.addWidget(QLabel("Avg Time:"), 0, 2)
        self.avg_total_time_label = QLabel("—")
        self.avg_total_time_label.setObjectName("statusLabel")
        avg_metrics_grid.addWidget(self.avg_total_time_label, 0, 3)
        
        # Average row 2: Response tokens and Prompt tokens
        avg_metrics_grid.addWidget(QLabel("Avg Response:"), 1, 0)
        self.avg_response_tokens_label = QLabel("—")
        self.avg_response_tokens_label.setObjectName("statusLabel")
        avg_metrics_grid.addWidget(self.avg_response_tokens_label, 1, 1)
        
        avg_metrics_grid.addWidget(QLabel("Avg Prompt:"), 1, 2)
        self.avg_prompt_tokens_label = QLabel("—")
        self.avg_prompt_tokens_label.setObjectName("statusLabel")
        avg_metrics_grid.addWidget(self.avg_prompt_tokens_label, 1, 3)
        
        avg_metrics_grid.setColumnStretch(1, 1)
        avg_metrics_grid.setColumnStretch(3, 1)
        
        perf_layout.addLayout(avg_metrics_grid)
        self.avg_metrics_grid_widget = avg_metrics_grid
        right_layout.addWidget(perf_group)
        
        # Keep performance metrics visible (shows "—" until analysis runs)
        perf_group.setVisible(True)
        self.perf_group = perf_group
        
        # Output format checkboxes
        checkbox_row = QHBoxLayout()
        
        # Custom checkbox stylesheet for better visibility
        checkbox_style = """
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 5px;
                border: 2px solid #585b70;
                background-color: #1e1e2e;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #89b4fa;
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #a6e3a1;
                border: 2px solid #a6e3a1;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #94e2a5;
                border: 2px solid #94e2a5;
            }
            QCheckBox::indicator:unchecked {
                background-color: #1e1e2e;
                border: 2px solid #585b70;
            }
            QCheckBox::indicator:unchecked:hover {
                background-color: #313244;
                border: 2px solid #89b4fa;
            }
        """
        
        # YAML sidecar checkbox
        self.write_yaml_checkbox = QCheckBox("✓ Write YAML sidecar")
        self.write_yaml_checkbox.setStyleSheet(checkbox_style)
        self.write_yaml_checkbox.setToolTip(
            "When enabled, creates PhotoPrism-compatible YAML sidecar files (.yml).\n"
            "These files contain structured metadata that photo management tools can read.\n"
            "Recommended for PhotoPrism integration."
        )
        self.write_yaml_checkbox.setChecked(True)  # Default to on
        self.write_yaml_checkbox.setVisible(False)  # Hidden by default until preset selected
        checkbox_row.addWidget(self.write_yaml_checkbox)
        
        # Metadata writing checkbox
        self.write_metadata_checkbox = QCheckBox("✓ Write to image metadata (EXIF/IPTC)")
        self.write_metadata_checkbox.setStyleSheet(checkbox_style)
        self.write_metadata_checkbox.setToolTip(
            "When enabled, writes the analysis result directly into the image file's EXIF/IPTC metadata fields.\n"
            "A .bak backup is created before modifying the original image.\n"
            "Only works with JPEG images."
        )
        self.write_metadata_checkbox.setChecked(False)  # Default to off
        self.write_metadata_checkbox.setVisible(False)  # Hidden by default until preset selected
        checkbox_row.addWidget(self.write_metadata_checkbox)
        
        right_layout.addLayout(checkbox_row)
        
        # Set initial checkbox visibility based on default preset
        self._on_preset_changed(self.prompt_editor.get_current_preset_name())
        
        # Button row for Analyze and Cancel
        button_row = QHBoxLayout()
        
        # Analyze button
        self.analyze_button = QPushButton("🔍 Analyze Image")
        self.analyze_button.setObjectName("primaryButton")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self._analyze_image)
        self.analyze_button.setMinimumHeight(40)
        button_row.addWidget(self.analyze_button)
        
        # Cancel button (hidden by default)
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setObjectName("dangerButton")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self._cancel_analysis)
        button_row.addWidget(self.cancel_button)
        
        right_layout.addLayout(button_row)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions (40% left, 60% right)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        
        main_layout.addWidget(splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setFormat("%p% - %v/%m")
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("Ready")
    
    def _setup_menu(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        import_action = QAction("&Import Image...", self)
        import_action.setShortcut(QKeySequence.StandardKey.Open)
        import_action.triggered.connect(self._import_image)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _apply_theme(self) -> None:
        """Apply the dark theme stylesheet."""
        self.setStyleSheet(DARK_THEME)
    
    def _restore_geometry(self) -> None:
        """Restore window geometry from config."""
        self.resize(self.config.window_width, self.config.window_height)
    
    def _save_geometry(self) -> None:
        """Save window geometry to config."""
        self.config.window_width = self.width()
        self.config.window_height = self.height()
        save_config()
    
    def _update_analyzer(self) -> None:
        """Update the Ollama analyzer with current configuration."""
        self.analyzer = OllamaAnalyzer(
            host=self.config.ollama_host,
            model=self.config.ollama_model,
            timeout=self.config.timeout_seconds,
        )
        logger.info(f"Analyzer configured: {self.config.ollama_host}, model={self.config.ollama_model}")
        self._update_connection_status()
    
    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_bar.showMessage(message)
    
    def _on_preset_changed(self, preset_name: str) -> None:
        """Handle preset change to show/hide output format checkboxes."""
        # Define which presets support which output formats
        yaml_presets = {
            "photoprism",           # Primary PhotoPrism integration
            "museum_archive",       # Archival/cataloging
            "stock_photography",    # Commercial stock libraries
            "ecommerce",           # Product cataloging
            "nft_metadata",        # NFT structured metadata
        }
        
        exif_presets = {
            "photoprism",           # PhotoPrism can read EXIF
            "museum_archive",       # Archival purposes
            "stock_photography",    # Commercial metadata
            "technical_photo_analysis",  # Photography metadata
        }
        
        # Show/hide checkboxes based on preset
        show_yaml = preset_name in yaml_presets
        show_exif = preset_name in exif_presets
        
        self.write_yaml_checkbox.setVisible(show_yaml)
        self.write_metadata_checkbox.setVisible(show_exif)
        
        # If showing checkboxes, ensure they have sensible defaults
        if show_yaml and not self.write_yaml_checkbox.isChecked():
            self.write_yaml_checkbox.setChecked(True)  # YAML on by default when visible
    
    def _update_connection_status(self) -> None:
        """Update the connection status display."""
        if self.analyzer is None:
            self.connection_status.setText("⚫ Disconnected")
            self.model_selector.clear()
            self.model_selector.setEnabled(False)
            return
        
        # Test connection
        connected = self.analyzer.test_connection()
        
        if connected:
            self.connection_status.setText("🟢 Connected")
            self.connection_status.setStyleSheet("color: #a6e3a1;")
            self._populate_model_list()
            self.model_selector.setEnabled(True)
        else:
            self.connection_status.setText("🔴 Disconnected")
            self.connection_status.setStyleSheet("color: #f38ba8;")
            self.model_selector.clear()
            self.model_selector.addItem(self.config.ollama_model)
            self.model_selector.setEnabled(False)
    
    def _populate_model_list(self) -> None:
        """Populate the model selector with available models."""
        try:
            models = self.analyzer.list_models()
            
            # Block signals while updating
            self.model_selector.blockSignals(True)
            self.model_selector.clear()
            
            # Add all available models
            for model in models:
                self.model_selector.addItem(model)
            
            # Select current model
            current_index = self.model_selector.findText(self.config.ollama_model)
            if current_index >= 0:
                self.model_selector.setCurrentIndex(current_index)
            else:
                # If current model not in list, add it and select it
                self.model_selector.addItem(self.config.ollama_model)
                self.model_selector.setCurrentText(self.config.ollama_model)
            
            self.model_selector.blockSignals(False)
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            # Fall back to just showing the current model
            self.model_selector.blockSignals(True)
            self.model_selector.clear()
            self.model_selector.addItem(self.config.ollama_model)
            self.model_selector.blockSignals(False)
    
    def _on_model_changed(self, model_name: str) -> None:
        """Handle model selection change."""
        if not model_name or model_name == self.config.ollama_model:
            return
        
        # Update config
        self.config.ollama_model = model_name
        save_config()
        
        # Update analyzer
        self._update_analyzer()
        
        self._update_status(f"Switched to model: {model_name}")
        logger.info(f"Model changed to: {model_name}")
    
    def _import_image(self) -> None:
        """Open file dialog to import an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Image",
            self.config.last_image_directory,
            "Images (*.jpg *.jpeg *.png *.webp *.gif *.bmp);;All Files (*.*)"
        )
        
        if file_path:
            path = Path(file_path)
            self.config.last_image_directory = str(path.parent)
            save_config()
            
            self.image_viewer.load_image(path)
    
    def _on_image_loaded(self, image_path: Path) -> None:
        """Handle image loaded event."""
        self.analyze_button.setEnabled(True)
        self.response_preview.clear()
        # Don't hide performance metrics - just keep them visible if already shown
        self._update_status(f"Loaded: {image_path.name}")
    
    def _analyze_image(self) -> None:
        """Start analyzing the current image."""
        if self.image_viewer.current_image is None:
            QMessageBox.warning(self, "No Image", "Please load an image first.")
            return
        
        # Ensure trigger word and prompt are up to date
        self.prompt_editor.refresh_trigger_replacement()
        
        prompt = self.prompt_editor.get_prompt()
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a prompt.")
            return
        
        # Check for existing output file
        if self.config.output_directory:
            base_output = Path(self.config.output_directory) / self.image_viewer.current_image.stem
        else:
            base_output = self.image_viewer.current_image.with_suffix("")
        
        txt_path = Path(str(base_output) + ".txt")
        
        if txt_path.exists():
            if not self.config.overwrite_existing_files:
                # Skip analysis if overwrite is disabled
                QMessageBox.information(
                    self,
                    "File Already Exists",
                    f"Analysis file already exists:\n{txt_path.name}\n\n"
                    "Overwrite protection is enabled. To analyze this image, either:\n"
                    "• Enable 'Overwrite existing files' in Settings\n"
                    "• Delete the existing file manually"
                )
                return
            else:
                # Warn user about overwriting
                reply = QMessageBox.question(
                    self,
                    "Overwrite Existing File?",
                    f"Analysis file already exists:\n{txt_path.name}\n\n"
                    "Do you want to overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
        
        # Disable UI during analysis
        self.analyze_button.setEnabled(False)
        self.import_button.setEnabled(False)
        self.batch_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setFormat("Analyzing...")
        
        # Create and start worker
        self.current_worker = AnalysisWorker(
            self.image_viewer.current_image,
            prompt,
            self.analyzer
        )
        
        self.current_worker.started.connect(self._on_analysis_started)
        self.current_worker.progress.connect(self._on_analysis_progress)
        self.current_worker.error.connect(self._on_analysis_error)
        self.current_worker.finished.connect(self._on_analysis_finished)
        
        self.current_worker.start()
    
    def _on_analysis_started(self) -> None:
        """Handle analysis started."""
        self._update_status("Analyzing image...")
    
    def _on_analysis_progress(self, message: str) -> None:
        """Handle analysis progress update."""
        self._update_status(message)
    
    def _on_analysis_error(self, error: str) -> None:
        """Handle analysis error."""
        logger.error(f"Analysis error: {error}")
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"Failed to analyze image:\n\n{error}"
        )
    
    def _on_analysis_finished(self, result: AnalysisResult) -> None:
        """Handle analysis completion."""
        # Re-enable UI
        self.analyze_button.setEnabled(True)
        self.import_button.setEnabled(True)
        self.batch_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p% - %v/%m")
        
        if result.success:
            # Show preview
            self.response_preview.setPlainText(result.response)
            
            # Update performance metrics
            self._update_performance_metrics(result)
            
            # Save result
            saved_files = []
            errors = []
            
            try:
                # Determine output path
                if self.config.output_directory:
                    base_output = Path(self.config.output_directory) / result.image_path.stem
                else:
                    base_output = result.image_path.with_suffix("")
                
                # Save YAML sidecar (PhotoPrism compatible)
                if self.write_yaml_checkbox.isVisible() and self.write_yaml_checkbox.isChecked():
                    try:
                        yaml_path = self.analyzer.save_yaml_sidecar(result, result.image_path, overwrite=self.config.overwrite_existing_files)
                        saved_files.append(f"YAML: {yaml_path.name}")
                    except ValueError as e:
                        # Validation error
                        errors.append(f"YAML (validation failed): {str(e)}")
                        logger.error(f"Validation failed: {e}")
                    except Exception as e:
                        errors.append(f"YAML sidecar: {str(e)}")
                        logger.error(f"Failed to save YAML sidecar: {e}")
                
                # Save .txt file (for backward compatibility)
                try:
                    txt_path = self.analyzer.save_result(result, Path(str(base_output) + ".txt"), overwrite=self.config.overwrite_existing_files)
                    saved_files.append(f"Text: {txt_path.name}")
                except ValueError as e:
                    # Validation error
                    errors.append(f"Text file (validation failed): {str(e)}")
                    logger.error(f"Validation failed: {e}")
                except Exception as e:
                    errors.append(f"Text file: {str(e)}")
                    logger.error(f"Failed to save text file: {e}")
                
                # Optionally write to image metadata
                if self.write_metadata_checkbox.isVisible() and self.write_metadata_checkbox.isChecked():
                    try:
                        if self.analyzer.write_to_image_metadata(result, result.image_path):
                            saved_files.append("EXIF metadata")
                        else:
                            errors.append("EXIF metadata: write failed")
                    except Exception as e:
                        errors.append(f"EXIF metadata: {str(e)}")
                        logger.error(f"Failed to write image metadata: {e}")
                
                # Show status
                if saved_files:
                    self._update_status(f"✓ Analysis complete! Saved: {', '.join(saved_files)}")
                    
                    message = "Analysis successful!\n\n" + "Saved files:\n" + "\n".join(f"• {f}" for f in saved_files)
                    if errors:
                        message += "\n\nErrors:\n" + "\n".join(f"• {e}" for e in errors)
                    
                    QMessageBox.information(
                        self,
                        "Analysis Complete",
                        message
                    )
                else:
                    raise Exception("All save operations failed")
            
            except Exception as e:
                logger.error(f"Failed to save result: {e}")
                QMessageBox.warning(
                    self,
                    "Save Error",
                    f"Analysis completed but failed to save:\n{str(e)}\n\n"
                    "You can copy the text from the preview."
                )
        else:
            self._update_status("Analysis failed")
    
    def _update_performance_metrics(self, result: AnalysisResult) -> None:
        """Update the performance metrics display with analysis results."""
        # Performance panel is always visible, just update the values
        
        # Update tokens per second
        if result.tokens_per_second:
            self.tokens_per_sec_label.setText(f"{result.tokens_per_second:.2f} tok/s")
            self.tokens_per_sec_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        else:
            self.tokens_per_sec_label.setText("—")
            self.tokens_per_sec_label.setStyleSheet("")
        
        # Update total time
        if result.total_seconds:
            self.total_time_label.setText(f"{result.total_seconds:.2f}s")
        else:
            self.total_time_label.setText("—")
        
        # Update response tokens
        if result.eval_count:
            self.response_tokens_label.setText(f"{result.eval_count} tokens")
        else:
            self.response_tokens_label.setText("—")
        
        # Update prompt tokens
        if result.prompt_eval_count:
            self.prompt_tokens_label.setText(f"{result.prompt_eval_count} tokens")
        else:
            self.prompt_tokens_label.setText("—")
        
        # Update eval time
        if result.eval_duration:
            eval_seconds = result.eval_duration / 1_000_000_000
            self.eval_time_label.setText(f"{eval_seconds:.2f}s")
        else:
            self.eval_time_label.setText("—")
        
        # Update load time
        if result.load_duration:
            load_seconds = result.load_duration / 1_000_000_000
            self.load_time_label.setText(f"{load_seconds:.2f}s")
        else:
            self.load_time_label.setText("—")
    
    def _update_batch_average_metrics(self) -> None:
        """Update the batch average metrics display."""
        if self.batch_metrics_count == 0:
            return
        
        # Calculate average tokens per second
        if self.batch_total_eval_duration > 0:
            avg_eval_seconds = self.batch_total_eval_duration / 1_000_000_000
            avg_tokens_per_sec = self.batch_total_tokens / avg_eval_seconds
            self.avg_tokens_per_sec_label.setText(f"{avg_tokens_per_sec:.2f} tok/s")
            self.avg_tokens_per_sec_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        else:
            self.avg_tokens_per_sec_label.setText("—")
            self.avg_tokens_per_sec_label.setStyleSheet("")
        
        # Calculate average total time
        if self.batch_total_duration > 0:
            avg_total_seconds = (self.batch_total_duration / 1_000_000_000) / self.batch_metrics_count
            self.avg_total_time_label.setText(f"{avg_total_seconds:.2f}s")
        else:
            self.avg_total_time_label.setText("—")
        
        # Calculate average response tokens
        avg_response_tokens = self.batch_total_tokens / self.batch_metrics_count
        self.avg_response_tokens_label.setText(f"{avg_response_tokens:.1f} tokens")
        
        # Calculate average prompt tokens
        if self.batch_total_prompt_tokens > 0:
            avg_prompt_tokens = self.batch_total_prompt_tokens / self.batch_metrics_count
            self.avg_prompt_tokens_label.setText(f"{avg_prompt_tokens:.1f} tokens")
        else:
            self.avg_prompt_tokens_label.setText("—")
    
    def _batch_analyze_folder(self) -> None:
        """Start batch analysis of all images in a folder."""
        # Select folder
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Analyze",
            self.config.last_image_directory,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not folder_path:
            return
        
        folder = Path(folder_path)
        self.config.last_image_directory = str(folder)
        save_config()
        
        # Find all images in folder
        image_paths = []
        for ext in OllamaAnalyzer.SUPPORTED_FORMATS:
            image_paths.extend(folder.glob(f"*{ext}"))
            image_paths.extend(folder.glob(f"*{ext.upper()}"))
        
        # Sort by name
        image_paths = sorted(set(image_paths))
        
        if not image_paths:
            QMessageBox.information(
                self,
                "No Images Found",
                f"No supported images found in:\n{folder}\n\n"
                f"Supported formats: {', '.join(OllamaAnalyzer.SUPPORTED_FORMATS)}"
            )
            return
        
        # Check for existing output files
        existing_files = []
        images_to_process = []
        
        for img_path in image_paths:
            if self.config.output_directory:
                base_output = Path(self.config.output_directory) / img_path.stem
            else:
                base_output = img_path.with_suffix("")
            
            txt_path = Path(str(base_output) + ".txt")
            
            if txt_path.exists():
                existing_files.append(txt_path.name)
                if self.config.overwrite_existing_files:
                    images_to_process.append(img_path)
            else:
                images_to_process.append(img_path)
        
        # Handle overwrite protection
        if not self.config.overwrite_existing_files and existing_files:
            skip_count = len(existing_files)
            process_count = len(images_to_process)
            
            if process_count == 0:
                QMessageBox.information(
                    self,
                    "All Files Exist",
                    f"All {len(image_paths)} images already have analysis files.\n\n"
                    "Overwrite protection is enabled. To re-analyze these images:\n"
                    "• Enable 'Overwrite existing files' in Settings\n"
                    "• Delete the existing analysis files"
                )
                return
            else:
                QMessageBox.information(
                    self,
                    "Skipping Existing Files",
                    f"Found {len(image_paths)} images.\n\n"
                    f"Skipping {skip_count} image(s) with existing analysis files.\n"
                    f"Will process {process_count} new image(s).\n\n"
                    "To process all files, enable 'Overwrite existing files' in Settings."
                )
            
            # Update image_paths to only include images to process
            image_paths = images_to_process
        
        elif self.config.overwrite_existing_files and existing_files:
            # Show overwrite warning with scrollable list
            dialog = OverwriteWarningDialog(existing_files, self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            
            # User confirmed, use all images
            image_paths = images_to_process
        
        # Confirm batch operation
        # First, ensure trigger word and prompt are up to date
        self.prompt_editor.refresh_trigger_replacement()
        
        prompt = self.prompt_editor.get_prompt()
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a prompt.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Batch Analysis",
            f"Found {len(image_paths)} images in:\n{folder.name}\n\n"
            f"Model: {self.config.ollama_model}\n"
            f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"
            f"Proceed with batch analysis?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable UI during batch analysis
        self.analyze_button.setEnabled(False)
        self.import_button.setEnabled(False)
        self.batch_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(image_paths))
        self.progress_bar.setValue(0)
        
        # Store total count for completion summary
        self.batch_total_count = len(image_paths)
        
        # Create and start batch worker
        self.batch_worker = BatchAnalysisWorker(
            image_paths,
            prompt,
            self.analyzer
        )
        
        self.batch_worker.started.connect(self._on_batch_started)
        self.batch_worker.item_started.connect(self._on_batch_item_started)
        self.batch_worker.item_finished.connect(self._on_batch_item_finished)
        self.batch_worker.item_retry.connect(self._on_batch_item_retry)
        self.batch_worker.progress.connect(self._on_batch_progress)
        self.batch_worker.error.connect(self._on_batch_error)
        self.batch_worker.finished.connect(self._on_batch_finished)
        
        self.batch_worker.start()
    
    def _on_batch_started(self) -> None:
        """Handle batch analysis started."""
        self._update_status("Starting batch analysis...")
        self.response_preview.clear()
        self.response_preview.setPlainText("Batch analysis in progress...\n\nResults will be saved next to each image.")
        
        # Reset batch metrics
        self.batch_metrics_count = 0
        self.batch_total_tokens = 0
        self.batch_total_prompt_tokens = 0
        self.batch_total_duration = 0
        self.batch_total_eval_duration = 0
        self.batch_total_load_duration = 0
        
        # Reset time tracking
        self.batch_start_time = time.time()
        self.batch_completed_count = 0
        
        # Reset error tracking
        self.batch_failed_items = []
        
        # Show average section (performance panel already visible)
        self.avg_label.setVisible(True)
    
    def _on_batch_item_started(self, current: int, total: int, filename: str, image_path: Path) -> None:
        """Handle batch item started."""
        # Update progress bar with ETA
        self._update_batch_progress_with_eta(current - 1, total)
        self._update_status(f"Analyzing {current}/{total}: {filename}")
        
        # Load and display the current image
        try:
            self.image_viewer.load_image(image_path)
            logger.debug(f"Loaded batch image: {filename}")
        except Exception as e:
            logger.error(f"Failed to load batch image {filename}: {e}")
    
    def _on_batch_item_retry(self, filename: str, error_msg: str) -> None:
        """Handle batch item retry notification."""
        short_error = error_msg[:40] + "..." if len(error_msg) > 40 else error_msg
        self._update_status(f"⚠️ Retrying {filename} (failed: {short_error})")
        logger.info(f"Retrying {filename} after failure: {error_msg}")
    
    def _on_batch_item_finished(self, result: AnalysisResult) -> None:
        """Handle batch item finished."""
        # Update completion count and ETA
        self.batch_completed_count += 1
        self._update_batch_progress_with_eta(self.batch_completed_count, self.batch_total_count)
        
        if result.success:
            # Save the result next to the image
            saved_files = []
            save_errors = []
            
            try:
                # Determine output base path
                if self.config.output_directory:
                    base_output = Path(self.config.output_directory) / result.image_path.stem
                else:
                    base_output = result.image_path.with_suffix("")
                
                # Save YAML sidecar (PhotoPrism compatible)
                if self.write_yaml_checkbox.isVisible() and self.write_yaml_checkbox.isChecked():
                    try:
                        yaml_path = self.analyzer.save_yaml_sidecar(result, result.image_path, overwrite=self.config.overwrite_existing_files)
                        saved_files.append("YAML")
                    except ValueError as e:
                        # Validation error - this is critical
                        save_errors.append(f"YAML validation: {str(e)}")
                        logger.error(f"Validation failed for {result.image_path.name}: {e}")
                    except Exception as e:
                        save_errors.append(f"YAML save: {str(e)}")
                        logger.error(f"Failed to save YAML sidecar for {result.image_path.name}: {e}")
                
                # Save .txt file (for backward compatibility)
                try:
                    txt_path = self.analyzer.save_result(result, Path(str(base_output) + ".txt"), overwrite=self.config.overwrite_existing_files)
                    saved_files.append("TXT")
                except ValueError as e:
                    # Validation error - this is critical
                    save_errors.append(f"TXT validation: {str(e)}")
                    logger.error(f"Validation failed for {result.image_path.name}: {e}")
                except Exception as e:
                    save_errors.append(f"TXT save: {str(e)}")
                    logger.error(f"Failed to save text file for {result.image_path.name}: {e}")
                
                # Optionally write to image metadata
                if self.write_metadata_checkbox.isVisible() and self.write_metadata_checkbox.isChecked():
                    try:
                        if self.analyzer.write_to_image_metadata(result, result.image_path):
                            saved_files.append("EXIF")
                        else:
                            logger.warning(f"Failed to write metadata for {result.image_path.name}")
                    except Exception as e:
                        save_errors.append(f"EXIF: {str(e)}")
                        logger.error(f"Failed to write image metadata for {result.image_path.name}: {e}")
                
                # If no files were saved successfully, treat this as a failure
                if not saved_files:
                    error_msg = "All save operations failed: " + "; ".join(save_errors)
                    logger.error(f"Complete save failure for {result.image_path.name}: {error_msg}")
                    self.batch_failed_items.append((result.image_path, result.image_path.name, error_msg))
                    self._update_status(f"❌ Failed to save {result.image_path.name}: {error_msg}")
                else:
                    logger.info(f"Batch item complete: {result.image_path.name} -> Saved: {', '.join(saved_files)}")
                    if save_errors:
                        # Some saves failed but at least one succeeded
                        logger.warning(f"Partial save for {result.image_path.name} - Errors: {'; '.join(save_errors)}")
                
                # Display the response
                self.response_preview.setPlainText(result.response)
                
                # Update performance metrics
                self._update_performance_metrics(result)
                
                # Track batch averages
                if result.eval_count:
                    self.batch_metrics_count += 1
                    self.batch_total_tokens += result.eval_count or 0
                    self.batch_total_prompt_tokens += result.prompt_eval_count or 0
                    self.batch_total_duration += result.total_duration or 0
                    self.batch_total_eval_duration += result.eval_duration or 0
                    self.batch_total_load_duration += result.load_duration or 0
                    
                    # Update average displays
                    self._update_batch_average_metrics()
                    
            except Exception as e:
                error_msg = f"Save error: {str(e)}"
                logger.error(f"Failed to save batch result for {result.image_path.name}: {e}")
                self.batch_failed_items.append((result.image_path, result.image_path.name, error_msg))
                self._update_status(f"⚠️ Error saving {result.image_path.name}: {error_msg}")
        else:
            error_msg = result.error or "Unknown error"
            logger.error(f"Batch item failed: {result.image_path.name} - {error_msg}")
            self.batch_failed_items.append((result.image_path, result.image_path.name, error_msg))
            self._update_status(f"❌ Failed: {result.image_path.name} - {error_msg}")
    
    def _update_batch_progress_with_eta(self, completed: int, total: int) -> None:
        """Update progress bar with completion count and estimated time remaining.
        
        Args:
            completed: Number of images completed so far.
            total: Total number of images to process.
        """
        self.progress_bar.setValue(completed)
        
        if completed == 0:
            # No time data yet
            self.progress_bar.setFormat(f"{completed}/{total} - %p%")
        else:
            # Calculate ETA
            elapsed_time = time.time() - self.batch_start_time
            avg_time_per_image = elapsed_time / completed
            remaining_images = total - completed
            estimated_seconds = avg_time_per_image * remaining_images
            
            # Format ETA nicely
            if estimated_seconds < 60:
                eta_str = f"{int(estimated_seconds)}s"
            elif estimated_seconds < 3600:
                minutes = int(estimated_seconds / 60)
                seconds = int(estimated_seconds % 60)
                eta_str = f"{minutes}m {seconds}s"
            else:
                hours = int(estimated_seconds / 3600)
                minutes = int((estimated_seconds % 3600) / 60)
                eta_str = f"{hours}h {minutes}m"
            
            self.progress_bar.setFormat(f"{completed}/{total} - %p% - ETA: {eta_str}")
    
    def _on_batch_progress(self, percentage: int) -> None:
        """Handle batch progress update."""
        # Progress is already shown via item_started
        pass
    
    def _on_batch_error(self, error: str) -> None:
        """Handle batch analysis error."""
        logger.error(f"Batch analysis error: {error}")
        QMessageBox.critical(
            self,
            "Batch Analysis Error",
            f"Batch analysis encountered an error:\n\n{error}"
        )
    
    def _on_batch_finished(self, processed: int, successful: int) -> None:
        """Handle batch analysis completion."""
        # Re-enable UI
        self.analyze_button.setEnabled(bool(self.image_viewer.current_image))
        self.import_button.setEnabled(True)
        self.batch_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - %v/%m")
        
        # Check if stopped early
        was_stopped = processed < self.batch_total_count
        
        # Show summary
        failed = processed - successful
        
        if was_stopped:
            summary = f"Batch analysis stopped!\n\n"
            summary += f"Processed: {processed} of {self.batch_total_count} images\n"
        else:
            summary = f"Batch analysis complete!\n\n"
            summary += f"Total images: {processed}\n"
        
        summary += f"✓ Successful: {successful}\n"
        
        if failed > 0:
            summary += f"✗ Failed: {failed}\n"
            
            # Add details about failed items
            if self.batch_failed_items:
                summary += f"\n❌ Failed items:\n"
                for image_path, filename, error_msg in self.batch_failed_items[:5]:  # Show first 5 errors
                    # Truncate long error messages
                    short_error = error_msg[:60] + "..." if len(error_msg) > 60 else error_msg
                    summary += f"  • {filename}: {short_error}\n"
                
                if len(self.batch_failed_items) > 5:
                    summary += f"  ... and {len(self.batch_failed_items) - 5} more\n"
        
        if was_stopped:
            summary += f"⏸️ Stopped: {self.batch_total_count - processed} not processed\n"
        
        # Add file format details based on checkbox states
        summary += f"\n📄 Results saved for each image:\n"
        if self.write_yaml_checkbox.isVisible() and self.write_yaml_checkbox.isChecked():
            summary += f"  • PhotoPrism YAML sidecar (.yml)\n"
        summary += f"  • Text file (.txt) for backward compatibility\n"
        if self.write_metadata_checkbox.isVisible() and self.write_metadata_checkbox.isChecked():
            summary += f"  • EXIF/IPTC metadata embedded in image\n"
        
        if was_stopped:
            self._update_status(f"⏸️ Batch stopped: {successful}/{processed} successful")
            title = "Batch Analysis Stopped"
        else:
            self._update_status(f"✓ Batch complete: {successful}/{processed} successful")
            title = "Batch Analysis Complete"
        
        # Show summary with retry option if there are failed items
        if self.batch_failed_items:
            dialog = BatchSummaryDialog(title, summary, self.batch_failed_items, self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted and dialog.should_retry:
                # User wants to retry failed items
                self._retry_failed_items()
        else:
            QMessageBox.information(self, title, summary)
        
        # Hide average metrics section
        self.avg_label.setVisible(False)
        
        self.response_preview.clear()
        self.batch_total_count = 0  # Reset counter
        self.batch_completed_count = 0  # Reset time tracking
        self.batch_start_time = 0.0
    
    def _retry_failed_items(self) -> None:
        """Retry processing failed items from the last batch."""
        if not self.batch_failed_items:
            return
        
        # Extract paths from failed items
        failed_paths = [path for path, filename, error in self.batch_failed_items]
        
        # Get the prompt used for the batch (from prompt editor)
        # First, ensure trigger word and prompt are up to date
        self.prompt_editor.refresh_trigger_replacement()
        
        prompt = self.prompt_editor.get_prompt()
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a prompt before retrying.")
            return
        
        # Clear the failed items list (will be repopulated during retry)
        self.batch_failed_items = []
        
        # Reset time tracking for retry
        self.batch_start_time = time.time()
        self.batch_completed_count = 0
        
        # Disable UI during batch analysis
        self.analyze_button.setEnabled(False)
        self.import_button.setEnabled(False)
        self.batch_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(failed_paths))
        self.progress_bar.setValue(0)
        
        # Store total count for completion summary
        self.batch_total_count = len(failed_paths)
        
        logger.info(f"Retrying {len(failed_paths)} failed items")
        
        # Create and start batch worker for failed items
        self.batch_worker = BatchAnalysisWorker(
            failed_paths,
            prompt,
            self.analyzer
        )
        
        self.batch_worker.started.connect(self._on_batch_started)
        self.batch_worker.item_started.connect(self._on_batch_item_started)
        self.batch_worker.item_finished.connect(self._on_batch_item_finished)
        self.batch_worker.item_retry.connect(self._on_batch_item_retry)
        self.batch_worker.progress.connect(self._on_batch_progress)
        self.batch_worker.error.connect(self._on_batch_error)
        self.batch_worker.finished.connect(self._on_batch_finished)
        
        self.batch_worker.start()
    
    def _cancel_analysis(self) -> None:
        """Cancel the current analysis operation."""
        # Check if single image analysis is running
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()
            self.current_worker = None
            
            # Re-enable UI
            self.analyze_button.setEnabled(bool(self.image_viewer.current_image))
            self.import_button.setEnabled(True)
            self.batch_button.setEnabled(True)
            self.cancel_button.setVisible(False)
            self.progress_bar.setVisible(False)
            
            self._update_status("❌ Analysis cancelled")
            logger.info("Single image analysis cancelled by user")
        
        # Check if batch analysis is running
        elif self.batch_worker and self.batch_worker.isRunning():
            # Request graceful stop
            self.batch_worker.stop()
            
            self._update_status("⏸️ Stopping batch analysis...")
            logger.info("Batch analysis stop requested by user")
            
            # Note: UI will be re-enabled when batch_worker.finished signal fires
    
    def _show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config, self)
        
        if dialog.exec():
            # Update config with new settings
            settings = dialog.get_settings()
            self.config.update(**settings)
            save_config()
            
            # Update analyzer  
            old_model = self.config.ollama_model
            self._update_analyzer()
            
            # If model changed, update the selector
            if old_model != self.config.ollama_model:
                self._populate_model_list()
            
            self._update_status("Settings saved")
            logger.info("Settings updated")
    
    def _show_about(self) -> None:
        """Show the about dialog."""
        from ollama_image_analyzer import __version__
        
        QMessageBox.about(
            self,
            "About Ollama Image Analyzer",
            f"<h2>Ollama Image Analyzer</h2>"
            f"<p>Version {__version__}</p>"
            f"<p>A modern cross-platform application for analyzing images "
            f"using Ollama vision models.</p>"
            f"<p><b>Features:</b></p>"
            f"<ul>"
            f"<li>Beautiful dark-themed interface</li>"
            f"<li>Drag-and-drop image support</li>"
            f"<li>Fully customizable prompts</li>"
            f"<li>Remote Ollama server support</li>"
            f"<li>Automatic result saving</li>"
            f"<li>Powerful CLI mode</li>"
            f"</ul>"
            f"<p>Built with PySide6 and Python.</p>"
        )
    
    def closeEvent(self, event) -> None:  # type: ignore
        """Handle window close event."""
        self._save_geometry()
        
        # Stop any running worker
        if self.current_worker and self.current_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Analysis in Progress",
                "An analysis is currently running. Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            self.current_worker.terminate()
            self.current_worker.wait()
        
        event.accept()


class BatchSummaryDialog(QDialog):
    """Dialog to show batch analysis summary with retry option."""
    
    def __init__(
        self, 
        title: str, 
        summary: str, 
        failed_items: list[tuple[Path, str, str]], 
        parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the batch summary dialog.
        
        Args:
            title: Dialog title.
            summary: Summary text to display.
            failed_items: List of (path, filename, error) tuples for failed items.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.failed_items = failed_items
        self.should_retry = False
        
        self.setWindowTitle(title)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Summary message
        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        summary_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(summary_label)
        
        # Buttons
        button_box = QDialogButtonBox()
        
        if failed_items:
            # Add retry button for failed items
            retry_button = button_box.addButton("Retry Failed Items", QDialogButtonBox.ButtonRole.AcceptRole)
            retry_button.setToolTip(f"Retry analyzing the {len(failed_items)} failed image(s)")
            retry_button.clicked.connect(self._on_retry_clicked)
        
        close_button = button_box.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def _on_retry_clicked(self) -> None:
        """Handle retry button clicked."""
        self.should_retry = True
        self.accept()


class OverwriteWarningDialog(QDialog):
    """Dialog to warn user about overwriting existing files."""
    
    def __init__(self, file_names: list[str], parent: Optional[QWidget] = None) -> None:
        """Initialize the overwrite warning dialog.
        
        Args:
            file_names: List of file names that will be overwritten.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.setWindowTitle("Overwrite Existing Files?")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Warning message
        message = QLabel(
            f"<b>Warning:</b> {len(file_names)} analysis file(s) already exist and will be overwritten.\n\n"
            "Do you want to continue?"
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Scrollable list of files
        list_label = QLabel("Files that will be overwritten:")
        layout.addWidget(list_label)
        
        file_list = QListWidget()
        for file_name in sorted(file_names):
            file_list.addItem(file_name)
        layout.addWidget(file_list)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
