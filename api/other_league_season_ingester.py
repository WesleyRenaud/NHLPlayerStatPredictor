from __future__ import annotations

from .nhl_client import NhlClient
from .other_league_season import OtherLeagueSeason
from .other_league_season_builder import OtherLeagueSeasonBuilder
from .season_length import SeasonLength


class OtherLeagueSeasonIngester():
   @classmethod
   def build_rows(
         cls,
         player_ids: list[ int ],
         seasons: list[ SeasonLength ],
         pace_games: int,
         force: bool = False ) -> list[ OtherLeagueSeason ]:
      rows: list[ OtherLeagueSeason ] = []
      total = len( player_ids )

      for index, player_id in enumerate( player_ids, start=1 ):
         if index == 1 or index % 100 == 0 or index == total:
            print( f'Fetching landings { index }/{ total }...' )

         try:
            landing = NhlClient.player_landing( player_id, force=force )
         except RuntimeError:
            continue

         rows.extend(
            OtherLeagueSeasonBuilder.build( landing, seasons, pace_games ) )

      return rows
