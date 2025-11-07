"""Tagset file management for Audio Components.

This module provides the Tagset class for reading and writing .tagset files
that store plugin metadata like nicknames, short names, and category tags.
"""

import plistlib
from dataclasses import dataclass, field
from pathlib import Path

from ..exceptions import (
    CannotParseTagsetError,
    NonexistentTagsetError,
    TagsetWriteError,
)


@dataclass
class Tagset:
    """Represents a .tagset file containing plugin metadata and tags.

    Tagset files store custom metadata and category tags for Audio Components.
    Each tagset is identified by a unique tags_id derived from the component's
    type, subtype, and manufacturer codes.

    Attributes:
        tags_id: Unique identifier (hex-encoded type-subtype-manufacturer).
        nickname: Custom nickname for the plugin.
        shortname: Custom short name for the plugin.
        tags: Dictionary mapping category names to tag values (e.g., 'user').
    """

    tags_id: str
    nickname: str
    shortname: str
    tags: dict[str, str]
    __raw_data: dict[str, str | dict[str, str]] = field(repr=False)

    def __init__(self, path: Path, *, lazy: bool = False):
        """Initialize a Tagset from a file path.

        Args:
            path: Path to .tagset file (extension added automatically if missing).
            lazy: If True, defer loading the file until needed.

        Note:
            If lazy=False, raises can occur from load() method during initialization.
        """
        self.path = path.with_suffix(".tagset")
        self.lazy = lazy

        if not lazy:
            self.load()

    def _parse_plist(self):
        """Parse the .tagset plist file.

        Returns:
            dict: Parsed plist data.

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist.
            CannotParseTagsetError: If plist cannot be parsed. This wraps:
                - plistlib.InvalidFileException: Invalid plist format.
                - OSError, IOError: File read errors.
                - UnicodeDecodeError: Encoding issues.
        """
        if not self.path.exists():
            raise NonexistentTagsetError(f".tagset not found at {self.path}")
        try:
            with open(self.path, "rb") as fp:
                plist_data = plistlib.load(fp)
                return plist_data
        except Exception as e:
            raise CannotParseTagsetError(f"An error occurred: {e}") from e

    def _write_plist(self):
        """Write the tagset data to the .tagset plist file.

        Raises:
            TagsetWriteError: If writing fails. This wraps:
                - OSError, IOError: File write errors.
                - TypeError: If data contains non-serializable types.
        """
        try:
            with open(self.path, "wb") as fp:
                plistlib.dump(self.__raw_data, fp)
        except Exception as e:
            raise TagsetWriteError(f"An error occurred: {e}") from e

    def load(self) -> "Tagset":
        """Load and parse the tagset file from disk.

        Returns:
            Tagset: Self for method chaining.

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from _parse_plist).
            CannotParseTagsetError: If plist cannot be parsed (from _parse_plist).
        """
        self.__raw_data = self._parse_plist()

        self.tags_id = self.path.name.removesuffix(".tagset")
        self.nickname = self.__raw_data.get("nickname")
        self.shortname = self.__raw_data.get("shortname")
        self.tags = self.__raw_data.get("tags") or {}

        return self

    def set_nickname(self, nickname: str):
        """Set the nickname field in the tagset.

        Args:
            nickname: New nickname value.

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from load).
            CannotParseTagsetError: If plist cannot be parsed (from load).
            TagsetWriteError: If writing fails (from _write_plist).
        """
        self.load()
        self.__raw_data["nickname"] = nickname
        self._write_plist()
        self.load()

    def set_shortname(self, shortname: str):
        """Set the shortname field in the tagset.

        Args:
            shortname: New short name value.

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from load).
            CannotParseTagsetError: If plist cannot be parsed (from load).
            TagsetWriteError: If writing fails (from _write_plist).
        """
        self.load()
        self.__raw_data["shortname"] = shortname
        self._write_plist()
        self.load()

    def set_tags(self, tags: dict[str, str]):
        """Replace all tags with the provided dictionary.

        Args:
            tags: Dictionary mapping category names to tag values.

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from load).
            CannotParseTagsetError: If plist cannot be parsed (from load).
            TagsetWriteError: If writing fails (from _write_plist).
        """
        self.load()
        self.__raw_data["tags"] = tags
        self._write_plist()
        self.load()

    def add_tag(self, tag: str, value: str):
        """Add or update a single tag.

        Args:
            tag: Category name.
            value: Tag value (typically 'user').

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from load).
            CannotParseTagsetError: If plist cannot be parsed (from load).
            TagsetWriteError: If writing fails (from _write_plist).
        """
        self.load()
        self.tags[tag] = value
        self._write_plist()
        self.load()

    def remove_tag(self, tag: str):
        """Remove a tag from the tagset.

        Args:
            tag: Category name to remove.

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from load).
            CannotParseTagsetError: If plist cannot be parsed (from load).
            KeyError: If tag doesn't exist in the tagset.
            TagsetWriteError: If writing fails (from _write_plist).
        """
        self.load()
        del self.tags[tag]
        self._write_plist()
        self.load()

    def move_to_tag(self, tag: str, value: str):
        """Clear all tags and set a single tag.

        Args:
            tag: Category name.
            value: Tag value (typically 'user').

        Raises:
            NonexistentTagsetError: If .tagset file doesn't exist (from load).
            CannotParseTagsetError: If plist cannot be parsed (from load).
            TagsetWriteError: If writing fails (from _write_plist).
        """
        self.load()
        self.tags.clear()
        self.tags[tag] = value
        self._write_plist()
        self.load()


__all__ = ["Tagset"]
