"""Background worker for batch image analysis."""

import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QThread, Signal

from ollama_image_analyzer.core import OllamaAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


class BatchAnalysisWorker(QThread):
    """Background worker thread for batch analyzing multiple images."""

    # Signals
    started = Signal()
    finished = Signal(int, int)  # total, successful
    item_started = Signal(int, int, str, object)  # current, total, filename, path
    item_finished = Signal(AnalysisResult)
    item_retry = Signal(str, str)  # filename, error_message (emitted when retrying)
    progress = Signal(int)  # Progress percentage (0-100)
    error = Signal(str)  # Error message

    def __init__(
        self,
        image_paths: List[Path],
        prompt: str,
        analyzer: OllamaAnalyzer,
        parent: Optional[QThread] = None,
    ) -> None:
        """
        Initialize the batch analysis worker.
        
        Args:
            image_paths: List of image paths to analyze.
            prompt: Analysis prompt.
            analyzer: OllamaAnalyzer instance.
            parent: Parent object.
        """
        super().__init__(parent)
        
        self.image_paths = image_paths
        self.prompt = prompt
        self.analyzer = analyzer
        self._should_stop = False
    
    def stop(self) -> None:
        """Request the worker to stop processing."""
        self._should_stop = True
    
    def run(self) -> None:
        """Run the batch analysis in a background thread."""
        total = len(self.image_paths)
        successful = 0
        processed = 0
        
        try:
            self.started.emit()
            logger.info(f"Starting batch analysis of {total} images")
            
            for index, image_path in enumerate(self.image_paths):
                # Check if we should stop
                if self._should_stop:
                    logger.info(f"Batch analysis stopped by user after {processed} images")
                    break
                
                # Emit progress
                current = index + 1
                self.item_started.emit(current, total, image_path.name, image_path)
                progress_pct = int((current / total) * 100)
                self.progress.emit(progress_pct)
                
                try:
                    # Perform analysis
                    logger.info(f"Analyzing {current}/{total}: {image_path.name}")
                    result = self.analyzer.analyze_image(image_path, self.prompt)
                    
                    # If analysis failed, retry once
                    if not result.success:
                        error_msg = result.error or "Unknown error"
                        logger.warning(f"Analysis failed for {image_path.name}: {error_msg}. Retrying...")
                        self.item_retry.emit(image_path.name, error_msg)
                        
                        # Retry the analysis
                        result = self.analyzer.analyze_image(image_path, self.prompt)
                        
                        if result.success:
                            logger.info(f"Retry successful for {image_path.name}")
                        else:
                            logger.error(f"Retry also failed for {image_path.name}: {result.error}")
                    
                    processed += 1
                    
                    if result.success:
                        successful += 1
                        logger.info(f"Analysis successful: {image_path.name}")
                    else:
                        logger.error(f"Analysis failed for {image_path.name}: {result.error}")
                    
                    # Emit result for this item
                    self.item_finished.emit(result)
                
                except Exception as e:
                    # Exception during analysis - retry once
                    logger.error(f"Exception analyzing {image_path.name}: {e}. Retrying...", exc_info=True)
                    self.item_retry.emit(image_path.name, str(e))
                    
                    try:
                        # Retry the analysis
                        result = self.analyzer.analyze_image(image_path, self.prompt)
                        
                        if result.success:
                            successful += 1
                            logger.info(f"Retry successful for {image_path.name}")
                        else:
                            logger.error(f"Retry also failed for {image_path.name}: {result.error}")
                        
                        processed += 1
                        self.item_finished.emit(result)
                        
                    except Exception as retry_error:
                        logger.error(f"Retry also threw exception for {image_path.name}: {retry_error}", exc_info=True)
                        processed += 1
                        error_result = AnalysisResult(
                            success=False,
                            response="",
                            model=self.analyzer.model,
                            error=f"Failed twice: {str(e)}; {str(retry_error)}",
                            image_path=image_path
                        )
                        self.item_finished.emit(error_result)
            
            # Batch complete (or stopped)
            if self._should_stop:
                logger.info(f"Batch analysis stopped: {successful}/{processed} successful (out of {total} total)")
            else:
                logger.info(f"Batch analysis complete: {successful}/{total} successful")
            
            self.finished.emit(processed, successful)
        
        except Exception as e:
            logger.error(f"Batch worker exception: {e}", exc_info=True)
            self.error.emit(f"Batch analysis error: {str(e)}")
            self.finished.emit(total, successful)
