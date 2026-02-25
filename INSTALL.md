# Installation Guide - Ollama Image Analyzer

Complete installation instructions for all platforms.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installing Ollama](#installing-ollama)
3. [Installing the Application](#installing-the-application)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Python 3.12 or Higher

#### Windows
Download from [python.org](https://www.python.org/downloads/) or use `winget`:
```powershell
winget install Python.Python.3.12
```

#### macOS
```bash
# Using Homebrew
brew install python@3.12
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

#### Verify Python Installation
```bash
python --version
# Should show Python 3.12.x or higher
```

---

## Installing Ollama

Ollama is required to run the vision models that analyze images.

### Windows

1. Download the installer from [ollama.ai](https://ollama.ai/download)
2. Run the installer
3. Ollama will start automatically

**Or use command line:**
```powershell
winget install Ollama.Ollama
```

### macOS

```bash
# Download and install
curl https://ollama.ai/install.sh | sh

# Or use Homebrew
brew install ollama
```

### Linux

```bash
curl https://ollama.ai/install.sh | sh
```

### Verify Ollama Installation

```bash
# Start Ollama server (if not already running)
ollama serve

# In a new terminal, test it
ollama --version
ollama list
```

### Install a Vision Model

```bash
# Install llava (recommended, ~4.5GB)
ollama pull llava

# Or install moondream (faster, smaller, ~1.7GB)
ollama pull moondream

# Or install bakllava (alternative)
ollama pull bakllava

# Verify
ollama list
```

---

## Installing the Application

### Method 1: From Source (Recommended for Development)

```bash
# Navigate to the project directory
cd "AI Photo Analyzer"

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m ollama_image_analyzer
```

### Method 2: Install as Package

```bash
cd "AI Photo Analyzer"

# Install in editable mode
pip install -e .

# Now you can run from anywhere
ollama-image-analyzer              # GUI mode
ollama-image-analyzer analyze image.jpg  # CLI mode
```

### Method 3: Use Pre-built Executables

**Windows:**
1. Download `OllamaImageAnalyzer.exe` from releases
2. Double-click to run (no installation needed)

**macOS:**
1. Download `Ollama Image Analyzer.app`
2. Move to Applications folder
3. Right-click → Open (first time only, to bypass Gatekeeper)

**Linux:**
1. Download `OllamaImageAnalyzer`
2. Make executable: `chmod +x OllamaImageAnalyzer`
3. Run: `./OllamaImageAnalyzer`

---

## Verification

### Test the GUI

```bash
python -m ollama_image_analyzer
```

You should see:
- ✅ The main window opens with a dark theme
- ✅ "Ollama Image Analyzer" title
- ✅ Image viewer on the left
- ✅ Prompt editor on the right

### Test the CLI

```bash
# Check version
ollama-image-analyzer --version

# List available models (requires Ollama running)
ollama-image-analyzer models

# Should show: llava, moondream, etc.
```

### Test Analysis (Full End-to-End)

1. **Find a test image** (any JPG, PNG, etc.)

2. **GUI Test:**
   ```bash
   python -m ollama_image_analyzer
   ```
   - Drag the image into the window
   - Click "Analyze Image"
   - Wait for the response
   - Verify a `.txt` file is created next to the image

3. **CLI Test:**
   ```bash
   ollama-image-analyzer analyze test-image.jpg
   ```
   - Should show progress bar
   - Should complete successfully
   - Should create `test-image.txt`

---

## Troubleshooting

### Issue: "Command not found: ollama-image-analyzer"

**Solution:**
```bash
# Install the package
pip install -e .

# Or run directly
python -m ollama_image_analyzer
```

### Issue: "Failed to connect to Ollama"

**Check if Ollama is running:**
```bash
# Test Ollama directly
ollama list

# If not running, start it
ollama serve
```

**For remote Ollama:**
- Open Settings in GUI
- Change host to `http://YOUR_IP:11434`
- Click "Test Connection"

### Issue: "No module named 'PySide6'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: GUI doesn't start on Linux

**Missing Qt dependencies:**
```bash
# Ubuntu/Debian
sudo apt install libxcb-cursor0 libxcb-xinerama0

# Fedora
sudo dnf install xcb-util-cursor
```

### Issue: "No vision models found"

**Solution:**
```bash
# Pull a vision model
ollama pull llava

# Verify
ollama list

# In the app, click Settings → 🔄 Refresh
```

### Issue: Python version too old

**Check version:**
```bash
python --version
```

**Solution:** Install Python 3.12+ from python.org or your package manager.

### Issue: Permission denied (Linux/macOS)

**When running executable:**
```bash
chmod +x OllamaImageAnalyzer
./OllamaImageAnalyzer
```

**When installing package:**
```bash
pip install --user -e .
```

### Issue: Analysis takes too long

**Solutions:**
1. Use a faster model: `--model moondream`
2. Increase timeout in Settings
3. Check Ollama server CPU/GPU usage
4. Use a smaller image (resize before analyzing)

---

## Uninstallation

### Remove Application

```bash
# If installed as package
pip uninstall ollama-image-analyzer

# Remove configuration
# Windows: Delete %APPDATA%\ollama_image_analyzer
# macOS: rm -rf ~/Library/Application\ Support/ollama_image_analyzer
# Linux: rm -rf ~/.config/ollama_image_analyzer
```

### Remove Ollama (Optional)

**Windows:**
```powershell
winget uninstall Ollama.Ollama
```

**macOS:**
```bash
brew uninstall ollama
```

**Linux:**
```bash
sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama
```

---

## Next Steps

After successful installation:

1. ✅ Read [README.md](README.md) for feature overview
2. ✅ Check [EXAMPLES.md](EXAMPLES.md) for usage examples
3. ✅ Explore the `prompts/` directory for templates
4. ✅ Try analyzing your first image!

---

**Need more help?** Check the main [README.md](README.md) or open an issue on GitHub.
