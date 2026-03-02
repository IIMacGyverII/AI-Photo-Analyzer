"""Configuration management for Ollama Image Analyzer.

Handles loading and saving application settings using platformdirs
for cross-platform configuration storage.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from platformdirs import user_config_dir, user_data_dir

from ollama_image_analyzer import PACKAGE_NAME

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration settings."""

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llava"
    
    # Paths
    output_directory: Optional[str] = None  # None = save next to image
    prompt_file: str = "prompts/default.txt"
    
    # GUI settings
    window_width: int = 1200
    window_height: int = 800
    last_image_directory: str = ""
    
    # Analysis settings
    timeout_seconds: int = 300
    save_responses: bool = True
    overwrite_existing_files: bool = True  # If False, creates numbered versions (_1, _2, etc.)
    
    # Internal
    _config_dir: Path = field(default_factory=lambda: Path(user_config_dir(PACKAGE_NAME)))
    _data_dir: Path = field(default_factory=lambda: Path(user_data_dir(PACKAGE_NAME)))

    def __post_init__(self) -> None:
        """Ensure directories exist after initialization."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config_file(self) -> Path:
        """Get the path to the configuration file."""
        return self._config_dir / "config.json"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary, excluding internal fields."""
        data = asdict(self)
        # Remove internal fields
        data.pop("_config_dir", None)
        data.pop("_data_dir", None)
        return data

    def save(self) -> None:
        """Save configuration to disk."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from disk, or create default if not found."""
        config = cls()
        
        if not config.config_file.exists():
            logger.info("No configuration file found, using defaults")
            config.save()  # Create default config
            return config
        
        try:
            with open(config.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Update config with loaded values
            for key, value in data.items():
                if hasattr(config, key) and not key.startswith("_"):
                    setattr(config, key, value)
            
            logger.info(f"Configuration loaded from {config.config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}, using defaults")
            return config

    def update(self, **kwargs: Any) -> None:
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key) and not key.startswith("_"):
                setattr(self, key, value)
            else:
                logger.warning(f"Attempted to set unknown config key: {key}")


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = Config.load()
    return _global_config


def save_config() -> None:
    """Save the global configuration to disk."""
    if _global_config is not None:
        _global_config.save()


def reset_config() -> Config:
    """Reset configuration to defaults."""
    global _global_config
    _global_config = Config()
    _global_config.save()
    return _global_config
