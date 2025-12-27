# Build script for creating executable with PyInstaller
# Usage: python build.py

"""
FreeTimer Executable Builder

Creates standalone executables for Windows, macOS, and Linux.
Uses PyInstaller to bundle the application with all dependencies.
"""

import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def clean_build_folders() -> None:
    """Remove previous build artifacts."""
    folders_to_clean = ["build", "dist", "__pycache__"]

    for folder in folders_to_clean:
        if Path(folder).exists():
            print(f"Removing {folder}/")
            shutil.rmtree(folder)

    # Remove spec files
    for spec_file in Path(".").glob("*.spec"):
        print(f"Removing {spec_file}")
        spec_file.unlink()


def cleanup_after_build() -> None:
    """Clean up temporary files after successful build."""
    # Remove spec file (can be regenerated if needed)
    for spec_file in Path(".").glob("*.spec"):
        print(f"Cleaning up {spec_file}")
        spec_file.unlink()

    # Remove build folder (only dist is needed)
    if Path("build").exists():
        print("Cleaning up build/")
        shutil.rmtree("build")


def build_executable() -> None:
    """Build executable using PyInstaller."""

    print("Building FreeTimer executable...")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")

    # Determine platform-specific settings
    is_windows = platform.system() == "Windows"
    data_sep = ";" if is_windows else ":"  # PyInstaller uses ';' on Windows and ':' on Unix

    sounds_src = Path("Assets") / "Sounds"
    add_data_arg = f"--add-data={sounds_src}{data_sep}Assets/Sounds"

    icon_path = Path("Assets") / "icon.ico"
    icon_arg = f"--icon={icon_path}" if is_windows and icon_path.exists() else ""

    # PyInstaller command using unified entry point
    cmd = [
        "pyinstaller",
        "--name=FreeTimer",
        "--onefile",  # Single executable
        "--windowed",  # No console window (GUI mode by default)
        add_data_arg,  # Include sound files (platform-specific separator)
        "--collect-all=tkinter",  # Collect all tkinter files
        icon_arg,  # Optional icon on Windows if present
        "src/__main__.py",  # Use src/__main__.py as entry point
    ]

    # Remove empty strings from command
    cmd = [arg for arg in cmd if arg]

    print(f"\nRunning: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)

        # Clean up temporary files after successful build
        cleanup_after_build()

        print("\n✅ Build successful!")
        print(f"Executable location: dist/FreeTimer{'.exe' if platform.system() == 'Windows' else ''}")
        print("\nUsage:")
        print("  ./dist/FreeTimer           # GUI interface (default)")
        print("  ./dist/FreeTimer --terminal # Terminal interface")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ PyInstaller not found. Install it with:")
        print("   uv sync --group build")
        sys.exit(1)


def main() -> None:
    """Main build process."""
    print("=" * 60)
    print("FreeTimer Executable Builder")
    print("=" * 60)

    clean_build_folders()
    build_executable()

    print("\n" + "=" * 60)
    print("Build Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
