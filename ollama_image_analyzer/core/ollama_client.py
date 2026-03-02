"""Ollama client for image analysis.

Provides a clean interface to the Ollama API for analyzing images
with vision models.
"""

import base64
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union, Tuple
from datetime import datetime

import ollama
from ollama import Client
import yaml
import piexif
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of an image analysis."""

    success: bool
    response: str
    model: str
    error: Optional[str] = None
    image_path: Optional[Path] = None
    # Performance metrics
    total_duration: Optional[int] = None  # nanoseconds
    load_duration: Optional[int] = None  # nanoseconds
    prompt_eval_count: Optional[int] = None  # tokens
    prompt_eval_duration: Optional[int] = None  # nanoseconds
    eval_count: Optional[int] = None  # tokens
    eval_duration: Optional[int] = None  # nanoseconds

    @property
    def is_error(self) -> bool:
        """Check if this result represents an error."""
        return not self.success or self.error is not None
    
    @property
    def tokens_per_second(self) -> Optional[float]:
        """Calculate tokens per second for response generation."""
        if self.eval_count and self.eval_duration:
            return self.eval_count / (self.eval_duration / 1_000_000_000)
        return None
    
    @property
    def total_seconds(self) -> Optional[float]:
        """Convert total duration to seconds."""
        if self.total_duration:
            return self.total_duration / 1_000_000_000
        return None


class OllamaAnalyzer:
    """Client for analyzing images with Ollama vision models."""

    # Supported image formats
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llava",
        timeout: int = 300,
    ) -> None:
        """
        Initialize the Ollama analyzer.

        Args:
            host: Ollama server URL (e.g., 'http://localhost:11434')
            model: Vision model name (e.g., 'llava', 'bakllava', 'moondream')
            timeout: Request timeout in seconds
        """
        self.host = host
        self.model = model
        self.timeout = timeout
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get or create the Ollama client."""
        if self._client is None:
            self._client = Client(host=self.host, timeout=self.timeout)
        return self._client

    def _get_numbered_path(self, original_path: Path) -> Path:
        """
        Generate a numbered file path if the original exists.
        
        Args:
            original_path: The original file path.
            
        Returns:
            A new path with a number suffix (e.g., file_1.txt, file_2.txt).
        """
        if not original_path.exists():
            return original_path
        
        stem = original_path.stem
        suffix = original_path.suffix
        parent = original_path.parent
        
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
            # Safety limit to prevent infinite loop
            if counter > 9999:
                raise IOError(f"Too many numbered files for {original_path.name}")

    def test_connection(self) -> bool:
        """
        Test connection to Ollama server.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            # Try to list models to verify connection
            self.client.list()
            logger.info(f"Successfully connected to Ollama at {self.host}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama at {self.host}: {e}")
            return False

    def list_models(self) -> List[str]:
        """
        Get list of available models from Ollama server.

        Returns:
            List of model names.

        Raises:
            ConnectionError: If unable to connect to server.
        """
        try:
            response = self.client.list()
            # Handle different response formats (dict or object with 'models' attribute)
            if hasattr(response, "models"):
                models_data = response.models
            elif isinstance(response, dict):
                models_data = response.get("models", [])
            else:
                models_data = []
            
            # Extract model names - handle both dict and object formats
            models = []
            for model in models_data:
                if hasattr(model, "model"):
                    models.append(model.model)
                elif hasattr(model, "name"):
                    models.append(model.name)
                elif isinstance(model, dict):
                    models.append(model.get("model") or model.get("name", ""))
                else:
                    continue
            
            logger.info(f"Found {len(models)} models on Ollama server")
            return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise ConnectionError(f"Could not retrieve models from {self.host}: {e}") from e

    def get_vision_models(self) -> List[str]:
        """
        Get list of vision-capable models.

        Returns:
            List of vision model names.
        """
        try:
            all_models = self.list_models()
            # Common vision model names/prefixes
            vision_keywords = ["llava", "bakllava", "moondream", "vision", "clip"]
            
            vision_models = [
                model for model in all_models
                if any(keyword in model.lower() for keyword in vision_keywords)
            ]
            
            if not vision_models:
                logger.warning("No obvious vision models found, returning all models")
                return all_models
            
            return vision_models
        except Exception as e:
            logger.error(f"Failed to get vision models: {e}")
            return []

    @staticmethod
    def is_supported_image(file_path: Path) -> bool:
        """
        Check if a file is a supported image format.

        Args:
            file_path: Path to the image file.

        Returns:
            True if supported, False otherwise.
        """
        return file_path.suffix.lower() in OllamaAnalyzer.SUPPORTED_FORMATS

    def _encode_image(self, image_path: Path) -> str:
        """
        Encode image to base64 string.

        Args:
            image_path: Path to the image file.

        Returns:
            Base64-encoded image string.
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        model: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Analyze an image using Ollama vision model.

        Args:
            image_path: Path to the image file.
            prompt: Prompt/instructions for the analysis.
            model: Model to use (if None, uses self.model).

        Returns:
            AnalysisResult with the response or error.
        """
        image_path = Path(image_path)
        model = model or self.model

        # Validate image file
        if not image_path.exists():
            error_msg = f"Image file not found: {image_path}"
            logger.error(error_msg)
            return AnalysisResult(
                success=False,
                response="",
                model=model,
                error=error_msg,
                image_path=image_path,
            )

        if not self.is_supported_image(image_path):
            error_msg = f"Unsupported image format: {image_path.suffix}"
            logger.error(error_msg)
            return AnalysisResult(
                success=False,
                response="",
                model=model,
                error=error_msg,
                image_path=image_path,
            )

        # Perform analysis
        try:
            logger.info(f"Analyzing {image_path.name} with model {model}")
            
            response = self.client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [str(image_path)],
                    }
                ],
            )

            response_text = response["message"]["content"]
            
            # Extract performance metrics
            total_duration = response.get("total_duration")
            load_duration = response.get("load_duration")
            prompt_eval_count = response.get("prompt_eval_count")
            prompt_eval_duration = response.get("prompt_eval_duration")
            eval_count = response.get("eval_count")
            eval_duration = response.get("eval_duration")
            
            # Calculate tokens/sec if available
            if eval_count and eval_duration:
                tokens_per_sec = eval_count / (eval_duration / 1_000_000_000)
                logger.info(f"Analysis complete: {len(response_text)} chars, {eval_count} tokens, {tokens_per_sec:.2f} tok/s")
            else:
                logger.info(f"Analysis complete: {len(response_text)} chars")

            return AnalysisResult(
                success=True,
                response=response_text,
                model=model,
                image_path=image_path,
                total_duration=total_duration,
                load_duration=load_duration,
                prompt_eval_count=prompt_eval_count,
                prompt_eval_duration=prompt_eval_duration,
                eval_count=eval_count,
                eval_duration=eval_duration,
            )

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(f"Error analyzing {image_path.name}: {e}", exc_info=True)
            return AnalysisResult(
                success=False,
                response="",
                model=model,
                error=error_msg,
                image_path=image_path,
            )

    def validate_response(
        self,
        response: str,
        min_chars: int = 20,
        max_words: int = 10000,
        min_avg_word_length: float = 2.0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a response looks reasonable and not corrupted.

        Args:
            response: The response text to validate.
            min_chars: Minimum character count (default 20).
            max_words: Maximum word count to prevent runaway generation (default 10000).
            min_avg_word_length: Minimum average word length to detect gibberish (default 2.0).

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
        """
        if not response or not response.strip():
            return False, "Response is empty"
        
        response = response.strip()
        
        # Check minimum length
        if len(response) < min_chars:
            return False, f"Response too short ({len(response)} chars, minimum {min_chars})"
        
        # Count words
        words = response.split()
        word_count = len(words)
        
        # Check maximum word count
        if word_count > max_words:
            return False, f"Response too long ({word_count} words, maximum {max_words})"
        
        # Check for gibberish - calculate average word length
        if words:
            # Filter out very short "words" (likely punctuation)
            meaningful_words = [w for w in words if len(w) > 1]
            if meaningful_words:
                avg_word_length = sum(len(w) for w in meaningful_words) / len(meaningful_words)
                if avg_word_length < min_avg_word_length:
                    return False, f"Response appears to be gibberish (avg word length: {avg_word_length:.1f})"
        
        # Check for excessive non-alphanumeric characters (gibberish detection)
        alphanumeric_chars = sum(c.isalnum() or c.isspace() for c in response)
        if alphanumeric_chars / len(response) < 0.7:  # Less than 70% normal characters
            return False, "Response contains excessive special characters (possible gibberish)"
        
        # Check for repetitive patterns (e.g., "word word word word...")
        if len(words) >= 10:
            # Check if more than 50% of words are the same
            unique_words = set(w.lower() for w in words)
            if len(unique_words) / len(words) < 0.3:
                return False, "Response contains excessive repetition"
        
        return True, None

    def save_result(
        self,
        result: AnalysisResult,
        output_path: Optional[Path] = None,
        overwrite: bool = True,
    ) -> Path:
        """
        Save analysis result to a text file.

        Args:
            result: The analysis result to save.
            output_path: Where to save (if None, saves next to image with .txt extension).
            overwrite: If False and file exists, will create numbered version (file_1.txt, file_2.txt, etc.).

        Returns:
            Path where the result was saved.

        Raises:
            IOError: If unable to save the file.
            ValueError: If the result is invalid or response validation fails.
        """
        if not result.success:
            raise ValueError("Cannot save a failed analysis result")

        # Validate response content before saving
        is_valid, validation_error = self.validate_response(result.response)
        if not is_valid:
            error_msg = f"Response validation failed: {validation_error}"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        # Determine output path
        if output_path is None:
            if result.image_path is None:
                raise ValueError("Cannot determine output path: no image_path in result")
            output_path = result.image_path.with_suffix(".txt")

        # Check if file exists and handle accordingly
        if not overwrite and output_path.exists():
            output_path = self._get_numbered_path(output_path)
            logger.info(f"File exists, using numbered path: {output_path}")

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.response)
            
            logger.info(f"Saved analysis result to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save result to {output_path}: {e}")
            raise IOError(f"Could not save analysis result: {e}") from e
    
    def save_yaml_sidecar(
        self,
        result: AnalysisResult,
        output_path: Optional[Path] = None,
        overwrite: bool = True,
    ) -> Path:
        """
        Save analysis result as PhotoPrism-compatible YAML sidecar file.

        Args:
            result: The analysis result to save.
            output_path: Where to save (if None, saves next to image as .yml).
            overwrite: If False and file exists, will create numbered version (file.jpg_1.yml, file.jpg_2.yml, etc.).

        Returns:
            Path where the YAML file was saved.

        Raises:
            IOError: If unable to save the file.
            ValueError: If the result is invalid or response validation fails.
        """
        if not result.success:
            raise ValueError("Cannot save a failed analysis result")

        # Validate response content before saving
        is_valid, validation_error = self.validate_response(result.response)
        if not is_valid:
            error_msg = f"Response validation failed: {validation_error}"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        # Determine output path
        if output_path is None:
            if result.image_path is None:
                raise ValueError("Cannot determine output path: no image_path in result")
            output_path = result.image_path.with_suffix(result.image_path.suffix + ".yml")

        # Check if file exists and handle accordingly
        if not overwrite and output_path.exists():
            output_path = self._get_numbered_path(output_path)
            logger.info(f"YAML file exists, using numbered path: {output_path}")

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create PhotoPrism-compatible YAML structure
            yaml_data = {
                "Title": result.image_path.stem if result.image_path else "",
                "Description": result.response,
                "TakenAt": datetime.now().isoformat(),
                "Details": {
                    "AI_Model": result.model,
                    "AI_Generated": True,
                    "Processing_Time": result.total_seconds if result.total_seconds else None,
                }
            }
            
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"Saved YAML sidecar to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save YAML sidecar to {output_path}: {e}")
            raise IOError(f"Could not save YAML sidecar: {e}") from e
    
    def write_to_image_metadata(
        self,
        result: AnalysisResult,
        backup: bool = True,
    ) -> bool:
        """
        Write description directly to image file's EXIF/IPTC metadata.

        Args:
            result: The analysis result to write.
            backup: Whether to create a backup before modifying.

        Returns:
            True if successful, False otherwise.

        Raises:
            IOError: If unable to modify the image file.
        """
        if not result.success or not result.image_path:
            raise ValueError("Cannot write metadata: invalid result or no image path")

        if not result.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {result.image_path}")

        try:
            # Create backup if requested
            if backup:
                backup_path = result.image_path.with_suffix(result.image_path.suffix + ".bak")
                if not backup_path.exists():
                    import shutil
                    shutil.copy2(result.image_path, backup_path)
                    logger.info(f"Created backup at {backup_path}")

            # Open image
            img = Image.open(result.image_path)
            
            # Try to get existing EXIF data
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            if "exif" in img.info:
                try:
                    exif_dict = piexif.load(img.info["exif"])
                except Exception as e:
                    logger.warning(f"Could not load existing EXIF data: {e}, creating new")
            
            # Write description to EXIF ImageDescription tag (0x010E)
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = result.response.encode('utf-8')
            
            # Write to UserComment in EXIF (for more compatibility)
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = result.response.encode('utf-8')
            
            # Compile EXIF data
            exif_bytes = piexif.dump(exif_dict)
            
            # Save image with new EXIF data
            img.save(result.image_path, exif=exif_bytes)
            
            logger.info(f"Wrote metadata to {result.image_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to write metadata to {result.image_path}: {e}")
            raise IOError(f"Could not write image metadata: {e}") from e
