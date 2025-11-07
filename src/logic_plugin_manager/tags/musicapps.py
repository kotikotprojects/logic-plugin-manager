"""MusicApps database management for Logic Pro tags and categories.

This module provides classes for reading and writing Logic Pro's MusicApps database
files (MusicApps.tagpool and MusicApps.properties) which store category definitions,
plugin counts, and sorting information.
"""

import logging
import plistlib
from dataclasses import dataclass, field
from pathlib import Path

from .. import defaults
from ..exceptions import MusicAppsLoadError, MusicAppsWriteError

logger = logging.getLogger(__name__)


def _parse_plist(path: Path):
    """Parse a plist file from the MusicApps database.

    Args:
        path: Path to plist file.

    Returns:
        dict: Parsed plist data.

    Raises:
        MusicAppsLoadError: If file doesn't exist or cannot be parsed.
            This wraps plistlib.InvalidFileException, OSError, IOError, UnicodeDecodeError.
    """
    logger.debug(f"Parsing plist at {path}")
    if not path.exists():
        raise MusicAppsLoadError(f"File not found at {path}")
    try:
        with open(path, "rb") as fp:
            plist_data = plistlib.load(fp)
            logger.debug(f"Parsed plist for {path}")
            return plist_data
    except Exception as e:
        raise MusicAppsLoadError(f"An error occurred: {e}") from e


def _save_plist(path: Path, data: dict):
    """Save data to a plist file in the MusicApps database.

    Args:
        path: Path to plist file.
        data: Dictionary to serialize and write.

    Raises:
        MusicAppsWriteError: If writing fails.
            This wraps OSError, IOError, TypeError.
    """
    logger.debug(f"Saving plist to {path}")
    try:
        with open(path, "wb") as fp:
            plistlib.dump(data, fp)
            logger.debug(f"Saved plist to {path}")
    except Exception as e:
        raise MusicAppsWriteError(f"An error occurred: {e}") from e


@dataclass
class Tagpool:
    """Represents MusicApps.tagpool - category to plugin count mapping.

    The tagpool file stores a dictionary mapping category names to the number
    of plugins assigned to each category.

    Attributes:
        categories: Dictionary mapping category names to plugin counts.
    """

    categories: dict[str, int]

    def __init__(self, tags_path: Path, *, lazy: bool = False):
        """Initialize Tagpool from database path.

        Args:
            tags_path: Path to tags database directory.
            lazy: If True, defer loading the file.
        """
        self.path = tags_path / "MusicApps.tagpool"
        self.lazy = lazy

        logger.debug(f"Created Tagpool from {self.path}")

        if not lazy:
            self.load()

    def load(self) -> "Tagpool":
        """Load tagpool data from disk.

        Returns:
            Tagpool: Self for method chaining.

        Raises:
            MusicAppsLoadError: If file cannot be loaded (from _parse_plist).
        """
        logger.debug(f"Loading Tagpool data from {self.path}")
        self.categories = _parse_plist(self.path)
        logger.debug(f"Loaded Tagpool data from {self.path}")
        return self

    def write_category(self, name: str, plugin_count: int = 0):
        """Write or update a category with its plugin count.

        Args:
            name: Category name.
            plugin_count: Number of plugins in this category.

        Raises:
            MusicAppsLoadError: If file cannot be loaded (from load).
            MusicAppsWriteError: If file cannot be written (from _save_plist).
        """
        self.load()
        self.categories[name] = plugin_count
        _save_plist(self.path, self.categories)
        self.load()

    def introduce_category(self, name: str):
        """Add a new category if it doesn't exist.

        Args:
            name: Category name to introduce.

        Raises:
            MusicAppsLoadError: If file cannot be loaded (from load).
            MusicAppsWriteError: If file cannot be written (from write_category).
        """
        self.load()
        if name in self.categories:
            return
        self.write_category(name)

    def remove_category(self, name: str):
        """Remove a category from the tagpool.

        Args:
            name: Category name to remove.

        Raises:
            MusicAppsLoadError: If file cannot be loaded (from load).
            MusicAppsWriteError: If file cannot be written (from _save_plist).
        """
        self.load()
        self.categories.pop(name, None)
        _save_plist(self.path, self.categories)
        self.load()


