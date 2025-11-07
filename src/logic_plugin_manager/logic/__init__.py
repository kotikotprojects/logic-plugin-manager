"""Logic package for plugin management and search.

This package provides the main Logic interface and Plugins collection
for managing Logic Pro's audio plugins.
"""

from .logic import Logic
from .plugins import Plugins, SearchResult

__all__ = ["Logic", "Plugins", "SearchResult"]
