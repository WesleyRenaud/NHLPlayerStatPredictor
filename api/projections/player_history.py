from __future__ import annotations

from dataclasses import dataclass

from .nhl_history_season import NhlHistorySeason
from .player_career_stats import PlayerCareerStats
from ..types import Types


@dataclass( frozen=True )
class PlayerHistory():
   seasons: list[ NhlHistorySeason ]
   career: PlayerCareerStats | None


   def to_dict( self ) -> Types.JsonObject:
      return {
         'seasons': [ season.to_dict() for season in self.seasons ],
         'career': None if self.career is None else self.career.to_dict(),
      }
