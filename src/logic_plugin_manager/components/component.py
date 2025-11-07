"""Component bundle representation and parsing.

This module provides the Component class for loading and parsing macOS
Audio Component bundles (.component directories) and their Info.plist files.
"""

import logging
import plistlib
from dataclasses import dataclass
from pathlib import Path

from .. import defaults
from ..exceptions import (
    CannotParseComponentError,
    CannotParsePlistError,
    NonexistentPlistError,
    OldComponentFormatError,
)
from ..tags import MusicApps
from .audiocomponent import AudioComponent

logger = logging.getLogger(__name__)


@dataclass
class Component:
    """Represents a macOS Audio Component bundle.

    A Component bundle (.component) can contain one or more AudioComponents.
    This class parses the bundle's Info.plist and instantiates AudioComponent
    objects for each Audio Unit defined within.

    Attributes:
        name: Component bundle name (without .component extension).
        bundle_id: CFBundleIdentifier from Info.plist.
        short_version: CFBundleShortVersionString from Info.plist.
        version: CFBundleVersion from Info.plist.
        audio_components: List of AudioComponent instances from this bundle.
    """

    name: str
    bundle_id: str
    short_version: str
    version: str
    audio_components: list[AudioComponent]

    def __init__(
        self,
        path: Path,
        *,
        lazy: bool = False,
        tags_path: Path = defaults.tags_path,
        musicapps: MusicApps = None,
    ):
        """Initialize a Component from a bundle path.

        Args:
            path: Path to .component bundle (with or without .component extension).
            lazy: If True, defer loading Info.plist and AudioComponents.
            tags_path: Path to tags database directory.
            musicapps: Shared MusicApps instance for category management.

        Note:
            If lazy=False, raises can occur from load() method during initialization.
        """
        self.path = path if path.suffix == ".component" else Path(f"{path}.component")
        self.lazy = lazy
        self.tags_path = tags_path
        self.musicapps = musicapps or MusicApps(tags_path=self.tags_path, lazy=lazy)
        logger.debug(f"Created Component from {self.path}")

        if not lazy:
            self.load()

    def _parse_plist(self):
        """Parse the Info.plist file from the component bundle.

        Returns:
            dict: Parsed plist data.

        Raises:
            NonexistentPlistError: If Info.plist file doesn't exist.
            CannotParsePlistError: If plist cannot be parsed. This wraps:
                - plistlib.InvalidFileException: Invalid plist format.
                - OSError, IOError: File read errors.
                - UnicodeDecodeError: Encoding issues.
        """
        info_plist_path = self.path / "Contents" / "Info.plist"
        logger.debug(f"Parsing Info.plist at {info_plist_path}")
        if not info_plist_path.exists():
            raise NonexistentPlistError(f"Info.plist not found at {info_plist_path}")

        try:
            with open(info_plist_path, "rb") as fp:
                plist_data = plistlib.load(fp)
                return plist_data
        except Exception as e:
            raise CannotParsePlistError(f"An error occurred: {e}") from e

    def load(self) -> "Component":
        """Load and parse the component bundle and its AudioComponents.

        Parses Info.plist, extracts bundle metadata, and creates AudioComponent
        instances for each Audio Unit defined in the AudioComponents array.

        Returns:
            Component: Self for method chaining.

        Raises:
            NonexistentPlistError: If Info.plist doesn't exist (from _parse_plist).
            CannotParsePlistError: If plist parsing or metadata extraction fails.
                This wraps AttributeError, TypeError from dict.get() operations.
            OldComponentFormatError: If AudioComponents key is missing (legacy format).
            CannotParseComponentError: If AudioComponent instantiation fails.
                This wraps CannotParseComponentError from AudioComponent.__init__.
        """
        plist_data = self._parse_plist()
        logger.debug(f"Loaded Info.plist for {self.path}")

        try:
            self.name = self.path.name.removesuffix(".component")
            self.bundle_id = plist_data.get("CFBundleIdentifier")
            self.version = plist_data.get("CFBundleVersion")
            self.short_version = plist_data.get("CFBundleShortVersionString")
            logger.debug(f"Loaded component info for {self.bundle_id}")
        except Exception as e:
            raise CannotParsePlistError(
                f"An error occurred while extracting: {e}"
            ) from e
        try:
            logger.debug(f"Loading components for {self.bundle_id}")
            self.audio_components = [
                AudioComponent(
                    name,
                    lazy=self.lazy,
                    tags_path=self.tags_path,
                    musicapps=self.musicapps,
                )
                for name in plist_data["AudioComponents"]
            ]
            logger.debug(
                f"Loaded {len(self.audio_components)} components for {self.bundle_id}"
            )
        except KeyError as e:
            raise OldComponentFormatError(
                "This component is in an old format and cannot be loaded"
            ) from e
        except Exception as e:
            raise CannotParseComponentError(
                "An error occurred while loading components"
            ) from e

        logger.debug(f"Loaded {self.name} from {self.path}")
        return self

    def __hash__(self):
        """Return hash based on bundle_id for use in sets and dicts.

        Returns:
            int: Hash value.
        """
        return hash(self.bundle_id)


__all__ = ["Component"]
