"""Shared logging controlled by the --log CLI flag."""

import sys

VERBOSE = "--log" in sys.argv


def log(*args, **kwargs):
    """Print only when --log is passed."""
    if VERBOSE:
        print(*args, **kwargs)

