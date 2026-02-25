"""Background worker for non-blocking image analysis."""

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal

from ollama_image_analyzer.core import OllamaAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


class AnalysisWorker(QThread):
    """Background worker thread for analyzing images."""

    # Signals
    started = Signal()
    finished = Signal(AnalysisResult)
    progress = Signal(str)  # Progress message
    error = Signal(str)  # Error message

    def __init__(
        self,
        image_path: Path,
        prompt: str,
        analyzer: OllamaAnalyzer,
        parent: Optional[QThread] = None,
    ) -> None:
        """
        Initialize the analysis worker.
        
        Args:
            image_path: Path to the image to analyze.
            prompt: Analysis prompt.
            analyzer: OllamaAnalyzer instance.
            parent: Parent object.
        """
        super().__init__(parent)
        
        self.image_path = image_path
        self.prompt = prompt
        self.analyzer = analyzer
    
    def run(self) -> None:
        """Run the analysis in a background thread."""
        try:
            self.started.emit()
            
            logger.info(f"Starting analysis of {self.image_path.name}")
            self.progress.emit(f"Analyzing {self.image_path.name}...")
            
            # Perform analysis
            result = self.analyzer.analyze_image(
                self.image_path,
                self.prompt
            )
            
            if result.success:
                logger.info(f"Analysis complete: {len(result.response)} chars")
                self.progress.emit("Analysis complete!")
            else:
                logger.error(f"Analysis failed: {result.error}")
                self.error.emit(result.error or "Unknown error")
            
            # Emit result
            self.finished.emit(result)
        
        except Exception as e:
            logger.error(f"Worker exception: {e}", exc_info=True)
            error_msg = f"Analysis error: {str(e)}"
            self.error.emit(error_msg)
            
            # Emit failed result
            result = AnalysisResult(
                success=False,
                response="",
                model=self.analyzer.model,
                error=error_msg,
                image_path=self.image_path
            )
            self.finished.emit(result)
