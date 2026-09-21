from .nhl_client import NhlClient
from .projections.career_pace import CareerPace
from .projections.last_season_nhl_skater import LastSeasonNhlSkater
from .season import Season
from .team import Team
from .types import Types


class NhlTeamSplitBuilder():
   @classmethod
   def build(
         cls,
         landings: dict[ int, Types.JsonObject ],
         season_id: int,
         pace_games: int ) -> list[ LastSeasonNhlSkater ]:
      rows: list[ LastSeasonNhlSkater ] = []

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
         pace_games: int ) -> list[ LastSeasonNhlSkater ]:
      player_id = int( landing[ 'playerId' ] )
      return [
         cls._parse( player_id, raw, pace_games )
         for raw in cls._totals( landing, season_id )
      ]


   @classmethod
   def _parse(
         cls,
         player_id: int,
         raw: Types.JsonObject,
         pace_games: int ) -> LastSeasonNhlSkater:
      games_played = int( raw[ 'gamesPlayed' ] )
      goals = float( raw[ 'goals' ] )
      assists = float( raw[ 'assists' ] )
      games = float( games_played )
      return LastSeasonNhlSkater(
         player_id,
         games,
         CareerPace(
            Season.pace( goals, games, pace_games ),
            Season.pace( assists, games, pace_games ) ),
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
         season_id: int ) -> Types.JsonObjectList:
      raw_rows = landing.get( 'seasonTotals' ) or []

      if not isinstance( raw_rows, list ):
         return []

      return [
         row for row in raw_rows
         if isinstance( row, dict )
         and row[ 'gameTypeId' ] == NhlClient.REGULAR_SEASON_GAME_TYPE_ID
         and str( row[ 'leagueAbbrev' ] ) == 'NHL'
         and int( row[ 'season' ] ) == season_id
         and row.get( 'gamesPlayed' )
      ]
