from __future__ import annotations

from datetime import date

from .nhl_client import NhlClient
from .season_games import SeasonGames


class SkaterGamesFetcher():
   @classmethod
   def games_played( cls, season_id: int, player_id: int, on_date: date ) -> int:
      return SeasonGames.played( season_id, on_date, lambda: cls._played( season_id, player_id ) )


   @classmethod
   def _played( cls, season_id: int, player_id: int ) -> int:
      played = {
         row.player_id: row.games_played
         for row in NhlClient.skater_summary( season_id )
      }
      return played.get( player_id, 0 )
