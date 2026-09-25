from __future__ import annotations

from .nhl_team_split_builder import NhlTeamSplitBuilder
from ..team_factor.club_games import ClubGames
from ..types import Types


class ClubGamesParser():
   @classmethod
   def parse(
         cls,
         landing: Types.JsonObject,
         season_id: int ) -> list[ ClubGames ]:
      return [
         ClubGames(
            NhlTeamSplitBuilder._team( raw ),
            int( raw[ 'gamesPlayed' ] ) )
         for raw in NhlTeamSplitBuilder._totals( landing, season_id )
      ]
