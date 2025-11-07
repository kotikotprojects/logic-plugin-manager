import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .. import defaults
from ..exceptions import CannotParseComponentError
from ..tags import Category, MusicApps, Tagset

logger = logging.getLogger(__name__)


class AudioUnitType(Enum):
    AUFX = ("aufx", "Audio FX", "Effect")
    AUMU = ("aumu", "Instrument", "Music Device")
    AUMF = ("aumf", "MIDI-controlled Effects", "Music Effect")
    AUMI = ("aumi", "MIDI FX", "MIDI Generator")
    AUGN = ("augn", "Generator", "Generator")

    @property
    def code(self) -> str:
        return self.value[0]

    @property
    def display_name(self) -> str:
        return self.value[1]

    @property
    def alt_name(self) -> str:
        return self.value[2]

    @classmethod
    def from_code(cls, code: str) -> "AudioUnitType | None":
        code_lower = code.lower()
        for unit_type in cls:
            if unit_type.code == code_lower:
                return unit_type
        return None

    @classmethod
    def search(cls, query: str) -> list["AudioUnitType"]:
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
        if not isinstance(other, AudioComponent):
            return NotImplemented
        return self.tags_id == other.tags_id

    def __hash__(self):
        return hash(self.tags_id)

    def set_nickname(self, nickname: str) -> "AudioComponent":
        self.tagset.set_nickname(nickname)
        self.load()
        return self

    def set_shortname(self, shortname: str) -> "AudioComponent":
        self.tagset.set_shortname(shortname)
        self.load()
        return self

    def set_categories(self, categories: list[Category]) -> "AudioComponent":
        self.tagset.set_tags({category.name: "user" for category in categories})
        self.load()
        return self

    def add_to_category(self, category: Category) -> "AudioComponent":
        self.tagset.add_tag(category.name, "user")
        self.load()
        return self

    def remove_from_category(self, category: Category) -> "AudioComponent":
        self.tagset.remove_tag(category.name)
        self.load()
        return self

    def move_to_category(self, category: Category) -> "AudioComponent":
        self.tagset.move_to_tag(category.name, "user")
        self.load()
        return self

    def move_to_parents(self) -> "AudioComponent":
        for category in self.categories:
            self.tagset.add_tag(category.parent.name, "user")
            self.tagset.remove_tag(category.name)
        self.load()
        return self


__all__ = ["AudioComponent", "AudioUnitType"]