@dataclass
class Properties:
    """Represents MusicApps.properties - category sorting and preferences.

    The properties file stores the category sorting order and whether user
    sorting is enabled (vs. alphabetical sorting).

    Attributes:
        sorting: Ordered list of category names.
        user_sorted: True if user sorting is enabled, False for alphabetical.
    """

    sorting: list[str]
    user_sorted: bool
    __raw_data: dict[str, str | list[str] | bool] = field(repr=False)

    def __init__(self, tags_path: Path, *, lazy: bool = False):
        """Initialize Properties from database path.

        Args:
            tags_path: Path to tags database directory.
            lazy: If True, defer loading the file.
        """
        self.path = tags_path / "MusicApps.properties"
        self.lazy = lazy

        logger.debug(f"Created Properties from {self.path}")

        if not lazy:
            self.load()

    def load(self) -> "Properties":
        """Load properties data from disk.

        Returns:
            Properties: Self for method chaining.

        Raises:
            MusicAppsLoadError: If file cannot be loaded (from _parse_plist).
        """
        logger.debug(f"Loading Properties data from {self.path}")
        self.__raw_data = _parse_plist(self.path)
        logger.debug(f"Loaded Properties data from {self.path}")

        self.sorting = self.__raw_data.get("sorting", [])
        self.user_sorted = bool(self.__raw_data.get("user_sorted", False))
        logger.debug(f"Parsed Properties data from {self.path}")
        return self

    def introduce_category(self, name: str):
        self.load()
        if name in self.sorting:
            return
        self.__raw_data["sorting"].append(name)
        _save_plist(self.path, self.__raw_data)
        self.load()

    def enable_user_sorting(self):
        self.load()
        self.__raw_data["user_sorted"] = "property"
        _save_plist(self.path, self.__raw_data)
        self.load()

    def enable_alphabetical_sorting(self):
        self.load()
        del self.__raw_data["user_sorted"]
        _save_plist(self.path, self.__raw_data)
        self.load()

    def remove_category(self, name: str):
        self.load()
        self.__raw_data["sorting"].remove(name)
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_up(self, category: str, steps: int = 1):
        """Move a category up in the sorting order.

        Args:
            category: Category name to move.
            steps: Number of positions to move up.

        Raises:
            ValueError: If category not found in sorting.
            MusicAppsLoadError: If file cannot be loaded (from load).
            MusicAppsWriteError: If file cannot be written (from _save_plist).
        """
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found in sorting")

        current_idx = sorting.index(category)
        new_idx = max(0, current_idx - steps)

        sorting.pop(current_idx)
        sorting.insert(new_idx, category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_down(self, category: str, steps: int = 1):
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found in sorting")

        current_idx = sorting.index(category)
        new_idx = min(len(sorting) - 1, current_idx + steps)

        sorting.pop(current_idx)
        sorting.insert(new_idx, category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_to_top(self, category: str):
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found in sorting")

        sorting.remove(category)
        sorting.insert(0, category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_to_bottom(self, category: str):
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found in sorting")

        sorting.remove(category)
        sorting.append(category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_before(self, category: str, target: str):
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found")
        if target not in sorting:
            raise ValueError(f"Target category '{target}' not found")

        sorting.remove(category)
        target_idx = sorting.index(target)
        sorting.insert(target_idx, category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_after(self, category: str, target: str):
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found")
        if target not in sorting:
            raise ValueError(f"Target category '{target}' not found")

        sorting.remove(category)
        target_idx = sorting.index(target)
        sorting.insert(target_idx + 1, category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def move_to_index(self, category: str, index: int):
        self.load()
        sorting = self.sorting.copy()

        if category not in sorting:
            raise ValueError(f"Category '{category}' not found")

        if index < 0:
            index = len(sorting) + index

        index = max(0, min(len(sorting) - 1, index))

        sorting.remove(category)
        sorting.insert(index, category)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def swap(self, category1: str, category2: str):
        self.load()
        sorting = self.sorting.copy()

        if category1 not in sorting or category2 not in sorting:
            raise ValueError("Both categories must exist")

        idx1 = sorting.index(category1)
        idx2 = sorting.index(category2)

        sorting[idx1], sorting[idx2] = sorting[idx2], sorting[idx1]

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def set_order(self, categories: list[str]):
        self.load()
        current = set(self.sorting)
        new = set(categories)

        if new != current:
            missing = current - new
            extra = new - current
            raise ValueError(f"Category mismatch. Missing: {missing}, Extra: {extra}")

        self.__raw_data["sorting"] = categories
        _save_plist(self.path, self.__raw_data)
        self.load()

    def reorder(self, key_func=None, reverse: bool = False):
        self.load()
        sorting = self.sorting.copy()

        if key_func is None:
            sorting.sort(reverse=reverse)
        else:
            sorting.sort(key=key_func, reverse=reverse)

        self.__raw_data["sorting"] = sorting
        _save_plist(self.path, self.__raw_data)
        self.load()

    def get_index(self, category: str) -> int:
        return self.sorting.index(category)

    def get_at_index(self, index: int) -> str:
        return self.sorting[index]

    def get_neighbors(self, category: str) -> tuple[str | None, str | None]:
        idx = self.get_index(category)
        prev_cat = self.sorting[idx - 1] if idx > 0 else None
        next_cat = self.sorting[idx + 1] if idx < len(self.sorting) - 1 else None
        return prev_cat, next_cat

    def is_first(self, category: str) -> bool:
        return self.get_index(category) == 0

    def is_last(self, category: str) -> bool:
        return self.get_index(category) == len(self.sorting) - 1


@dataclass
class MusicApps:
    """Main interface to Logic Pro's MusicApps database.

    Provides unified access to both tagpool and properties files, managing
    category definitions, plugin counts, and sorting preferences.

    Attributes:
        tagpool: Tagpool instance managing category/plugin counts.
        properties: Properties instance managing sorting and preferences.
    """

    tagpool: Tagpool
    properties: Properties

    def __init__(self, tags_path: Path = defaults.tags_path, *, lazy: bool = False):
        """Initialize MusicApps from database path.

        Args:
            tags_path: Path to tags database directory.
            lazy: If True, defer loading files.
        """
        self.path = tags_path
        self.lazy = lazy

        logger.debug(f"Created MusicApps from {self.path}")

        if not lazy:
            self.load()

    def load(self) -> "MusicApps":
        """Load both tagpool and properties files.

        Returns:
            MusicApps: Self for method chaining.

        Raises:
            MusicAppsLoadError: If files cannot be loaded (from Tagpool/Properties).
        """
        self.tagpool = Tagpool(self.path, lazy=self.lazy)
        self.properties = Properties(self.path, lazy=self.lazy)
        logger.debug(f"Loaded MusicApps from {self.path}")
        return self

    def introduce_category(self, name: str):
        """Add a new category to both tagpool and properties.

        Args:
            name: Category name to introduce.

        Raises:
            MusicAppsLoadError: If files cannot be loaded.
            MusicAppsWriteError: If files cannot be written.
        """
        self.tagpool.introduce_category(name)
        self.properties.introduce_category(name)

    def remove_category(self, name: str):
        """Remove a category from both tagpool and properties.

        Args:
            name: Category name to remove.

        Raises:
            MusicAppsLoadError: If files cannot be loaded.
            MusicAppsWriteError: If files cannot be written.
        """
        self.tagpool.remove_category(name)
        self.properties.remove_category(name)


__all__ = ["MusicApps", "Properties", "Tagpool"]
