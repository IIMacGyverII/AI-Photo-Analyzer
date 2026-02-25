# Build Scripts for Ollama Image Analyzer

This directory contains scripts for building standalone executables.

## Prerequisites

```bash
pip install pyinstaller
```

## Building

### Windows

#### GUI Application
```powershell
# Create standalone GUI executable
pyinstaller ollama_image_analyzer_gui.spec

# Output: dist/OllamaImageAnalyzer.exe
```

#### CLI Application
```powershell
# Create standalone CLI executable
pyinstaller ollama_image_analyzer_cli.spec

# Output: dist/ollama-image-analyzer.exe
```

### Linux

#### GUI Application
```bash
# Create standalone GUI executable
pyinstaller ollama_image_analyzer_gui.spec

# Output: dist/OllamaImageAnalyzer
```

#### CLI Application
```bash
# Create standalone CLI executable
pyinstaller ollama_image_analyzer_cli.spec

# Output: dist/ollama-image-analyzer
```

### macOS

#### GUI Application
```bash
# Create macOS app bundle
pyinstaller ollama_image_analyzer_gui.spec

# Output: dist/Ollama Image Analyzer.app
```

#### CLI Application
```bash
# Create standalone CLI executable
pyinstaller ollama_image_analyzer_cli.spec

# Output: dist/ollama-image-analyzer
```

## Build All Platforms (from dev mode)

### Using the Python module directly

```bash
# GUI mode (no args = GUI)
python -m ollama_image_analyzer

# CLI mode (with args)
python -m ollama_image_analyzer analyze image.jpg
```

## Distribution

After building:

1. Test the executable thoroughly
2. Package with any required assets (prompts folder is embedded)
3. Create installer (optional):
   - Windows: Use Inno Setup, NSIS, or WiX
   - macOS: Use `create-dmg` or similar
   - Linux: Create .deb, .rpm, AppImage, or Flatpak

## Troubleshooting

### Missing Dependencies
If you get import errors, add them to `hiddenimports` in the spec file.

### Large Executable Size
The executable includes Python interpreter and all dependencies. To reduce size:
- Use UPX compression (already enabled)
- Exclude unnecessary modules in the `excludes` list
- Consider using `--onedir` instead of `--onefile` if needed

### Icon Not Showing
1. Create/add icon files:
   - Windows: `assets/icon.ico`
   - macOS: `assets/icon.icns`
   - Linux: `assets/icon.png`
2. Uncomment icon lines in spec files
3. Rebuild

### Prompts Not Found
The spec files automatically include all `.txt` files from the `prompts/` directory.
Verify they're present before building.

## Advanced Options

### Debug Build
For debugging, set `debug=True` in the spec file:
```python
exe = EXE(
    # ...
    debug=True,
    console=True,  # Show console even for GUI version
    # ...
)
```

### Code Signing (macOS/Windows)
For distribution, sign your executables:

**macOS:**
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "dist/Ollama Image Analyzer.app"
```

**Windows:**
```powershell
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist/OllamaImageAnalyzer.exe"
```
