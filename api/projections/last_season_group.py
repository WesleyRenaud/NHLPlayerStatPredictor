from __future__ import annotations

from dataclasses import dataclass

from .last_season_nhl_skater import LastSeasonNhlSkater
from .last_season_skater import LastSeasonSkater


@dataclass( frozen=True )
class LastSeasonGroup():
   nhl: list[ LastSeasonNhlSkater ]
   other: list[ LastSeasonSkater ]


   def skaters( self ) -> list[ LastSeasonSkater ]:
      return [ *self.nhl, *self.other ]
