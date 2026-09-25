from __future__ import annotations

from ..depth.club_ice import ClubIce
from .nhl_team_split_builder import NhlTeamSplitBuilder
from ..time import Time
from ..types import Types


class ClubIceParser():
   @classmethod
   def parse(
         cls,
         landing: Types.JsonObject,
         season_id: int ) -> list[ ClubIce ]:
      return [
         ClubIce(
            NhlTeamSplitBuilder._team( raw ),
            int( raw[ 'gamesPlayed' ] ),
            Time.clock( str( raw[ 'avgToi' ] ) ) )
         for raw in NhlTeamSplitBuilder._totals( landing, season_id )
      ]
