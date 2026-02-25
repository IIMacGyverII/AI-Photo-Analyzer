"""Main entry point for Ollama Image Analyzer.

Automatically detects whether to run in CLI or GUI mode based on arguments.
"""

import sys
from typing import NoReturn


def main() -> NoReturn:
    """Main entry point - route to CLI or GUI based on arguments."""
    # Check if we should run CLI mode
    # CLI mode if: any arguments provided OR --cli flag
    run_cli = len(sys.argv) > 1 or "--cli" in sys.argv

    if run_cli:
        # Remove --cli flag if present (it's just a mode selector)
        if "--cli" in sys.argv:
            sys.argv.remove("--cli")
        
        # Run CLI
        from ollama_image_analyzer.cli.main import app
        app()
    else:
        # Run GUI
        from PySide6.QtWidgets import QApplication
        from ollama_image_analyzer.gui.main_window import MainWindow
        from ollama_image_analyzer.core.logging_config import setup_logging
        import logging

        # Setup logging for GUI
        setup_logging(level=logging.INFO)

        app = QApplication(sys.argv)
        app.setApplicationName("Ollama Image Analyzer")
        app.setOrganizationName("OllamaImageAnalyzer")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
