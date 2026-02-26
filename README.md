# 🤖 Ollama Image Analyzer

**A modern, polished, cross-platform desktop application for detailed image analysis using Ollama vision models.**

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.12+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![PySide6](https://img.shields.io/badge/GUI-PySide6-purple)

---

## ✨ Features

### 🧠 Powerful AI Analysis
- **Any Ollama vision model**: llava, moondream, bakllava, or any custom model
- **Remote server support**: Connect to Ollama running anywhere on your network
- **Non-blocking analysis**: Background processing with real-time progress feedback
- **Multiple output formats**:
  - PhotoPrism-compatible YAML sidecars (.yml) for photo management integration
  - Text files (.txt) for backward compatibility
  - Optional EXIF/IPTC metadata embedding directly into images

### ✏️ Fully Customizable Prompts
- **Built-in prompt editor** with character/word count
- **Preset dropdown selector** for quick template switching
- **Save/Load/Reset** functionality for managing multiple prompt templates
- **AI-Toolkit preset** with dynamic trigger word input and model-type selector for training datasets
- **Pre-built templates** for common use cases:
  - **Default**: Comprehensive image description for general use
  - **AI-Toolkit**: Diffusion model training (FLUX, SD3, SDXL, SD1.5, Pony, LTX variants)
  - **PhotoPrism**: Searchable metadata for photo management systems
  - **Product**: E-commerce product descriptions with features and benefits
  - **Technical**: Professional photography analysis (composition, lighting, settings)
  - **Text Extraction**: OCR and text content detection
  - **Alt Text**: Accessibility-focused image descriptions
  - **Stock Photography**: SEO-optimized descriptions for stock photo platforms
  - **Social Media**: Engagement-focused content for Instagram/Pinterest
  - **E-commerce**: Detailed product descriptions with selling points
  - **Museum Archive**: Scholarly archival cataloging with structured metadata
  - **NFT Metadata**: Artistic descriptions with rarity traits for digital collectibles

### ⌨️ Powerful CLI Mode
- **Batch processing** of multiple images with progress bars
- **Rich terminal output** with beautiful formatting and colors
- **Model listing** and server testing commands
- **Same prompts as GUI** - complete consistency across modes

### 🔧 Professional Features
- **Real-time status panel** showing connection status and current model
- **Quick model switching** via dropdown (no need to open Settings)
- **Performance metrics** - Always-visible panel showing speed, tokens, and timing
- **Batch folder analysis** - Process entire folders of images at once
- **Batch error tracking** - Real-time status updates and detailed failure reports
- **Settings dialog** with connection testing and model refresh
- **Keyboard shortcuts** for common actions (Ctrl+O, Ctrl+,)
- **Progress tracking** with detailed status for batch operations
- **Configuration persistence** across sessions
- **Cross-platform** directory management using platformdirs

---

## 📋 Requirements

- **Python 3.12+** (for development/running from source)
- **Ollama server** (local or remote, version 0.1.0+)
- **Vision model** installed (e.g., `ollama pull llava`)

### Supported Image Formats
JPG, JPEG, PNG, WEBP, GIF, BMP, TIFF

### Supported Operating Systems
- Windows 10/11
- macOS 11+ (Big Sur and later)
- Ubuntu 20.04+ / Debian 11+ / Fedora 35+

---

## 🚀 Quick Start

### Option 1: Install from Source

```bash
# Clone or download this repository
cd "AI Photo Analyzer"

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m ollama_image_analyzer
```

### Option 2: Install as Package

```bash
pip install -e .

# Then run from anywhere:
ollama-image-analyzer  # GUI mode
ollama-image-analyzer analyze image.jpg  # CLI mode
```

### Option 3: Use Pre-built Executables

Download the executable for your platform from the [releases page](https://github.com/IIMacGyverII/AI-Photo-Analyzer/releases) and run it directly. No Python installation required!

---

## 📚 How to Use

### Quick Start Guide (5 Steps)

1. **Install Ollama** (if not already installed)
   ```bash
   # Download from https://ollama.ai or use:
   curl https://ollama.ai/install.sh | sh
   ```

2. **Pull a vision model**
   ```bash
   ollama pull llava    # or llava:13b, llava:34b, moondream, bakllava
   ```

3. **Download and run the application**
   - Download `OllamaImageAnalyzer.exe` from the [latest release](https://github.com/IIMacGyverII/AI-Photo-Analyzer/releases)
   - Double-click to launch (no installation needed)
   - Or run from source: `python -m ollama_image_analyzer`

4. **Analyze an image**
   - Drag and drop an image onto the window
   - Select a preset from the dropdown (or use Default)
   - Click **"🔍 Analyze Image"**
   - Wait for the AI analysis to complete

5. **Find your results**
   - Response appears in the preview panel
   - Automatically saved as `[imagename].txt` and `[imagename].jpg.yml`
   - Optional: Enable "📝 Write to image metadata" to embed results into EXIF/IPTC

### Need More Details?
See the complete [Usage Guide](#usage-guide) below for advanced features, batch processing, custom prompts, and PhotoPrism integration.

---

## 📖 Usage Guide

### GUI Mode

#### Starting the Application

**From source:**
```bash
python -m ollama_image_analyzer
```

**From executable:**
- Windows: Double-click `OllamaImageAnalyzer.exe`
- macOS: Double-click `Ollama Image Analyzer.app`
- Linux: Run `./OllamaImageAnalyzer`

#### Main Interface

The GUI has three main areas:

**Status Panel (Top):**
- **Connection Status**: Real-time indicator (🟢 Connected / 🔴 Disconnected)
- **Model Selector**: Dropdown to quickly switch between available Ollama models
- Auto-populates with all installed vision models when connected

**Left Panel - Image Viewer:**
- Drag and drop an image file directly onto the window
- Or click "📁 Import Image" to browse for a file
- Click "📂 Batch Analyze Folder" to process all images in a folder
- The image preview automatically scales to fit while maintaining aspect ratio

**Right Panel - Prompt & Controls:**
- **Prompt Enhancer**: Customizable analysis prompts with multiple options
  - **Preset Dropdown**: Quick selection from built-in templates
  - **Trigger Word** (AI-Toolkit only): Dynamic placeholder replacement
  - **Refresh**: Reload preset list from prompts/ directory
  - **Save as Preset**: Save your current prompt as a new template
  - **Load File**: Import prompt from any .txt file
  - **Reset**: Restore the default comprehensive analysis prompt
- **Response Preview**: Shows the AI's analysis after completion
- **Analyze Image**: Starts single image analysis (becomes active when an image is loaded)

#### First-Time Setup

1. Click **File → Settings** (or press `Ctrl+,`)
2. Configure your Ollama server:
   - **Host URL**: Default is `http://localhost:11434`
   - For remote servers: `http://192.168.1.100:11434`
   - Click "Test Connection" to verify
3. Select your **Model**:
   - Click the refresh button (🔄) to load available models
   - Choose from llava, moondream, bakllava, etc.
4. Optionally set an **Output Directory** (leave empty to save next to images)
5. Click **OK** to save

#### Analyzing Images

**Single Image Analysis:**
1. **Load an image** (drag-and-drop or Import button)
2. **Select a preset** from the dropdown or customize the prompt
3. **For AI-Toolkit preset**: Optionally enter a trigger word (e.g., "FLXDGT", "mychar")
4. **Optional**: Enable "📝 Write to image metadata" to embed results into the image's EXIF/IPTC fields
5. Click **"🔍 Analyze Image"**
6. Watch the progress bar as Ollama analyzes
7. **Review the response** in the preview panel
8. The full response is **automatically saved** in multiple formats:
   - **PhotoPrism YAML sidecar** (`[imagename].jpg.yml`) - for photo management tools
   - **Text file** (`[imagename].txt`) - for backward compatibility
   - **EXIF metadata** (embedded in image) - if checkbox enabled

**Batch Folder Analysis:**
1. **Select a preset** and customize if needed
2. **Optional**: Enable "📝 Write to image metadata" for EXIF/IPTC embedding
3. Click **"📂 Batch Analyze Folder"**
4. **Choose a folder** containing images
5. **Confirm** the operation (shows image count and current settings)
6. Watch the **progress bar** showing "X/Y - percentage"
7. **Monitor failures** - Status bar shows real-time errors for any failed images
8. **Review the summary** when complete (includes detailed error list if any failures occurred)
9. All results are **automatically saved** in the selected formats (YAML, TXT, and optionally EXIF)

#### Keyboard Shortcuts

- `Ctrl+O` - Import Image
- `Ctrl+,` - Open Settings
- `Ctrl+Q` - Quit Application

---

### 📸 PhotoPrism Integration & Metadata Writing

The application automatically creates **PhotoPrism-compatible YAML sidecars** for seamless integration with photo management systems.

#### Output Formats

**YAML Sidecar Files** (always created):
- Filename: `[image].jpg.yml` (e.g., `photo.jpg.yml`)
- PhotoPrism automatically detects and imports these files
- Contains structured metadata: Title, Description, TakenAt timestamp, AI model info, processing time
- Perfect for searchable photo libraries without modifying original images

**Text Files** (always created):
- Filename: `[image].txt` (e.g., `photo.txt`)
- Plain text format for maximum compatibility
- Useful for traditional workflows and quick viewing

**EXIF/IPTC Metadata** (optional):
- Enable via "📝 Write to image metadata" checkbox
- Writes description directly into image's EXIF fields (ImageDescription + UserComment)
- Creates `.bak` backup before modifying the original image
- Maximum compatibility with all photo management tools (Lightroom, Bridge, etc.)
- **Note**: Only works with JPEG images (PNG, WEBP don't support EXIF)

#### Example YAML Sidecar

```yaml
Title: Professional headshot photograph
Description: A professional corporate headshot showing a woman in business attire...
TakenAt: "2024-01-15T14:30:00Z"
Details:
  AI_Model: llava:latest
  AI_Generated: true
  Processing_Time: 2.34s
```

#### PhotoPrism Setup

1. Enable "📝 Write to image metadata" if you want EXIF embedding
2. Analyze your images (single or batch mode)
3. Import your photo folder into PhotoPrism
4. PhotoPrism will automatically:
   - Read the YAML sidecars
   - Make descriptions searchable
   - Display AI-generated metadata alongside photos

---

### CLI Mode

#### Basic Usage

The CLI provides powerful batch processing capabilities with beautiful terminal output.

**Analyze a single image:**
```bash
ollama-image-analyzer analyze photo.jpg
```

**Batch process multiple images:**
```bash
# All JPGs in current directory
ollama-image-analyzer analyze *.jpg

# Multiple files explicitly
ollama-image-analyzer analyze img1.png img2.png img3.webp
```

#### Advanced Options

```bash
# Use a remote Ollama server
ollama-image-analyzer analyze image.jpg --host http://192.168.1.100:11434

# Specify a different model
ollama-image-analyzer analyze image.jpg --model moondream

# Use a custom prompt file
ollama-image-analyzer analyze image.jpg --prompt prompts/product_description.txt

# Save results to a specific directory
ollama-image-analyzer analyze *.png --output-dir ./analysis_results

# Combine options
ollama-image-analyzer analyze *.jpg \
  --host http://server:11434 \
  --model llava \
  --prompt prompts/technical_photo_analysis.txt \
  --output-dir ./results

# Verbose logging
ollama-image-analyzer analyze image.jpg --verbose

# Quiet mode (errors only)
ollama-image-analyzer analyze image.jpg --quiet
```

#### Utility Commands

**List available vision models:**
```bash
ollama-image-analyzer models

# From a remote server
ollama-image-analyzer models --host http://192.168.1.100:11434
```

**Show current configuration:**
```bash
ollama-image-analyzer config-show
```

**Get help:**
```bash
ollama-image-analyzer --help
ollama-image-analyzer analyze --help
```

---

## 🎯 Prompt Templates

The application includes several pre-built prompt templates in the `prompts/` directory:

### 1. Default - Comprehensive Analysis
**File:** `prompts/default.txt`

Provides detailed analysis with structured sections:
- Overview summary
- Visual elements (subjects, composition, colors, lighting)
- Details & context
- Interpretation and use cases

### 2. Product Description
**File:** `prompts/product_description.txt`

Perfect for e-commerce:
- Product identification
- Physical description
- Quality indicators
- Marketing copy generation
- Price range estimation

### 3. Accessibility Alt Text
**File:** `prompts/accessibility_alt_text.txt`

Creates screen-reader friendly descriptions:
- 125 character limit
- Focuses on essential content
- Natural, conversational tone

### 4. Technical Photo Analysis
**File:** `prompts/technical_photo_analysis.txt`

For photographers and enthusiasts:
- Estimated camera settings
- Lighting analysis
- Composition techniques
- Post-processing observations
- Improvement suggestions

### 5. Text Extraction
**File:** `prompts/text_extraction.txt`

OCR and text analysis:
- Extracts all visible text
- Location and context
- Language detection
- Structured data extraction

### 6. AI-Toolkit (Diffusion Model Training)
**File:** `prompts/ai_toolkit.txt`

Perfect for Flux.1-dev LoRA training datasets:
- Natural language captions (150-400 words)
- No markdown, bullets, or headers
- Subject/action/environment/lighting details
- **Trigger word support**: Enter your trigger word and it will be automatically inserted
- Option to omit trigger for generic captions
- Avoids describing permanent traits (for character training)
- Focuses on scene/content (for style training)

### Creating Custom Prompts

1. Create a new `.txt` file in the `prompts/` folder
2. Write your prompt instructions
3. Load it in the GUI (Prompt Enhancer → Load) or use `--prompt` in CLI

**Tips for effective prompts:**
- Be specific about what you want to extract
- Use markdown formatting for structured output
- Include examples if needed
- Set the context (e.g., "You are a product expert...")

---

## ⚙️ Configuration

### Configuration File Location

The app stores settings in platform-specific locations:

- **Windows:** `%APPDATA%\ollama_image_analyzer\config.json`
- **macOS:** `~/Library/Application Support/ollama_image_analyzer/config.json`
- **Linux:** `~/.config/ollama_image_analyzer/config.json`

### Configuration Options

```json
{
  "ollama_host": "http://localhost:11434",
  "ollama_model": "llava",
  "output_directory": null,
  "prompt_file": "prompts/default.txt",
  "window_width": 1200,
  "window_height": 800,
  "last_image_directory": "",
  "timeout_seconds": 300,
  "save_responses": true
}
```

**Key Settings:**
- `ollama_host`: URL of your Ollama server
- `ollama_model`: Default vision model to use
- `output_directory`: Where to save results (`null` = same as image)
- `timeout_seconds`: Maximum time to wait for analysis

---

## 🏗️ Building Executables

### Prerequisites

```bash
pip install pyinstaller
```

### Quick Build

```bash
# Interactive build script
python build.py
```

### Manual Build

#### Windows
```powershell
# GUI application
pyinstaller ollama_image_analyzer_gui.spec
# Result: dist/OllamaImageAnalyzer.exe

# CLI application
pyinstaller ollama_image_analyzer_cli.spec
# Result: dist/ollama-image-analyzer.exe
```

#### macOS
```bash
# GUI application (creates .app bundle)
pyinstaller ollama_image_analyzer_gui.spec
# Result: dist/Ollama Image Analyzer.app

# CLI application
pyinstaller ollama_image_analyzer_cli.spec
# Result: dist/ollama-image-analyzer
```

#### Linux
```bash
# GUI application
pyinstaller ollama_image_analyzer_gui.spec
# Result: dist/OllamaImageAnalyzer

# CLI application
pyinstaller ollama_image_analyzer_cli.spec
# Result: dist/ollama-image-analyzer
```

See [BUILD.md](BUILD.md) for detailed build instructions and troubleshooting.

---

## 🛠️ Development

### Project Structure

```
ollama_image_analyzer/
├── ollama_image_analyzer/
│   ├── __init__.py           # Package metadata
│   ├── __main__.py           # Entry point (CLI/GUI router)
│   ├── core/                 # Shared business logic
│   │   ├── config.py         # Configuration management
│   │   ├── prompt_manager.py # Prompt loading/saving
│   │   ├── ollama_client.py  # Ollama API client
│   │   └── logging_config.py # Logging setup
│   ├── gui/                  # PySide6 GUI
│   │   ├── main_window.py    # Main application window
│   │   ├── image_viewer.py   # Image display widget
│   │   ├── prompt_editor.py  # Prompt editing widget
│   │   ├── settings_dialog.py # Settings dialog
│   │   ├── worker.py         # Background analysis thread
│   │   ├── batch_worker.py   # Batch analysis thread
│   │   └── theme.py          # Dark theme stylesheet
│   └── cli/                  # Typer CLI
│       └── main.py           # CLI commands
├── prompts/                  # Prompt templates
├── pyproject.toml            # Project metadata & dependencies
├── requirements.txt          # Pip dependencies
├── build.py                  # Build automation script
├── BUILD.md                  # Build documentation
└── README.md                 # This file
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy ollama_image_analyzer

# Code formatting
black ollama_image_analyzer
ruff check ollama_image_analyzer
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Clone the repository
2. Install in editable mode: `pip install -e ".[dev]"`
3. Make your changes
4. Run tests and type checking
5. Submit a PR

---

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 🙏 Acknowledgments

- **Ollama** - Amazing local LLM runtime
- **PySide6** - Professional Qt bindings for Python
- **Typer** - Modern CLI framework
- **Rich** - Beautiful terminal formatting
- **piexif** - Pure Python EXIF/IPTC metadata library
- **PyYAML** - YAML parser and emitter for Python

---

## 📞 Support

### Common Issues

**"Failed to connect to Ollama server"**
- Make sure Ollama is running: `ollama serve`
- Check the host URL in Settings
- For remote servers, verify network access and firewall rules

**"No vision models found"**
- Install a vision model: `ollama pull llava`
- Refresh the model list in Settings

**"Analysis timeout"**
- Increase timeout in Settings (default: 300 seconds)
- Large images or complex prompts may take longer
- Check Ollama server performance

**GUI doesn't start on Linux**
- Install Qt dependencies: `sudo apt install libxcb-cursor0`

### Getting Help

- Check existing issues on GitHub
- Review the BUILD.md for packaging problems
- Ensure you're using Python 3.12+

---

## 🚦 Roadmap

Completed:
- [✓] Batch analysis in GUI mode
- [✓] Preset selector dropdown
- [✓] Quick model switching from main window
- [✓] Real-time connection status indicator
- [✓] AI training dataset caption generation
- [✓] PhotoPrism YAML sidecar integration
- [✓] EXIF/IPTC metadata embedding
- [✓] Performance metrics tracking
- [✓] Batch error tracking and reporting

Potential future enhancements:
- [ ] Export results to PDF/HTML
- [ ] Image comparison mode
- [ ] Custom model parameter tuning (temperature, top_p, etc.)
- [ ] Plugin system for custom analyzers
- [ ] Multi-language support
- [ ] Streaming responses for large analyses
- [ ] Recursive folder processing with subdirectories

---

**Built with ❤️ using Python, PySide6, and Ollama**
