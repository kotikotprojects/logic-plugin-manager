import plistlib
from dataclasses import dataclass
from pathlib import Path

from ..exceptions import CannotParseTagsetError, NonexistentTagsetError


@dataclass
class Tagset:
    tags_id: str
    nickname: str
    shortname: str
    tags: dict[str, str]

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
            raise CannotParseTagsetError(f"An error occurred: {e}")

    def load(self) -> "Tagset":
        tagset_data = self._parse_plist()

        self.tags_id = self.path.name.removesuffix(".tagset")
        self.nickname = tagset_data.get("nickname")
        self.shortname = tagset_data.get("shortname")
        self.tags = tagset_data.get("tags") or {}

        return self


__all__ = ["Tagset"]
