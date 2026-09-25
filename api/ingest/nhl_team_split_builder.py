from __future__ import annotations

from .nhl_client import NhlClient
from ..projections.previous_season_nhl_skater import PreviousSeasonNhlSkater
from ..projections.season_pace import SeasonPace
from ..season import Season
from ..skaters.skater_position import SkaterPosition
from ..skaters.team import Team
from ..types import Types


class NhlTeamSplitBuilder():
   @classmethod
   def build(
         cls,
         landings: dict[ int, Types.JsonObject ],
         season_id: int,
         pace_games: int ) -> list[ PreviousSeasonNhlSkater ]:
      rows: list[ PreviousSeasonNhlSkater ] = []

      for landing in landings.values():
         rows.extend( cls._rows( landing, season_id, pace_games ) )

      return sorted(
         rows,
         key=lambda row: ( row.player_id, row.team.value ) )


   @classmethod
   def _rows(
         cls,
         landing: Types.JsonObject,
         season_id: int,
         pace_games: int ) -> list[ PreviousSeasonNhlSkater ]:
      player_id = int( landing[ 'playerId' ] )
      position = SkaterPosition( str( landing[ 'position' ] ) )
      return [
         cls._parse( player_id, position, raw, pace_games )
         for raw in cls._totals( landing, season_id )
      ]


   @classmethod
   def _parse(
         cls,
         player_id: int,
         position: SkaterPosition,
         raw: Types.JsonObject,
         pace_games: int ) -> PreviousSeasonNhlSkater:
      games_played = int( raw[ 'gamesPlayed' ] )
      goals = float( raw[ 'goals' ] )
      assists = float( raw[ 'assists' ] )
      return PreviousSeasonNhlSkater(
         player_id,
         games_played,
         SeasonPace(
            Season.pace( goals, games_played, pace_games ),
            Season.pace( assists, games_played, pace_games ) ),
         position,
         cls._team( raw ) )


   @classmethod
   def _team( cls, raw: Types.JsonObject ) -> Team:
      value = raw[ 'teamName' ]

      if isinstance( value, dict ):
         return Team.from_name( str( value[ 'default' ] ) )

      return Team.from_name( str( value ) )


   @classmethod
   def _totals(
         cls,
         landing: Types.JsonObject,
         season_id: int | None = None ) -> Types.JsonObjectList:
      raw_rows = landing.get( 'seasonTotals' ) or []

      if not isinstance( raw_rows, list ):
         return []

      return [
         row for row in raw_rows
         if isinstance( row, dict )
         and row[ 'gameTypeId' ] == NhlClient.REGULAR_SEASON_GAME_TYPE_ID
         and str( row[ 'leagueAbbrev' ] ) == 'NHL'
         and row.get( 'gamesPlayed' )
         and ( season_id is None or int( row[ 'season' ] ) == season_id )
      ]
