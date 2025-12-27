#!/usr/bin/env python3
"""
FreeTimer GUI Entry Point

DEPRECATED: This file is kept for backward compatibility.
Use 'python -m src --gui' instead.

Desktop GUI interface for FreeTimer using Tkinter.
Reuses core business logic from src/core and src/services.

Usage:
    python gui.py [--debug] [--mute]

Examples:
    python gui.py
    python gui.py --debug
    python gui.py --mute
"""

import sys

# Forward to unified entry point with --gui flag
if __name__ == "__main__":
    sys.argv.insert(1, "--gui")  # Add --gui flag
    from src.__main__ import main

    sys.exit(main())
