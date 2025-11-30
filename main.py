"""FreeTimer - Simple terminal-based timer application.

Usage:
    python main.py [--debug] [--mute]

Options:
    --debug     Enable debug logging
    --mute      Disable sound notifications
"""

import argparse
import logging
from os import environ
from src.services.logger import get_logger
from src.terminal.interface import TerminalInterface

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="FreeTimer - Terminal-based timer application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Run with default settings
  python main.py --debug      # Run with debug logging
  python main.py --mute       # Run without sound notifications
        """,
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging output")

    parser.add_argument("--mute", action="store_true", help="Disable sound notifications")

    return parser.parse_args()


def setup_environment(args: argparse.Namespace) -> None:
    """Configure environment based on arguments.

    Args:
        args: Parsed command-line arguments.
    """
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    if args.mute:
        environ["FREETIMER_MUTE"] = "1"
        logger.info("Sound notifications disabled")


def run() -> None:
    """Execute application main loop."""
    args = parse_arguments()
    setup_environment(args)

    try:
        logger.info("Starting FreeTimer (Terminal)")
        app = TerminalInterface()
        app.run()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error("❌ An unexpected error occurred.")


if __name__ == "__main__":
    run()
