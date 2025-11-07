"""Main Logic Pro plugin management interface.

This module provides the Logic class, the primary entry point for discovering
and managing Logic Pro's audio plugins and their categorization.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from .. import defaults
from ..components import AudioComponent, Component
from ..tags import Category, MusicApps
from .plugins import Plugins

logger = logging.getLogger(__name__)


@dataclass
class Logic:
    """Main interface for Logic Pro plugin and category management.

    Provides high-level operations for discovering plugins, managing categories,
    and bulk category assignments.

    Attributes:
        musicapps: MusicApps instance for database access.
        plugins: Plugins collection with search capabilities.
        components: Set of discovered Component bundles.
        categories: Dictionary of category name to Category instance.
        components_path: Path to Audio Components directory.
        tags_path: Path to tags database directory.
    """

    musicapps: MusicApps
    plugins: Plugins
    components: set[Component]
    categories: dict[str, Category]
    components_path: Path = defaults.components_path
    tags_path: Path = defaults.tags_path

    def __init__(
        self,
        *,
        components_path: Path | str = None,
        tags_path: Path | str = None,
        lazy: bool = False,
    ):
        """Initialize Logic plugin manager.

        Args:
            components_path: Custom path to Components directory.
            tags_path: Custom path to tags database.
            lazy: If True, skip automatic discovery.

        Note:
            If lazy=False, automatically calls discover_plugins() and
            discover_categories() which may raise various exceptions.
        """
        self.components_path = (
            Path(components_path) if components_path else defaults.components_path
        )
        self.tags_path = Path(tags_path) if tags_path else defaults.tags_path

        self.tags_path = self.tags_path.expanduser()
        self.components_path = self.components_path.expanduser()

        self.musicapps = MusicApps(tags_path=self.tags_path, lazy=lazy)
        self.plugins = Plugins()
        self.components = set()
        self.categories = {}

        self.lazy = lazy

        logger.debug("Created Logic instance")

        if not lazy:
            self.discover_plugins()
            self.discover_categories()

    def discover_plugins(self) -> "Logic":
        """Scan components directory and load all plugins.

        Iterates through .component bundles, loading their AudioComponents
        into the plugins collection. Failed components are logged as warnings.

        Returns:
            Logic: Self for method chaining.
        """
        for component_path in self.components_path.glob("*.component"):
            try:
                logger.debug(f"Loading component {component_path}")
                component = Component(
                    component_path, lazy=self.lazy, musicapps=self.musicapps
                )
                self.components.add(component)
                logger.debug(f"Loading plugins for {component.name}")
                for plugin in component.audio_components:
                    self.plugins.add(plugin, lazy=self.lazy)
            except Exception as e:
                logger.warning(f"Failed to load component {component_path}: {e}")

        return self

    def discover_categories(self) -> "Logic":
        """Load all categories from the MusicApps database.

        Returns:
            Logic: Self for method chaining.

        Raises:
            MusicAppsLoadError: If database files cannot be loaded.
        """
        for category in self.musicapps.tagpool.categories.keys():
            logger.debug(f"Loading category {category}")
            self.categories[category] = Category(
                category, musicapps=self.musicapps, lazy=self.lazy
            )

        return self

    def sync_category_plugin_amount(self, category: Category | str) -> "Logic":
        if isinstance(category, str):
            category = self.categories[category]
        logger.debug(f"Syncing plugin amount for {category.name}")
        category.update_plugin_amount(
            len(
                self.plugins.get_by_category(
                    category.name if isinstance(category, Category) else category
                )
            )
        )
        return self

    def sync_all_categories_plugin_amount(self) -> "Logic":
        for category in self.categories.values():
            self.sync_category_plugin_amount(category)
        return self

    def search_categories(self, query: str) -> set[Category]:
        return {
            category
            for category in self.categories.values()
            if query in category.name.lower()
        }

    def introduce_category(self, name: str) -> Category:
        return Category.introduce(name, musicapps=self.musicapps, lazy=self.lazy)

    def add_plugins_to_category(
        self, category: Category, plugins: set[AudioComponent]
    ) -> "Logic":
        for plugin in plugins:
            plugin.add_to_category(category)
        self.sync_category_plugin_amount(category)
        return self

    def move_plugins_to_category(
        self, category: Category, plugins: set[AudioComponent]
    ) -> "Logic":
        for plugin in plugins:
            plugin.move_to_category(category)
        self.sync_category_plugin_amount(category)
        return self

    def remove_plugins_from_category(
        self, category: Category, plugins: set[AudioComponent]
    ) -> "Logic":
        for plugin in plugins:
            plugin.remove_from_category(category)
        self.sync_category_plugin_amount(category)
        return self


__all__ = ["Logic"]
