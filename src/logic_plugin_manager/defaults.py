"""Default paths for Logic Plugin Manager.

This module provides default filesystem paths used throughout the library
for locating Audio Components and tag databases.
"""

from pathlib import Path

components_path: Path = Path("/Library/Audio/Plug-Ins/Components")
"""Path: Default location for macOS Audio Components (.component bundles)."""

tags_path: Path = Path("~/Music/Audio Music Apps/Databases/Tags").expanduser()
"""Path: Default location for Logic Pro's tag and category database files."""


__all__ = ["components_path", "tags_path"]
