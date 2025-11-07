"""Audio Component representation and management.

This module provides classes for working with macOS Audio Unit components,
including parsing component metadata and managing their tags and categories.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .. import defaults
from ..exceptions import CannotParseComponentError
from ..tags import Category, MusicApps, Tagset

logger = logging.getLogger(__name__)


class AudioUnitType(Enum):
    """Enumeration of Audio Unit types supported by macOS.

    Each enum value contains a tuple of (code, display_name, alt_name).
    """

    AUFX = ("aufx", "Audio FX", "Effect")
    AUMU = ("aumu", "Instrument", "Music Device")
    AUMF = ("aumf", "MIDI-controlled Effects", "Music Effect")
    AUMI = ("aumi", "MIDI FX", "MIDI Generator")
    AUGN = ("augn", "Generator", "Generator")

    @property
    def code(self) -> str:
        """Get the four-character code for this Audio Unit type.

        Returns:
            str: Four-character type code (e.g., 'aufx', 'aumu').
        """
        return self.value[0]

    @property
    def display_name(self) -> str:
        """Get the human-readable display name for this Audio Unit type.

        Returns:
            str: Display name (e.g., 'Audio FX', 'Instrument').
        """
        return self.value[1]

    @property
    def alt_name(self) -> str:
        """Get the alternative name for this Audio Unit type.

        Returns:
            str: Alternative name (e.g., 'Effect', 'Music Device').
        """
        return self.value[2]

    @classmethod
    def from_code(cls, code: str) -> "AudioUnitType | None":
        """Find an AudioUnitType by its four-character code.

        Args:
            code: Four-character type code (case-insensitive).

        Returns:
            AudioUnitType | None: Matching AudioUnitType or None if not found.
        """
        code_lower = code.lower()
        for unit_type in cls:
            if unit_type.code == code_lower:
                return unit_type
        return None

    @classmethod
    def search(cls, query: str) -> list["AudioUnitType"]:
        """Search for AudioUnitTypes matching a query string.

        Searches across code, display_name, and alt_name fields.

        Args:
            query: Search query string (case-insensitive).

        Returns:
            list[AudioUnitType]: List of matching AudioUnitType values.
        """
        query_lower = query.lower()
        results = []
        for unit_type in cls:
            if (
                query_lower in unit_type.code
                or query_lower in unit_type.display_name.lower()
                or query_lower in unit_type.alt_name.lower()
            ):
                results.append(unit_type)
        return results


@dataclass
class AudioComponent:
    """Represents a single Audio Unit component.

    An AudioComponent encapsulates metadata about an Audio Unit plugin,
    including its type, manufacturer, version, and associated tags/categories.

    Attributes:
        full_name: Full name in format 'Manufacturer: Plugin Name'.
        manufacturer: Manufacturer/vendor name.
        name: Plugin name (without manufacturer prefix).
        manufacturer_code: Four-character manufacturer code.
        description: Plugin description text.
        factory_function: Name of the factory function.
        type_code: Four-character Audio Unit type code.
        type_name: AudioUnitType enum value.
        subtype_code: Four-character subtype code.
        version: Plugin version number.
        tags_id: Unique identifier for tagset lookup.
        tagset: Associated Tagset containing tags and metadata.
        categories: List of Category objects this plugin belongs to.
    """

    full_name: str
    manufacturer: str
    name: str
    manufacturer_code: str
    description: str
    factory_function: str
    type_code: str
    type_name: AudioUnitType
    subtype_code: str
    version: int
    tags_id: str
    tagset: Tagset
    categories: list[Category] = field(default_factory=list)

    def __init__(
        self,
        data: dict,
        *,
        lazy: bool = False,
        tags_path: Path = defaults.tags_path,
        musicapps: MusicApps = None,
    ):
        """Initialize an AudioComponent from component data dictionary.

        Args:
            data: Dictionary containing component metadata from Info.plist.
            lazy: If True, defer loading tagset and categories until needed.
            tags_path: Path to tags database directory.
            musicapps: Shared MusicApps instance for category management.

        Raises:
            CannotParseComponentError: If required fields are missing or malformed.
                This can wrap KeyError, IndexError, AttributeError, UnicodeEncodeError,
                or ValueError from data extraction operations.
        """
        self.tags_path = tags_path
        self.lazy = lazy
        self.musicapps = musicapps or MusicApps(tags_path=self.tags_path, lazy=lazy)

        try:
            self.full_name = data.get("name")
            self.manufacturer = self.full_name.split(": ")[0]
            self.name = self.full_name.split(": ")[-1]
            self.manufacturer_code = data.get("manufacturer")
            self.description = data.get("description")
            self.factory_function = data.get("factoryFunction")
            self.type_code = data.get("type")
            self.type_name = AudioUnitType.from_code(self.type_code)
            self.subtype_code = data.get("subtype")
            self.version = int(data.get("version"))
            self.tags_id = (
                f"{self.type_code.encode('ascii').hex()}-"
                f"{self.subtype_code.encode('ascii').hex()}-"
                f"{self.manufacturer_code.encode('ascii').hex()}"
            )
            logger.debug(f"Created AudioComponent {self.full_name} from data")
        except Exception as e:
            raise CannotParseComponentError(
                f"An error occurred while parsing: {e}"
            ) from e

        if not lazy:
            self.load()

    def load(self) -> "AudioComponent":
        """Load tagset and categories for this component.

        Loads the component's tagset from disk and initializes Category objects
        for all tags. Invalid categories are logged as warnings and skipped.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset).
            MusicAppsLoadError: If MusicApps database files cannot be loaded (from Category).
        """
        logger.debug(f"Loading AudioComponent {self.full_name}")
        self.tagset = Tagset(self.tags_path / self.tags_id, lazy=self.lazy)
        logger.debug(f"Loaded Tagset for {self.full_name}")
        self.categories = []
        for name in self.tagset.tags.keys():
            try:
                logger.debug(f"Loading category {name} for {self.full_name}")
                self.categories.append(
                    Category(name, musicapps=self.musicapps, lazy=self.lazy)
                )
            except Exception as e:
                logger.warning(
                    f"Failed to load category {name} for {self.full_name}: {e}"
                )
        logger.debug(f"Loaded {len(self.categories)} categories for {self.full_name}")
        return self

    def __eq__(self, other) -> bool:
        """Check equality based on tags_id.

        Args:
            other: Object to compare with.

        Returns:
            bool: True if both have the same tags_id, NotImplemented otherwise.
        """
        if not isinstance(other, AudioComponent):
            return NotImplemented
        return self.tags_id == other.tags_id

    def __hash__(self):
        """Return hash based on tags_id for use in sets and dicts.

        Returns:
            int: Hash value.
        """
        return hash(self.tags_id)

    def set_nickname(self, nickname: str) -> "AudioComponent":
        """Set a custom nickname for this component.

        Args:
            nickname: Custom nickname string.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset.set_nickname).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset.set_nickname).
            TagsetWriteError: If writing tagset fails (from Tagset.set_nickname).
        """
        self.tagset.set_nickname(nickname)
        self.load()
        return self

    def set_shortname(self, shortname: str) -> "AudioComponent":
        """Set a custom short name for this component.

        Args:
            shortname: Custom short name string.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset.set_shortname).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset.set_shortname).
            TagsetWriteError: If writing tagset fails (from Tagset.set_shortname).
        """
        self.tagset.set_shortname(shortname)
        self.load()
        return self

    def set_categories(self, categories: list[Category]) -> "AudioComponent":
        """Replace all categories with the provided list.

        Args:
            categories: List of Category objects to assign.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset.set_tags).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset.set_tags).
            TagsetWriteError: If writing tagset fails (from Tagset.set_tags).
        """
        self.tagset.set_tags({category.name: "user" for category in categories})
        self.load()
        return self

    def add_to_category(self, category: Category) -> "AudioComponent":
        """Add this component to a category.

        Args:
            category: Category to add this component to.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset.add_tag).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset.add_tag).
            TagsetWriteError: If writing tagset fails (from Tagset.add_tag).
        """
        self.tagset.add_tag(category.name, "user")
        self.load()
        return self

    def remove_from_category(self, category: Category) -> "AudioComponent":
        """Remove this component from a category.

        Args:
            category: Category to remove this component from.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset.remove_tag).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset.remove_tag).
            KeyError: If tag doesn't exist (from Tagset.remove_tag).
            TagsetWriteError: If writing tagset fails (from Tagset.remove_tag).
        """
        self.tagset.remove_tag(category.name)
        self.load()
        return self

    def move_to_category(self, category: Category) -> "AudioComponent":
        """Move this component to a single category, removing all others.

        Args:
            category: Category to move this component to exclusively.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset.move_to_tag).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset.move_to_tag).
            TagsetWriteError: If writing tagset fails (from Tagset.move_to_tag).
        """
        self.tagset.move_to_tag(category.name, "user")
        self.load()
        return self

    def move_to_parents(self) -> "AudioComponent":
        """Move this component to the parent categories of all current categories.

        For each category this component belongs to, adds it to the parent category
        and removes it from the child category.

        Returns:
            AudioComponent: Self for method chaining.

        Raises:
            NonexistentTagsetError: If tagset file doesn't exist (from Tagset operations).
            CannotParseTagsetError: If tagset file cannot be parsed (from Tagset operations).
            TagsetWriteError: If writing tagset fails (from Tagset operations).
            KeyError: If a category tag doesn't exist during removal (from Tagset.remove_tag).
        """
        for category in self.categories:
            self.tagset.add_tag(category.parent.name, "user")
            self.tagset.remove_tag(category.name)
        self.load()
        return self


__all__ = ["AudioComponent", "AudioUnitType"]
