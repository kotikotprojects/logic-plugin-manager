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
    tags_id: str
    nickname: str
    shortname: str
    tags: dict[str, str]
    __raw_data: dict[str, str | dict[str, str]] = field(repr=False)

    def __init__(self, path: Path, *, lazy: bool = False):
        self.path = path.with_suffix(".tagset")
        self.lazy = lazy

        if not lazy:
            self.load()

    def _parse_plist(self):
        if not self.path.exists():
            raise NonexistentTagsetError(f".tagset not found at {self.path}")
        try:
            with open(self.path, "rb") as fp:
                plist_data = plistlib.load(fp)
                return plist_data
        except Exception as e:
            raise CannotParseTagsetError(f"An error occurred: {e}") from e

    def _write_plist(self):
        try:
            with open(self.path, "wb") as fp:
                plistlib.dump(self.__raw_data, fp)
        except Exception as e:
            raise TagsetWriteError(f"An error occurred: {e}") from e

    def load(self) -> "Tagset":
        self.__raw_data = self._parse_plist()

        self.tags_id = self.path.name.removesuffix(".tagset")
        self.nickname = self.__raw_data.get("nickname")
        self.shortname = self.__raw_data.get("shortname")
        self.tags = self.__raw_data.get("tags") or {}

        return self

    def set_nickname(self, nickname: str):
        self.load()
        self.__raw_data["nickname"] = nickname
        self._write_plist()
        self.load()

    def set_shortname(self, shortname: str):
        self.load()
        self.__raw_data["shortname"] = shortname
        self._write_plist()
        self.load()

    def set_tags(self, tags: dict[str, str]):
        self.load()
        self.__raw_data["tags"] = tags
        self._write_plist()
        self.load()

    def add_tag(self, tag: str, value: str):
        self.load()
        self.tags[tag] = value
        self._write_plist()
        self.load()

    def remove_tag(self, tag: str):
        self.load()
        del self.tags[tag]
        self._write_plist()
        self.load()

    def move_to_tag(self, tag: str, value: str):
        self.load()
        self.tags.clear()
        self.tags[tag] = value
        self._write_plist()
        self.load()


__all__ = ["Tagset"]
