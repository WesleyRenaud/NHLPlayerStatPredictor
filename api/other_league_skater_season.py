from __future__ import annotations

from dataclasses import dataclass

from .other_league_season_key import OtherLeagueSeasonKey
from .skater_season import SkaterSeason
from .types import Types


@dataclass( frozen=True )
class OtherLeagueSkaterSeason( SkaterSeason ):
   league: str


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> OtherLeagueSkaterSeason:
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         season_id=int( row[ 'SEASON_ID' ] ),
         age=float( row[ 'AGE' ] ),
         games_played=int( row[ 'GAMES_PLAYED' ] ),
         goals=int( row[ 'GOALS' ] ),
         assists=int( row[ 'ASSISTS' ] ),
         points=int( row[ 'POINTS' ] ),
         g_pace=float( row[ 'G_PACE' ] ),
         a_pace=float( row[ 'A_PACE' ] ),
         league=str( row[ 'LEAGUE' ] ) )


   def key( self ) -> OtherLeagueSeasonKey:
      return OtherLeagueSeasonKey( self.player_id, self.season_id, self.league )
