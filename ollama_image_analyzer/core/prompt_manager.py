"""Prompt management for Ollama Image Analyzer.

Handles loading, saving, and managing user-editable prompts for image analysis.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompt templates for image analysis."""

    def __init__(self, default_prompt_path: Optional[Path] = None) -> None:
        """
        Initialize the prompt manager.
        
        Args:
            default_prompt_path: Path to the default prompt file.
                                If None, uses 'prompts/default.txt' relative to project root.
        """
        if default_prompt_path is None:
            # Find project root by looking for prompts directory
            current = Path(__file__).resolve()
            while current.parent != current:
                prompts_dir = current / "prompts"
                if prompts_dir.exists():
                    default_prompt_path = prompts_dir / "default.txt"
                    break
                current = current.parent
            
            # Fallback: use relative path
            if default_prompt_path is None or not default_prompt_path.exists():
                default_prompt_path = Path("prompts/default.txt")
        
        self.default_prompt_path = default_prompt_path
        self._current_prompt: Optional[str] = None

    def load_prompt(self, prompt_path: Optional[Path] = None) -> str:
        """
        Load a prompt from file.
        
        Args:
            prompt_path: Path to prompt file. If None, uses default.
            
        Returns:
            The prompt text.
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist.
            IOError: If there's an error reading the file.
        """
        path = prompt_path or self.default_prompt_path
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                prompt = f.read().strip()
            
            if not prompt:
                raise ValueError(f"Prompt file is empty: {path}")
            
            self._current_prompt = prompt
            logger.info(f"Loaded prompt from {path} ({len(prompt)} characters)")
            return prompt
            
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load prompt from {path}: {e}")
            raise IOError(f"Could not read prompt file: {e}") from e

    def save_prompt(self, prompt: str, prompt_path: Optional[Path] = None) -> None:
        """
        Save a prompt to file.
        
        Args:
            prompt: The prompt text to save.
            prompt_path: Path to save to. If None, saves to default location.
            
        Raises:
            IOError: If there's an error writing the file.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Cannot save empty prompt")
        
        path = prompt_path or self.default_prompt_path
        
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(prompt.strip() + "\n")
            
            self._current_prompt = prompt.strip()
            logger.info(f"Saved prompt to {path} ({len(prompt)} characters)")
            
        except Exception as e:
            logger.error(f"Failed to save prompt to {path}: {e}")
            raise IOError(f"Could not write prompt file: {e}") from e

    def get_default_prompt(self) -> str:
        """
        Get the default prompt text.
        
        Returns:
            The default prompt.
        """
        return self.load_prompt(self.default_prompt_path)

    def get_current_prompt(self) -> str:
        """
        Get the currently loaded prompt, or load default if none loaded.
        
        Returns:
            The current prompt text.
        """
        if self._current_prompt is None:
            return self.load_prompt()
        return self._current_prompt

    def reset_to_default(self) -> str:
        """
        Reset to the default prompt.
        
        Returns:
            The default prompt text.
        """
        return self.load_prompt(self.default_prompt_path)

    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate that a prompt is suitable for use.
        
        Args:
            prompt: The prompt to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if not prompt or not prompt.strip():
            logger.warning("Prompt validation failed: empty prompt")
            return False
        
        # Basic validation - ensure it's not too short
        if len(prompt.strip()) < 10:
            logger.warning("Prompt validation failed: too short")
            return False
        
        return True

    def create_prompt_with_context(
        self, 
        base_prompt: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Create a prompt with additional context appended.
        
        Args:
            base_prompt: Base prompt to use. If None, uses current prompt.
            additional_context: Additional instructions to append.
            
        Returns:
            Combined prompt text.
        """
        prompt = base_prompt or self.get_current_prompt()
        
        if additional_context:
            prompt = f"{prompt}\n\n{additional_context}"
        
        return prompt
