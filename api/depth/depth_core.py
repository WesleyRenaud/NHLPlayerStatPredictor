from __future__ import annotations

from dataclasses import dataclass

from .ice_skater import IceSkater


@dataclass( frozen=True )
class DepthCore():
   regulars: list[ IceSkater ]
   extras: list[ IceSkater ]
