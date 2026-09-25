from __future__ import annotations

from dataclasses import dataclass

from ..depth.ice_available import IceAvailable


@dataclass( frozen=True )
class AvailabilityState():
   share: float
   playing: list[ IceAvailable ]
   regulars_out: int
