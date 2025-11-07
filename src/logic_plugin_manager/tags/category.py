import logging
from dataclasses import dataclass, field

from ..exceptions import CategoryExistsError, CategoryValidationError
from .musicapps import MusicApps

logger = logging.getLogger(__name__)


@dataclass
class Category:
    name: str
    musicapps: MusicApps = field(repr=False)
    is_root: bool
    plugin_amount: int
    lazy: bool

    def __init__(self, name: str, *, musicapps: MusicApps = None, lazy: bool = False):
        self.name = name
        self.musicapps = musicapps or MusicApps(lazy=lazy)
        self.is_root = False
        self.plugin_amount = 0
        self.lazy = lazy

        if not lazy:
            self.load()

    def load(self):
        logger.debug(f"Validating category {self.name}")
        if self.name not in self.musicapps.tagpool.categories.keys():
            raise CategoryValidationError(f"Category {self.name} not found in tagpool")
        self.plugin_amount = self.musicapps.tagpool.categories[self.name]
        logger.debug(f"Loaded plugin amount for {self.name} - {self.plugin_amount}")
        if self.name == "":
            self.is_root = True
            logger.debug("This is the root category")
            return
        if self.name not in self.musicapps.properties.sorting:
            raise CategoryValidationError(f"Category {self.name} not found in sorting")
        logger.debug(f"Valid category {self.name}")

    @classmethod
    def introduce(cls, name: str, *, musicapps: MusicApps = None, lazy: bool = False):
        logger.debug(f"Introducing category {name}")
        if musicapps is None:
            musicapps = MusicApps()
        try:
            cls(name, musicapps=musicapps, lazy=lazy)
            raise CategoryExistsError(f"Category {name} already exists")
        except CategoryValidationError:
            logger.debug(f"Category {name} doesn't exist, proceeding")
            pass

        musicapps.introduce_category(name)
        logger.debug(f"Introduced category {name}")

        return cls(name, musicapps=musicapps)

    @property
    def parent(self) -> "Category":
        if self.is_root:
            return self
        return self.__class__(
            ":".join(self.name.split(":")[:-1]),
            musicapps=self.musicapps,
            lazy=self.lazy,
        )

    def child(self, name: str) -> "Category":
        return self.__class__(
            f"{self.name}:{name}", musicapps=self.musicapps, lazy=self.lazy
        )

    def delete(self):
        if self.is_root:
            return
        self.musicapps.tagpool.remove_category(self.name)
        self.musicapps.properties.remove_category(self.name)

    def update_plugin_amount(self, amount: int):
        if self.is_root:
            return
        self.musicapps.tagpool.write_category(self.name, amount)
        self.load()

    def move_up(self, steps: int = 1):
        if self.is_root:
            return
        self.musicapps.properties.move_up(self.name, steps)
        self.load()

    def move_down(self, steps: int = 1):
        if self.is_root:
            return
        self.musicapps.properties.move_down(self.name, steps)
        self.load()

    def move_to_top(self):
        if self.is_root:
            return
        self.musicapps.properties.move_to_top(self.name)
        self.load()

    def move_to_bottom(self):
        if self.is_root:
            return
        self.musicapps.properties.move_to_bottom(self.name)
        self.load()

    def move_before(self, other: "Category"):
        if self.is_root:
            return
        self.musicapps.properties.move_before(self.name, other.name)
        self.load()

    def move_after(self, other: "Category"):
        if self.is_root:
            return
        self.musicapps.properties.move_after(self.name, other.name)
        self.load()

    def move_to(self, index: int):
        if self.is_root:
            return
        self.musicapps.properties.move_to_index(self.name, index)
        self.load()

    def swap(self, other: "Category"):
        if self.is_root:
            return
        self.musicapps.properties.swap(self.name, other.name)
        self.load()

    @property
    def index(self):
        return self.musicapps.properties.get_index(self.name)

    @property
    def neighbors(self):
        if self.is_root:
            return None, None
        neighbors = self.musicapps.properties.get_neighbors(self.name)
        if neighbors is None or len(neighbors) != 2:
            return None, None
        return (
            self.__class__(name=neighbors[0], musicapps=self.musicapps),
            self.__class__(name=neighbors[1], musicapps=self.musicapps),
        )

    @property
    def is_first(self):
        return self.musicapps.properties.is_first(self.name)

    @property
    def is_last(self):
        return self.musicapps.properties.is_last(self.name)


__all__ = ["Category"]
