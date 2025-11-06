import plistlib
from dataclasses import dataclass
from pathlib import Path

from .. import defaults
from ..exceptions import MusicAppsLoadError


def _parse_plist(path: Path):
    if not path.exists():
        raise MusicAppsLoadError(f"File not found at {path}")
    try:
        with open(path, "rb") as fp:
            plist_data = plistlib.load(fp)
            return plist_data
    except Exception as e:
        raise MusicAppsLoadError(f"An error occurred: {e}")


@dataclass
class Tagpool:
    categories: dict[str, int]

    def __init__(self, tags_path: Path, *, lazy: bool = False):
        self.path = tags_path / "MusicApps.tagpool"
        self.lazy = lazy

        if not lazy:
            self.load()

    def load(self) -> "Tagpool":
        self.categories = _parse_plist(self.path)
        return self


@dataclass
class Properties:
    sorting: list[str]
    user_sorted: bool

    def __init__(self, tags_path: Path, *, lazy: bool = False):
        self.path = tags_path / "MusicApps.properties"
        self.lazy = lazy

        if not lazy:
            self.load()

    def load(self) -> "Properties":
        properties_data = _parse_plist(self.path)
        self.sorting = properties_data.get("sorting", [])
        self.user_sorted = bool(properties_data.get("user_sorted", False))
        return self


@dataclass
class MusicApps:
    tagpool: Tagpool
    properties: Properties

    def __init__(self, tags_path: Path = defaults.tags_path, *, lazy: bool = False):
        self.path = tags_path
        self.lazy = lazy

        if not lazy:
            self.load()

    def load(self) -> "MusicApps":
        self.tagpool = Tagpool(self.path, lazy=self.lazy)
        self.properties = Properties(self.path, lazy=self.lazy)
        return self


__all__ = ["MusicApps", "Properties", "Tagpool"]
