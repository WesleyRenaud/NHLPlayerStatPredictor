from __future__ import annotations

from dataclasses import replace

from .nhl_client import NhlClient
from ..skaters.nhl_skater_season import NhlSkaterSeason
from ..types import Types


class PlayoffTotalsMerger():
   NHL = 'NHL'


   @classmethod
   def merge(
         cls,
         rows: list[ NhlSkaterSeason ],
         landings: dict[ int, Types.JsonObject ] ) -> list[ NhlSkaterSeason ]:
      return [ cls._merged( row, landings.get( row.player_id ) ) for row in rows ]


   @classmethod
   def _merged( cls, row: NhlSkaterSeason, landing: Types.JsonObject | None ) -> NhlSkaterSeason:
      totals = [] if landing is None else cls._totals( landing, row.season_id )

      if not totals:
         return row

      return replace(
         row,
         playoff_games=sum( int( raw[ 'gamesPlayed' ] ) for raw in totals ),
         playoff_goals=sum( int( raw[ 'goals' ] ) for raw in totals ),
         playoff_assists=sum( int( raw[ 'assists' ] ) for raw in totals ) )


   @classmethod
   def _totals( cls, landing: Types.JsonObject, season_id: int ) -> Types.JsonObjectList:
      raw_rows = landing.get( 'seasonTotals' ) or []

      if not isinstance( raw_rows, list ):
         return []

      return [
         row for row in raw_rows
         if isinstance( row, dict )
         and row[ 'gameTypeId' ] == NhlClient.PLAYOFF_GAME_TYPE_ID
         and str( row[ 'leagueAbbrev' ] ) == PlayoffTotalsMerger.NHL
         and int( row[ 'season' ] ) == season_id
         and row.get( 'gamesPlayed' )
      ]
