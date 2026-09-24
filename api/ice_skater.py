from __future__ import annotations

from dataclasses import dataclass

from .roster_skater import RosterSkater


@dataclass( frozen=True )
class IceSkater( RosterSkater ):
   implied: float
   last_toi: float | None
   last_games: int | None
   moved: bool
   availability: float
