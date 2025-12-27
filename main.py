"""FreeTimer - Simple terminal-based timer application.

DEPRECATED: This file is kept for backward compatibility.
Use 'python -m src' or 'python -m src --gui' instead.

Usage:
    python main.py [--debug] [--mute]

Options:
    --debug     Enable debug logging
    --mute      Disable sound notifications
"""

import sys

# Forward to unified entry point
if __name__ == "__main__":
    from src.__main__ import main

    sys.exit(main())
