"""Components package for Audio Unit management.

This package provides classes for working with macOS Audio Component bundles
and their associated Audio Units.
"""

from .audiocomponent import AudioComponent, AudioUnitType
from .component import Component

__all__ = ["AudioComponent", "AudioUnitType", "Component"]
