from __future__ import annotations

from dataclasses import dataclass

from .previous_season_nhl_skater import PreviousSeasonNhlSkater
from .previous_season_skater import PreviousSeasonSkater


@dataclass( frozen=True )
class PreviousSeasonGroup():
   nhl: list[ PreviousSeasonNhlSkater ]
   other: list[ PreviousSeasonSkater ]


   def skaters( self ) -> list[ PreviousSeasonSkater ]:
      return [ *self.nhl, *self.other ]
