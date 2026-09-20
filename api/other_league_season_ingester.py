from __future__ import annotations

from concurrent.futures import as_completed, ThreadPoolExecutor

from .nhl_client import NhlClient
from .other_league_season_builder import OtherLeagueSeasonBuilder
from .other_league_skater_season import OtherLeagueSkaterSeason
from .season_length import SeasonLength


class OtherLeagueSeasonIngester():
   WORKERS = 16
   PROGRESS_EVERY = 100


   @classmethod
   def build_rows(
         cls,
         player_ids: list[ int ],
         seasons: list[ SeasonLength ],
         pace_games: int,
         force: bool = False ) -> list[ OtherLeagueSkaterSeason ]:
      completed: dict[ int, list[ OtherLeagueSkaterSeason ] ] = {}
      total = len( player_ids )
      finished = 0

      with ThreadPoolExecutor( max_workers=OtherLeagueSeasonIngester.WORKERS ) as executor:
         futures = {
            executor.submit(
               cls._rows_for_player,
               player_id,
               seasons,
               pace_games,
               force ): player_id
            for player_id in player_ids
         }

         for future in as_completed( futures ):
            player_id = futures[ future ]
            completed[ player_id ] = future.result()
            finished += 1

            if (
                  finished == 1
                  or finished % OtherLeagueSeasonIngester.PROGRESS_EVERY == 0
                  or finished == total ):
               print( f'Fetching landings { finished }/{ total }...', flush=True )

      return [
         row
         for player_id in player_ids
         for row in completed[ player_id ]
      ]


   @classmethod
   def _rows_for_player(
         cls,
         player_id: int,
         seasons: list[ SeasonLength ],
         pace_games: int,
         force: bool ) -> list[ OtherLeagueSkaterSeason ]:
      try:
         landing = NhlClient.player_landing( player_id, force=force )
      except RuntimeError:
         return []

      return OtherLeagueSeasonBuilder.build( landing, seasons, pace_games )
