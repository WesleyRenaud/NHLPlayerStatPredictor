from __future__ import annotations

from dataclasses import dataclass

from .season_pace import SeasonPace
from ..skaters.skater_position import SkaterPosition


@dataclass( frozen=True )
class PreviousSeasonSkater():
   player_id: int
   games: int
   pace: SeasonPace
   position: SkaterPosition


   @property
   def contribution( self ) -> float:
      return self.games * ( self.pace.goals + self.pace.assists )
