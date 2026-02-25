"""Build script for creating executables on all platforms."""

import platform
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with error code {e.returncode}")
        return False


def main() -> int:
    """Main build script."""
    print("\n" + "="*60)
    print("  Ollama Image Analyzer - Build Script")
    print("="*60)
    
    system = platform.system()
    print(f"\nDetected platform: {system}")
    print(f"Python version: {sys.version}")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("\n✗ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        return 1
    
    # Ask what to build
    print("\nWhat would you like to build?")
    print("1. GUI application only")
    print("2. CLI application only")
    print("3. Both GUI and CLI")
    
    choice = input("\nEnter choice (1-3) [3]: ").strip() or "3"
    
    build_gui = choice in ["1", "3"]
    build_cli = choice in ["2", "3"]
    
    success = True
    
    if build_gui:
        success = run_command(
            [sys.executable, "-m", "PyInstaller", "ollama_image_analyzer_gui.spec"],
            "Building GUI Application"
        ) and success
    
    if build_cli:
        success = run_command(
            [sys.executable, "-m", "PyInstaller", "ollama_image_analyzer_cli.spec"],
            "Building CLI Application"
        ) and success
    
    # Summary
    print("\n" + "="*60)
    print("  Build Summary")
    print("="*60)
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\nBuilt files in dist/:")
        for item in dist_dir.iterdir():
            size_mb = sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024*1024)
            print(f"  - {item.name} ({size_mb:.1f} MB)")
    
    if success:
        print("\n✓ Build completed successfully!")
        print("\nNext steps:")
        print("1. Test the executables")
        print("2. Check BUILD.md for distribution instructions")
        return 0
    else:
        print("\n✗ Build completed with errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
