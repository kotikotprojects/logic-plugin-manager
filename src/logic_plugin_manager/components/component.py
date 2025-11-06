import plistlib
from dataclasses import dataclass
from pathlib import Path

from .. import defaults
from ..exceptions import (
    CannotParseComponentError,
    CannotParsePlistError,
    NonexistentPlistError,
    OldComponentFormatError,
)
from .audiocomponent import AudioComponent


@dataclass
class Component:
    name: str
    bundle_id: str
    short_version: str
    version: str
    audio_components: list[AudioComponent]

    def __init__(
        self, path: Path, *, lazy: bool = False, tags_path: Path = defaults.tags_path
    ):
        self.path = path if path.suffix == ".component" else Path(f"{path}.component")
        self.lazy = lazy
        self.tags_path = tags_path
        if not lazy:
            self.load()

    def _parse_plist(self):
        info_plist_path = self.path / "Contents" / "Info.plist"
        if not info_plist_path.exists():
            raise NonexistentPlistError(f"Info.plist not found at {info_plist_path}")

        try:
            with open(info_plist_path, "rb") as fp:
                plist_data = plistlib.load(fp)
                return plist_data
        except Exception as e:
            raise CannotParsePlistError(f"An error occurred: {e}")

    def load(self) -> "Component":
        plist_data = self._parse_plist()

        try:
            self.name = self.path.name.removesuffix(".component")
            self.bundle_id = plist_data["CFBundleIdentifier"]
            self.version = plist_data["CFBundleVersion"]
            self.short_version = plist_data["CFBundleShortVersionString"]
        except Exception as e:
            raise CannotParsePlistError(
                f"An error occurred while extracting: {e}"
            ) from e
        try:
            self.audio_components = [
                AudioComponent(name, lazy=self.lazy, tags_path=self.tags_path)
                for name in plist_data["AudioComponents"]
            ]
        except KeyError as e:
            raise OldComponentFormatError(
                "This component is in an old format and cannot be loaded"
            ) from e
        except Exception as e:
            raise CannotParseComponentError(
                "An error occurred while loading components"
            ) from e

        return self

    def __hash__(self):
        return hash(self.bundle_id)


__all__ = ["Component"]
