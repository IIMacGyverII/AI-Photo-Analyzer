# Changelog

All notable changes to Ollama Image Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2026-03-01

### Added
- **Response Validation**: Automatic validation of AI-generated responses before saving
  - Detects and prevents saving of empty or near-empty responses (minimum 20 characters)
  - Prevents runaway generation by enforcing maximum length limit (10,000 words)
  - Detects gibberish output by analyzing average word length and character patterns
  - Identifies excessive repetition in responses (e.g., "word word word..." patterns)
  - Validates that responses contain normal alphanumeric characters (at least 70%)
- **Automatic Retry Logic**: Failed analyses automatically retry once before marking as failed
  - If an image analysis fails for any reason, the system automatically retries once
  - Status messages show when retries are occurring
  - After batch completion, failed items can be manually retried via summary dialog
  - "Retry Failed Items" button appears in batch summary when items fail twice
- **Estimated Time to Completion**: Real-time ETA display during batch processing
  - Progress bar shows estimated time remaining based on actual processing speed
  - Updates after each image completes for accurate predictions
  - Displays in seconds, minutes, or hours depending on remaining time
  - Format: "5/20 - 25% - ETA: 2m 30s"
- **File Overwrite Protection**: Optional protection against overwriting existing analysis files
  - New "Overwrite existing files" setting in Settings dialog (enabled by default)
  - When disabled, images with existing analysis files are skipped entirely (no re-analysis)
  - When enabled, user receives warning dialog before overwriting with scrollable file list
  - CLI supports `--no-overwrite` flag for batch processing protection
  - Skip behavior clearly communicated with informative messages about which files were skipped
- **Application Icon**: Custom icon for taskbar and window title bar
  - Beautiful camera lens-themed icon with dark purple gradient
  - Multi-size icon support (16x16 to 256x256) for crisp display at all sizes
  - ICO file bundled with executable for Windows taskbar
- **Improved Error Reporting**: Validation failures are clearly distinguished from save errors
  - GUI shows specific validation error messages (e.g., "Response too short", "Response appears to be gibberish")
  - CLI displays "[red]✗ Validation failed[/red]" status for failed validations
  - Batch processing tracks validation failures separately and includes them in error reports

### Changed
- Single image analysis now checks for existing files before starting analysis
- Batch processing filters out images with existing files when overwrite protection is enabled
- Overwrite warnings show scrollable list when many files would be affected

### Fixed
- Empty text files no longer created when AI returns no content
- Extremely long responses (runaway generation) now rejected before saving
- Gibberish responses (random characters, very short words) now detected and rejected
- Batch processing now properly marks images as failed when all save operations fail due to validation
- Accidental data loss prevented by skip behavior when overwrite protection is enabled
- Trigger word now properly updates before each batch analysis or single image analysis
- Trigger word no longer reverts to "[trigger]" placeholder after changing between batches

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
