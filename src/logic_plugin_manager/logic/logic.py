from dataclasses import dataclass
from pathlib import Path

from .. import defaults
from ..components import Component
from ..tags import MusicApps
from .plugins import Plugins


@dataclass
class Logic:
    musicapps: MusicApps
    plugins: Plugins
    components: set[Component]
    components_path: Path = defaults.components_path
    tags_path: Path = defaults.tags_path

    def __init__(
        self,
        *,
        components_path: Path | str = None,
        tags_path: Path | str = None,
        lazy: bool = False,
    ):
        self.components_path = (
            Path(components_path) if components_path else defaults.components_path
        )
        self.tags_path = Path(tags_path) if tags_path else defaults.tags_path

        self.tags_path = self.tags_path.expanduser()
        self.components_path = self.components_path.expanduser()

        self.musicapps = MusicApps(tags_path=self.tags_path, lazy=lazy)
        self.plugins = Plugins()
        self.components = set()

        self.lazy = lazy

        if not lazy:
            self.discover_plugins()

    def discover_plugins(self):
        for component_path in self.components_path.glob("*.component"):
            try:
                component = Component(component_path, lazy=self.lazy)
                self.components.add(component)
                for plugin in component.audio_components:
                    self.plugins.add(plugin, lazy=self.lazy)
            except Exception as e:
                assert e
                continue


__all__ = ["Logic"]
