"""
Logging configuration for fontpls.
"""
import logging
import sys

# Create logger
logger = logging.getLogger("fontpls")

# Default to only showing warnings and above
logger.setLevel(logging.WARNING)

# Create handlers
console_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def configure_logging(verbose=0):
    """Configure logging based on verbosity level.

    Args:
        verbose (int): Verbosity level
            0 - Only show WARNING and above (default)
            1 - Show INFO and above
            2 - Show DEBUG and above
    """
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
