from __future__ import annotations

from dataclasses import dataclass

from .season_pace import SeasonPace
from ..skaters.skater_position import SkaterPosition
from ..skaters.team import Team


@dataclass( frozen=True )
class CurrentSeasonNhlSkater():
   player_id: int
   pace: SeasonPace
   team: Team
   position: SkaterPosition


   @property
   def contribution( self ) -> float:
      return self.pace.goals + self.pace.assists
