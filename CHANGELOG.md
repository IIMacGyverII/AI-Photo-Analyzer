# Changelog

All notable changes to Ollama Image Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-25

### Added
- **PhotoPrism Integration**: Automatic YAML sidecar file generation for PhotoPrism compatibility
  - Creates `.yml` files with structured metadata (Title, Description, TakenAt, AI model info)
  - PhotoPrism can automatically import and index these files
- **EXIF/IPTC Metadata Writing**: Optional embedding of analysis results directly into image files
  - Writes to ImageDescription and UserComment EXIF tags
  - Automatic `.bak` backup creation before modifying images
  - Works with JPEG images only
- **Context-Aware Checkboxes**: Output format options now appear only for relevant presets
  - YAML checkbox for PhotoPrism, Museum Archive, Stock Photography, E-commerce, NFT presets
  - EXIF checkbox for PhotoPrism, Museum Archive, Stock Photography, Technical Photography presets
  - All other presets (AI-Toolkit, Default, etc.) show no checkboxes - just save text files
- **Performance Metrics Panel**: Always-visible performance tracking
  - Real-time display of tokens/second, total time, token counts
  - Evaluation and load duration breakdown
  - Batch average metrics during folder processing
- **Batch Error Tracking**: Comprehensive error reporting for batch operations
  - Real-time status bar updates when items fail
  - Detailed error summary in completion dialog
  - Shows filename and error message for each failed item
  - First 5 errors displayed in detail, with count of additional failures
- **New Dependencies**: Added piexif and PyYAML for metadata handling
- **12 Preset Templates**: Expanded from 6 to 12 presets covering diverse use cases
  - PhotoPrism: Searchable metadata for photo management
  - Stock Photography: SEO-optimized descriptions
  - Social Media: Engagement-focused content
  - E-commerce: Product descriptions with selling points
  - Museum Archive: Scholarly cataloging
  - NFT Metadata: Artistic descriptions with rarity traits

### Changed
- Performance metrics panel now visible by default (shows "—" until first analysis)
- Text files (.txt) always created for backward compatibility regardless of checkbox state
- Batch completion summary now includes detailed file format breakdown
- Updated README with new features and dependencies
- Bumped version from 1.0.0 to 1.1.0

### Fixed
- Performance metrics no longer flash/disappear between analyses
- Batch analysis now properly tracks and reports all failures

## [1.0.0] - 2026-02-20

### Added
- Initial release
- Cross-platform GUI with PySide6
- CLI mode with Typer
- Drag-and-drop image loading
- Real-time connection status
- Quick model switching
- 6 built-in preset templates
- AI-Toolkit preset with model type selector (FLUX, SD3, SDXL, SD1.5, Pony, LTX)
- Batch folder analysis
- Custom prompt editor
- Progress tracking with cancel support
- Dark-themed modern UI
- Remote Ollama server support

[1.1.0]: https://github.com/yourusername/ollama-image-analyzer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourusername/ollama-image-analyzer/releases/tag/v1.0.0
