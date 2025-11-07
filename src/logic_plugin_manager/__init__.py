"""Logic Plugin Manager - Programmatic management of Logic Pro audio plugins.

This library provides tools for discovering, categorizing, and managing
macOS Audio Unit plugins used by Logic Pro. It interfaces with Logic's
internal tag database to enable automated plugin organization.

Main Classes:
    Logic: Primary interface for plugin discovery and management.
    AudioComponent: Represents a single Audio Unit plugin.
    Component: Represents a .component bundle.
    Category: Represents a Logic Pro plugin category.
    Plugins: Collection with indexed search capabilities.

Example:
    >>> from logic_plugin_manager import Logic
    >>> logic = Logic()
    >>> for plugin in logic.plugins.all():
    ...     print(plugin.full_name)
"""

import logging

from .components import AudioComponent, AudioUnitType, Component
from .exceptions import MusicAppsLoadError, PluginLoadError, TagsetLoadError
from .logic import Logic, Plugins, SearchResult
from .tags import Category, MusicApps, Properties, Tagpool, Tagset

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "AudioComponent",
    "AudioUnitType",
    "Category",
    "Component",
    "Logic",
    "MusicApps",
    "MusicAppsLoadError",
    "PluginLoadError",
    "Plugins",
    "Properties",
    "SearchResult",
    "Tagpool",
    "Tagset",
    "TagsetLoadError",
]
