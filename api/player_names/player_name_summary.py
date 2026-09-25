from __future__ import annotations

from dataclasses import dataclass

from ..season import Season
from ..skaters.skater_position import SkaterPosition
from ..skaters.team import Team


@dataclass( frozen=True )
class PlayerNameSummary():
   player_id: int
   player_name: str
   position: SkaterPosition
   team: Team
   first_season_id: int


   def to_dict( self ) -> dict[ str, object ]:
      return {
         'playerId': self.player_id,
         'playerName': self.player_name,
         'position': self.position.value,
         'team': self.team.value,
         'firstSeason': Season.label( self.first_season_id ),
      }
