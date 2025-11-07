"""Exception classes for Logic Plugin Manager.

This module defines all custom exceptions used throughout the library for
error handling related to plugin loading, tag management, and category operations.
"""


class PluginLoadError(Exception):
    """Base exception for errors occurring during plugin/component loading."""

    pass


class NonexistentPlistError(PluginLoadError):
    """Raised when a required Info.plist file cannot be found."""

    pass


class CannotParsePlistError(PluginLoadError):
    """Raised when a plist file exists but cannot be parsed or decoded."""

    pass


class CannotParseComponentError(PluginLoadError):
    """Raised when component data is malformed or cannot be extracted."""

    pass


class OldComponentFormatError(PluginLoadError):
    """Raised when a component uses a legacy format that is not supported."""

    pass


class TagsetLoadError(Exception):
    """Base exception for errors occurring during tagset operations."""

    pass


class NonexistentTagsetError(TagsetLoadError):
    """Raised when a .tagset file cannot be found at the expected path."""

    pass


class CannotParseTagsetError(TagsetLoadError):
    """Raised when a tagset file exists but cannot be parsed."""

    pass


class TagsetWriteError(TagsetLoadError):
    """Raised when writing to a tagset file fails."""

    pass


class MusicAppsLoadError(Exception):
    """Raised when MusicApps database files cannot be loaded or parsed."""

    pass


class MusicAppsWriteError(Exception):
    """Raised when writing to MusicApps database files fails."""

    pass


class CategoryValidationError(Exception):
    """Raised when a category name is invalid or not found in the database."""

    pass


class CategoryExistsError(Exception):
    """Raised when attempting to create a category that already exists."""

    pass
