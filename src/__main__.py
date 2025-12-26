#!/usr/bin/env python3
"""
FreeTimer - Unified Entry Point

Main entry point for FreeTimer application.
Supports both terminal and GUI interfaces.

Usage:
    python -m src [--terminal] [--debug] [--mute]

Examples:
    python -m src                # GUI interface (default)
    python -m src --terminal     # Terminal interface
    python -m src --debug        # GUI with debug logging
    python -m src --terminal --mute  # Terminal without sound
"""

import argparse
import logging
import os
import sys


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments with interface selection and options
    """
    parser = argparse.ArgumentParser(
        description="FreeTimer - Multi-interface Timer Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Launch terminal interface (default: GUI)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging output",
    )

    parser.add_argument(
        "--mute",
        action="store_true",
        help="Disable sound notifications",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point with interface selection."""
    args = parse_arguments()

    # Setup logging
    from src.services.logger import get_logger

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logger = get_logger(__name__)

    # Set mute environment variable if requested
    if args.mute:
        os.environ["FREETIMER_MUTE"] = "1"
        logger.info("Sound notifications disabled via --mute flag")

    # Launch appropriate interface
    try:
        if args.terminal:
            logger.info("Starting FreeTimer terminal interface")
            from src.interfaces.terminal.interface import TerminalInterface

            app = TerminalInterface()
            app.run()
        else:
            logger.info("Starting FreeTimer GUI interface")
            from src.interfaces.gui.main_window import run_gui

            run_gui()
    except KeyboardInterrupt:
        logger.info("\n👋 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error in application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
