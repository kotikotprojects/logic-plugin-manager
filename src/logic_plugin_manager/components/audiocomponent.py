from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .. import defaults
from ..exceptions import CannotParseComponentError
from ..tags import Tagset


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

    def __init__(
        self, data: dict, *, lazy: bool = False, tags_path: Path = defaults.tags_path
    ):
        self.tags_path = tags_path
        self.lazy = lazy

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
        except Exception as e:
            raise CannotParseComponentError(f"An error occurred while parsing: {e}")

        if not lazy:
            self.load()

    def load(self) -> "AudioComponent":
        self.tagset = Tagset(self.tags_path / self.tags_id, lazy=self.lazy)
        return self

    def __eq__(self, other):
        if not isinstance(other, AudioComponent):
            return NotImplemented
        return self.tags_id == other.tags_id

    def __hash__(self):
        return hash(self.tags_id)


__all__ = ["AudioComponent", "AudioUnitType"]
