"""Resolve file paths for both development and PyInstaller-frozen mode.

When running as a bundled .exe, PyInstaller extracts data files to a temp
directory at sys._MEIPASS.  This module provides a single helper so every
other module can find its resources without caring about the execution mode.
"""

import os
import sys


def get_base_path() -> str:
    """Return the base directory where resource files live."""
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        return sys._MEIPASS  # type: ignore[attr-defined]
    # Running as a normal Python script
    return os.path.dirname(os.path.abspath(__file__))


def resource(relative_path: str) -> str:
    """Turn a project-relative path into an absolute path that works
    in both dev and frozen mode.

    Example:
        resource("src/fire-affinity.png")
        resource("bossData.sqlite3")
        resource("tesseract/tesseract.exe")
    """
    return os.path.join(get_base_path(), relative_path)

