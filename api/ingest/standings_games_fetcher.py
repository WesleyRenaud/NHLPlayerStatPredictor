from __future__ import annotations

from datetime import date

from .nhl_client import NhlClient
from .season_games import SeasonGames
from ..skaters.team import Team


class StandingsGamesFetcher():
   @classmethod
   def games_played( cls, season_id: int, team: Team, on_date: date ) -> int:
      return SeasonGames.played( season_id, on_date, lambda: cls._played( season_id, team ) )


   @classmethod
   def _played( cls, season_id: int, team: Team ) -> int:
      standing = next(
         row for row in NhlClient.standings()[ 'standings' ]
         if int( row[ 'seasonId' ] ) == season_id and row[ 'teamAbbrev' ][ 'default' ] == team.value )
      return int( standing[ 'gamesPlayed' ] )
