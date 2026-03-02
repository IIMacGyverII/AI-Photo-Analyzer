"""Prompt editor widget for customizing analysis prompts."""

import logging
from pathlib import Path
from typing import Optional

from platformdirs import user_data_dir
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ollama_image_analyzer import PACKAGE_NAME
from ollama_image_analyzer.core import PromptManager

logger = logging.getLogger(__name__)


class PromptEditor(QWidget):
    """Widget for editing and managing analysis prompts."""

    # Signal emitted when prompt changes
    prompt_changed = Signal(str)
    # Signal emitted when preset changes (emits preset filename without extension)
    preset_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the prompt editor."""
        super().__init__(parent)
        
        self.prompt_manager = PromptManager()
        self._current_preset_path: Optional[Path] = None
        self._base_prompt: Optional[str] = None  # Store original prompt for trigger replacement
        
        # Set up user presets directory (writable location for custom presets)
        self._user_presets_dir = Path(user_data_dir(PACKAGE_NAME)) / "prompts"
        self._user_presets_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"User presets directory: {self._user_presets_dir}")
        
        self._setup_ui()
        self._refresh_presets()
        self._load_default_prompt()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Group box
        group = QGroupBox("Prompt Enhancer")
        group_layout = QVBoxLayout(group)
        
        # Preset selector row
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset:")
        preset_layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        self.preset_combo.setToolTip("Select a prompt preset")
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        preset_layout.addWidget(self.preset_combo, 1)
        
        # Refresh presets button
        self.refresh_presets_button = QPushButton("🔄")
        self.refresh_presets_button.setToolTip("Refresh preset list")
        self.refresh_presets_button.setMaximumWidth(40)
        self.refresh_presets_button.clicked.connect(self._refresh_presets)
        preset_layout.addWidget(self.refresh_presets_button)
        
        group_layout.addLayout(preset_layout)
        
        # Model type selector (hidden by default, shown only for AI-Toolkit preset)
        self.model_type_layout = QHBoxLayout()
        self.model_type_label = QLabel("Model Type:")
        self.model_type_layout.addWidget(self.model_type_label)
        
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["FLUX", "SD3", "SDXL", "SD 1.5", "Pony Diffusion", "LTX / LTX-2", "Generic"])
        self.model_type_combo.setToolTip("Select the diffusion model type for optimized captions")
        self.model_type_combo.currentTextChanged.connect(self._on_model_type_changed)
        self.model_type_layout.addWidget(self.model_type_combo, 1)
        
        group_layout.addLayout(self.model_type_layout)
        
        # Hide model type selector by default
        self.model_type_label.hide()
        self.model_type_combo.hide()
        
        # Trigger word input (hidden by default, shown only for AI-Toolkit preset)
        self.trigger_layout = QHBoxLayout()
        self.trigger_label = QLabel("Trigger Word:")
        self.trigger_layout.addWidget(self.trigger_label)
        
        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("Leave blank for generic captions, or enter trigger word...")
        self.trigger_input.setToolTip("Enter the trigger word to replace [trigger] in the prompt")
        self.trigger_input.textChanged.connect(self._on_trigger_changed)
        self.trigger_layout.addWidget(self.trigger_input, 1)
        
        group_layout.addLayout(self.trigger_layout)
        
        # Hide trigger input by default
        self.trigger_label.hide()
        self.trigger_input.hide()
        
        # Prompt text editor
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your custom prompt here...")
        self.prompt_edit.setMinimumHeight(200)
        self.prompt_edit.textChanged.connect(self._on_prompt_changed)
        group_layout.addWidget(self.prompt_edit)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Save as Preset button
        self.save_preset_button = QPushButton("💾 Save as Preset")
        self.save_preset_button.setToolTip("Save current prompt as a new preset")
        self.save_preset_button.clicked.connect(self._save_as_preset)
        button_layout.addWidget(self.save_preset_button)
        
        # Load button (from any file)
        self.load_button = QPushButton("📂 Load File")
        self.load_button.setToolTip("Load prompt from any file")
        self.load_button.clicked.connect(self._load_prompt)
        button_layout.addWidget(self.load_button)
        
        # Reset button
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setToolTip("Reset to default prompt")
        self.reset_button.clicked.connect(self._reset_prompt)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        # Character count label
        self.char_count_label = QLabel()
        self.char_count_label.setObjectName("subtitleLabel")
        button_layout.addWidget(self.char_count_label)
        
        group_layout.addLayout(button_layout)
        layout.addWidget(group)
    
    def _load_default_prompt(self) -> None:
        """Load the default prompt."""
        try:
            prompt = self.prompt_manager.get_current_prompt()
            self._base_prompt = prompt
            self.prompt_edit.setPlainText(prompt)
            self._current_preset_path = self.prompt_manager.default_prompt_path
            self._update_char_count()
            # Update combo box selection
            self._update_preset_selection()
            self._update_trigger_visibility()
        except Exception as e:
            logger.error(f"Failed to load default prompt: {e}")
            self.prompt_edit.setPlainText("Describe this image in detail.")
    
    def _refresh_presets(self) -> None:
        """Refresh the list of available presets from both bundled and user directories."""
        try:
            # Find bundled prompts directory
            bundled_prompts_dir = Path("prompts")
            if not bundled_prompts_dir.exists():
                # Try relative to package
                for parent in Path(__file__).parents:
                    test_dir = parent / "prompts"
                    if test_dir.exists():
                        bundled_prompts_dir = test_dir
                        break
            
            # Block signals to prevent triggering on_preset_selected
            self.preset_combo.blockSignals(True)
            
            # Clear and repopulate
            self.preset_combo.clear()
            
            # Collect presets from both locations
            preset_files = []
            
            # Add bundled presets (built-in, read-only)
            if bundled_prompts_dir.exists():
                preset_files.extend(sorted(bundled_prompts_dir.glob("*.txt")))
            
            # Add user presets (custom, writable)
            if self._user_presets_dir.exists():
                user_preset_files = sorted(self._user_presets_dir.glob("*.txt"))
                # Mark user presets with their full path to distinguish them
                preset_files.extend(user_preset_files)
            
            # Remove duplicates (prefer user presets over bundled)
            seen_names = set()
            unique_presets = []
            for preset_file in reversed(preset_files):  # Reverse so user presets are checked first
                stem = preset_file.stem
                if stem not in seen_names:
                    seen_names.add(stem)
                    unique_presets.append(preset_file)
            
            unique_presets.reverse()  # Restore original order
            
            for preset_file in unique_presets:
                # Skip AI Toolkit variant files (they're accessed via Model Type dropdown)
                # Keep ai_toolkit.txt, but skip ai_toolkit_flux.txt, ai_toolkit_sdxl.txt, etc.
                if preset_file.stem.startswith("ai_toolkit_"):
                    continue
                
                # Use filename without extension as display name
                display_name = preset_file.stem.replace("_", " ").title()
                
                # Add indicator for user presets
                if preset_file.parent == self._user_presets_dir:
                    display_name += " ★"  # Star to indicate custom preset
                
                self.preset_combo.addItem(display_name, preset_file)
            
            # Restore signals
            self.preset_combo.blockSignals(False)
            
            # Update selection to match current preset
            self._update_preset_selection()
            
            logger.info(f"Refreshed {self.preset_combo.count()} presets (bundled + user)")
            
        except Exception as e:
            logger.error(f"Failed to refresh presets: {e}")
    
    def _update_preset_selection(self) -> None:
        """Update the combo box to match the current preset."""
        if self._current_preset_path is None:
            return
        
        # Find the index of the current preset
        for i in range(self.preset_combo.count()):
            preset_path = self.preset_combo.itemData(i)
            if preset_path and Path(preset_path) == self._current_preset_path:
                self.preset_combo.blockSignals(True)
                self.preset_combo.setCurrentIndex(i)
                self.preset_combo.blockSignals(False)
                break
    
    def _on_preset_selected(self, index: int) -> None:
        """Handle preset selection from combo box."""
        if index < 0:
            return
        
        preset_path = self.preset_combo.itemData(index)
        if not preset_path:
            return
        
        try:
            self._current_preset_path = Path(preset_path)
            
            # For AI Toolkit, load the appropriate variant based on model type
            if self._current_preset_path.stem == "ai_toolkit":
                self._load_ai_toolkit_variant()
            else:
                prompt = self.prompt_manager.load_prompt(Path(preset_path))
                self._base_prompt = prompt
            
            # Update trigger visibility and apply trigger replacement if needed
            self._update_trigger_visibility()
            self._apply_trigger_replacement()
            
            # Emit preset changed signal
            self.preset_changed.emit(self._current_preset_path.stem)
            
            logger.info(f"Loaded preset: {preset_path}")
        except Exception as e:
            logger.error(f"Failed to load preset: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load preset:\n{str(e)}"
            )
    
    def _save_as_preset(self) -> None:
        """Save the current prompt as a new preset in user directory."""
        prompt = self.get_prompt()
        
        if not prompt.strip():
            QMessageBox.warning(
                self,
                "Warning",
                "Cannot save an empty prompt."
            )
            return
        
        # Ask for preset name
        preset_name, ok = QInputDialog.getText(
            self,
            "Save as Preset",
            "Enter a name for this preset:",
            text="my_custom_prompt"
        )
        
        if not ok or not preset_name.strip():
            return
        
        # Clean up the name
        preset_name = preset_name.strip().replace(" ", "_").lower()
        if not preset_name.endswith(".txt"):
            preset_name += ".txt"
        
        # Always save to user presets directory (writable location)
        preset_path = self._user_presets_dir / preset_name
        
        # Check if file exists
        if preset_path.exists():
            reply = QMessageBox.question(
                self,
                "Overwrite Preset",
                f"Preset '{preset_name}' already exists.\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            self.prompt_manager.save_prompt(prompt, preset_path)
            self._current_preset_path = preset_path
            self._refresh_presets()
            
            QMessageBox.information(
                self,
                "Success",
                f"Preset saved as:\n{preset_name}\n\nLocation: {preset_path.parent.name}/"
            )
        except Exception as e:
            logger.error(f"Failed to save preset: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save preset:\n{str(e)}"
            )
    
    def _on_prompt_changed(self) -> None:
        """Handle prompt text changes."""
        self._update_char_count()
        self.prompt_changed.emit(self.get_prompt())
    
    def _on_trigger_changed(self) -> None:
        """Handle trigger word changes."""
        self._apply_trigger_replacement()
    
    def _load_ai_toolkit_variant(self) -> None:
        """Load the appropriate AI Toolkit prompt variant based on selected model type."""
        model_type = self.model_type_combo.currentText()
        
        # Map model type to filename
        model_map = {
            "FLUX": "ai_toolkit_flux.txt",
            "SD3": "ai_toolkit_sd3.txt",
            "SDXL": "ai_toolkit_sdxl.txt",
            "SD 1.5": "ai_toolkit_sd15.txt",
            "Pony Diffusion": "ai_toolkit_pony.txt",
            "LTX / LTX-2": "ai_toolkit_ltx.txt",
            "Generic": "ai_toolkit.txt"
        }
        
        filename = model_map.get(model_type, "ai_toolkit.txt")
        
        # Find prompts directory
        prompts_dir = Path("prompts")
        if not prompts_dir.exists():
            for parent in Path(__file__).parents:
                test_dir = parent / "prompts"
                if test_dir.exists():
                    prompts_dir = test_dir
                    break
        
        variant_path = prompts_dir / filename
        
        try:
            if variant_path.exists():
                prompt = self.prompt_manager.load_prompt(variant_path)
                self._base_prompt = prompt
                logger.info(f"Loaded AI Toolkit variant: {filename}")
            else:
                logger.warning(f"AI Toolkit variant not found: {filename}, using default")
                # Fall back to generic ai_toolkit.txt
                default_path = prompts_dir / "ai_toolkit.txt"
                if default_path.exists():
                    prompt = self.prompt_manager.load_prompt(default_path)
                    self._base_prompt = prompt
        except Exception as e:
            logger.error(f"Failed to load AI Toolkit variant: {e}")
    
    def _update_trigger_visibility(self) -> None:
        """Show or hide trigger word input and model type selector based on current preset."""
        if self._current_preset_path and self._current_preset_path.stem == "ai_toolkit":
            self.trigger_label.show()
            self.trigger_input.show()
            self.model_type_label.show()
            self.model_type_combo.show()
        else:
            self.trigger_label.hide()
            self.trigger_input.hide()
            self.trigger_input.clear()
            self.model_type_label.hide()
            self.model_type_combo.hide()
    
    def _on_model_type_changed(self) -> None:
        """Handle model type selection changes."""
        if self._current_preset_path and self._current_preset_path.stem == "ai_toolkit":
            # Reload the appropriate prompt variant
            self._load_ai_toolkit_variant()
            self._apply_trigger_replacement()
    
    def _apply_trigger_replacement(self) -> None:
        """Apply trigger word replacement to the prompt."""
        if not self._base_prompt:
            return
        
        # Check if this is the AI-Toolkit preset
        if self._current_preset_path and self._current_preset_path.stem == "ai_toolkit":
            trigger_word = self.trigger_input.text().strip()
            
            if trigger_word:
                # Replace [trigger] placeholder with actual trigger word
                updated_prompt = self._base_prompt.replace("[trigger]", trigger_word)
            else:
                # Use base prompt as-is (contains [trigger] placeholder)
                updated_prompt = self._base_prompt
            
            # Block signals to prevent recursion
            self.prompt_edit.blockSignals(True)
            self.prompt_edit.setPlainText(updated_prompt)
            self.prompt_edit.blockSignals(False)
            self._update_char_count()
        else:
            # For other presets, just use the base prompt
            self.prompt_edit.blockSignals(True)
            self.prompt_edit.setPlainText(self._base_prompt)
            self.prompt_edit.blockSignals(False)
            self._update_char_count()
    
    def _update_char_count(self) -> None:
        """Update the character count display."""
        text = self.prompt_edit.toPlainText()
        char_count = len(text)
        word_count = len(text.split())
        self.char_count_label.setText(f"{char_count} chars, {word_count} words")
    
    def _load_prompt(self) -> None:
        """Load a prompt from any file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Prompt",
            "prompts",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            prompt = self.prompt_manager.load_prompt(Path(file_path))
            self._base_prompt = prompt
            self._current_preset_path = Path(file_path)
            self._update_preset_selection()
            self._update_trigger_visibility()
            self._apply_trigger_replacement()
            
            QMessageBox.information(
                self,
                "Success",
                f"Prompt loaded from:\n{file_path}"
            )
        except Exception as e:
            logger.error(f"Failed to load prompt: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load prompt:\n{str(e)}"
            )
    
    def _reset_prompt(self) -> None:
        """Reset to the default prompt."""
        reply = QMessageBox.question(
            self,
            "Reset Prompt",
            "Reset to the default prompt?\nAny unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                prompt = self.prompt_manager.reset_to_default()
                self._base_prompt = prompt
                self.prompt_edit.setPlainText(prompt)
                self._current_preset_path = self.prompt_manager.default_prompt_path
                self._update_preset_selection()
                self._update_trigger_visibility()
            except Exception as e:
                logger.error(f"Failed to reset prompt: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to reset prompt:\n{str(e)}"
                )
    
    def get_prompt(self) -> str:
        """Get the current prompt text."""
        return self.prompt_edit.toPlainText().strip()
    
    def refresh_trigger_replacement(self) -> None:
        """Refresh trigger word replacement to ensure it's up to date.
        
        This should be called before getting the prompt for batch operations
        to ensure any trigger word changes are properly applied.
        """
        if self._current_preset_path and self._current_preset_path.stem == "ai_toolkit":
            # Re-apply trigger replacement with current trigger word
            self._apply_trigger_replacement()
            logger.debug(f"Refreshed trigger replacement: trigger='{self.trigger_input.text().strip()}'")
    
    def get_current_preset_name(self) -> str:
        """Get the current preset name (stem without extension)."""
        if self._current_preset_path:
            return self._current_preset_path.stem
        return "default"
    
    def set_prompt(self, prompt: str) -> None:
        """Set the prompt text."""
        self.prompt_edit.setPlainText(prompt)
