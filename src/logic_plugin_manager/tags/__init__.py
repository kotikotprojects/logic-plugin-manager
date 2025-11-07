"""Tags package for category and metadata management.

This package provides classes for managing Logic Pro's tag database system,
including categories, plugin metadata, and sorting preferences.
"""

from .category import Category
from .musicapps import MusicApps, Properties, Tagpool
from .tagset import Tagset

__all__ = ["Category", "MusicApps", "Properties", "Tagpool", "Tagset"]
