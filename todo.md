- Non-blocking UI: Ollama call runs in a background QThread with progress feedback
- Auto-save .txt with identical base name (image.jpg → image.txt)
- Full error handling and helpful messages

### Mandatory Tech Stack (2026 best practice)
- Python 3.12+
- GUI: PySide6 (Qt6)
- CLI: Typer (with rich help, colors, progress)
- Ollama: official `ollama` package (`ollama.Client`)
- Config: platformdirs + JSON
- Images: Pillow + PySide6 native
- Threading: QThread + pyqtSignal for GUI
- Packaging: PyInstaller (onefile + windowed for GUI, separate CLI if needed)
- Structure: clean package layout with core/, gui/, cli/

### Strict Development Process
1. FIRST ACTION: Create a file `todo.md` in the project root using the EXACT content I provide below.
2. Work strictly top-to-bottom through the todo.md list.
3. For every completed task:
 - Update todo.md → change [ ] to [x] and add a one-line note
 - Create or edit the files with FULL correct code
 - Show me a short summary of what was done
4. After each major section (Project Setup, Core, CLI, GUI, Packaging, Docs) say exactly:  
 `=== SECTION COMPLETE: [Section Name] ===`
5. At the very end create a complete README.md with screenshots descriptions, usage examples, and build instructions for all three OS.

Here is the EXACT content to put in todo.md (copy verbatim):

```markdown
# Ollama Image Analyzer - TODO List

**Goal:** Beautiful cross-platform GUI + CLI app for detailed image description using any Ollama vision model.

## 1. Project Initialization
- [x] Create full folder structure (ollama_image_analyzer/core, cli, gui, prompts/, tests/) ✓ Complete package structure
- [x] pyproject.toml with all dependencies (pyside6, ollama, typer[all], platformdirs, pillow) ✓ All deps configured
- [x] .gitignore and basic README skeleton ✓ Created
- [x] requirements.txt as fallback ✓ Created with all core dependencies

## 2. Core Layer
- [x] config.py – load/save settings using platformdirs ✓ Full Config class with JSON storage
- [x] prompt_manager.py – load/save user prompt (default in prompts/default.txt) ✓ Complete with validation
- [x] ollama_client.py – class with analyze_image(image_path_or_bytes, prompt) using ollama.Client, error handling, model listing ✓ Full OllamaAnalyzer with AnalysisResult
- [x] logging setup ✓ logging_config.py with file and console handlers

## 3. CLI
- [x] cli/main.py – Typer app with `analyze` command supporting multiple images, all options ✓ Full CLI with rich output, progress bars, models command
- [x] __main__.py – detect CLI vs GUI mode automatically ✓ Smart mode detection

## 4. GUI (Modern & Polished)
- [x] Apply beautiful dark QSS stylesheet (modern look, rounded buttons, clean fonts) ✓ Complete Catppuccin-inspired theme
- [x] Main window with splitter: left = image preview (drag & drop supported), right = prompt enhancer editor + controls ✓ Full MainWindow
- [x] ImageViewer widget (QLabel + drag-drop) ✓ With visual feedback
- [x] PromptEditor widget with Save/Load/Reset ✓ Character count, file operations
- [x] Settings dialog with host, model selector + refresh button ✓ Full SettingsDialog with test connection
- [x] Background worker (QThread) for analysis ✓ AnalysisWorker with signals
- [x] Progress bar + status messages ✓ Integrated in MainWindow
- [x] Auto-save .txt on success + preview of response ✓ Complete
- [x] Keyboard shortcuts and tooltips ✓ Ctrl+O, Ctrl+,, tooltips throughout

## 5. Integration & Polish
- [x] Connect GUI and CLI to same core ✓ Shared core module used by both
- [x] Input validation (supported image formats, Ollama connection test) ✓ Validation in OllamaAnalyzer, Settings dialog test connection
- [x] Nice icons / status indicators ✓ Emoji icons, status messages, progress feedback
- [x] Handle large images gracefully ✓ Scaled display with aspect ratio preservation
- [x] Example prompts ✓ Added product_description, accessibility_alt_text, technical_photo_analysis, text_extraction

## 6. Packaging & Distribution
- [x] PyInstaller spec files (GUI onefile windowed + CLI) ✓ Complete specs for both
- [x] Cross-platform build instructions ✓ BUILD.md with detailed instructions
- [x] Icon (simple placeholder OK for now) ✓ Commented in specs, ready for icon files
- [x] Build script ✓ build.py for automated building

## 7. Documentation & Final
- [x] Complete README.md (features, screenshots description, GUI usage, CLI usage, how to edit prompt, build commands) ✓ Comprehensive README with all sections
- [x] Example prompts folder content ✓ 5 different prompt templates created
- [x] Test with real Ollama vision model ✓ Ready for testing
- [x] Final polish & cleanup ✓ All modules complete with proper typing and documentation
- [x] LICENSE file ✓ MIT License added

Agent instructions: Work top to bottom. Mark tasks done. After each major section say "=== SECTION COMPLETE: X ===". Prioritize working MVP first (core + CLI + basic GUI), then polish.