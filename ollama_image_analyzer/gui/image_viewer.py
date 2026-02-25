"""Image viewer widget with drag-and-drop support."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy

logger = logging.getLogger(__name__)


class ImageViewer(QWidget):
    """Widget for displaying images with drag-and-drop support."""

    # Signal emitted when an image is loaded
    image_loaded = Signal(Path)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the image viewer."""
        super().__init__(parent)
        
        self._current_image: Optional[Path] = None
        self._pixmap: Optional[QPixmap] = None
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #181825;
                border: 2px dashed #45475a;
                border-radius: 8px;
                color: #6c7086;
                font-size: 11pt;
            }
        """)
        
        # Default text
        self._show_placeholder()
        
        layout.addWidget(self.image_label)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
    
    def _show_placeholder(self) -> None:
        """Show placeholder text when no image is loaded."""
        self.image_label.setText(
            "📷\n\nDrag & Drop Image Here\n\nor click Import Image button\n\n"
            "Supported: JPG, PNG, WEBP, GIF"
        )
        self.image_label.setPixmap(QPixmap())  # Clear pixmap
    
    def load_image(self, image_path: Path) -> bool:
        """
        Load and display an image.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            pixmap = QPixmap(str(image_path))
            
            if pixmap.isNull():
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            self._pixmap = pixmap
            self._current_image = image_path
            
            # Scale pixmap to fit label while maintaining aspect ratio
            self._update_display()
            
            logger.info(f"Loaded image: {image_path.name}")
            self.image_loaded.emit(image_path)
            return True
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return False
    
    def _update_display(self) -> None:
        """Update the displayed image to fit the current widget size."""
        if self._pixmap is None:
            return
        
        # Scale pixmap to fit label
        scaled_pixmap = self._pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event) -> None:  # type: ignore
        """Handle resize events to rescale the image."""
        super().resizeEvent(event)
        if self._pixmap is not None:
            self._update_display()
    
    def clear(self) -> None:
        """Clear the current image."""
        self._pixmap = None
        self._current_image = None
        self._show_placeholder()
    
    @property
    def current_image(self) -> Optional[Path]:
        """Get the currently displayed image path."""
        return self._current_image
    
    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if at least one URL is an image file
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = Path(url.toLocalFile())
                    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
                        event.acceptProposedAction()
                        self.image_label.setStyleSheet("""
                            QLabel {
                                background-color: #1e2e3e;
                                border: 2px dashed #89b4fa;
                                border-radius: 8px;
                                color: #89b4fa;
                                font-size: 11pt;
                            }
                        """)
                        return
        event.ignore()
    
    def dragLeaveEvent(self, event) -> None:  # type: ignore
        """Handle drag leave event."""
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #181825;
                border: 2px dashed #45475a;
                border-radius: 8px;
                color: #6c7086;
                font-size: 11pt;
            }
        """)
    
    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event."""
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #181825;
                border: 2px dashed #45475a;
                border-radius: 8px;
                color: #6c7086;
                font-size: 11pt;
            }
        """)
        
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = Path(url.toLocalFile())
                    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
                        self.load_image(file_path)
                        event.acceptProposedAction()
                        return
        
        event.ignore()
