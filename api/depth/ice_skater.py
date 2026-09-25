from __future__ import annotations

from dataclasses import dataclass

from ..skaters.roster_skater import RosterSkater


@dataclass( frozen=True )
class IceSkater( RosterSkater ):
   implied: float
   last_toi: float | None
   availability: float
