from __future__ import annotations

from dataclasses import dataclass

from .other_league_season_key import OtherLeagueSeasonKey
from .types import Types


@dataclass( frozen=True )
class OtherLeagueSeason():
   player_id: int
   season_id: int
   league: str
   age: float
   games_played: int
   goals: int
   assists: int
   points: int
   g_pace: float
   a_pace: float


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> OtherLeagueSeason:
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         season_id=int( row[ 'SEASON_ID' ] ),
         league=str( row[ 'LEAGUE' ] ),
         age=float( row[ 'AGE' ] ),
         games_played=int( row[ 'GAMES_PLAYED' ] ),
         goals=int( row[ 'GOALS' ] ),
         assists=int( row[ 'ASSISTS' ] ),
         points=int( row[ 'POINTS' ] ),
         g_pace=float( row[ 'G_PACE' ] ),
         a_pace=float( row[ 'A_PACE' ] ) )


   def key( self ) -> OtherLeagueSeasonKey:
      return OtherLeagueSeasonKey( self.player_id, self.season_id, self.league )
