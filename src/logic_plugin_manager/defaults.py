from pathlib import Path

components_path: Path = Path("/Library/Audio/Plug-Ins/Components")
tags_path: Path = Path("~/Music/Audio Music Apps/Databases/Tags").expanduser()


__all__ = ["components_path", "tags_path"]
