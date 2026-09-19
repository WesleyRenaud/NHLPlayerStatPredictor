from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .shared.enums.position import Position
from .skater_position import SkaterPosition
from .skater_season_key import SkaterSeasonKey
from .team import Team
from .types import Types


@dataclass( frozen=True )
class SkaterSeason():
   player_id: int
   season_id: int
   player_name: str
   position: SkaterPosition
   birth_date: date
   age: float
   team: Team
   games_played: int
   goals: int
   assists: int
   points: int
   schedule_games: int
   pace_games: int
   g_pace: float
   a_pace: float
   p_pace: float
   gp_share: float | None


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> SkaterSeason:
      gp_share = row[ 'GP_SHARE' ]
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         season_id=int( row[ 'SEASON_ID' ] ),
         player_name=str( row[ 'PLAYER_NAME' ] ),
         position=SkaterPosition( str( row[ 'POSITION' ] ) ),
         birth_date=date.fromisoformat(
            str( row[ 'BIRTH_DATE' ] ).split( 'T' )[ Position.FIRST ] ),
         age=float( row[ 'AGE' ] ),
         team=Team( str( row[ 'TEAM' ] ) ),
         games_played=int( row[ 'GAMES_PLAYED' ] ),
         goals=int( row[ 'GOALS' ] ),
         assists=int( row[ 'ASSISTS' ] ),
         points=int( row[ 'POINTS' ] ),
         schedule_games=int( row[ 'SCHEDULE_GAMES' ] ),
         pace_games=int( row[ 'PACE_GAMES' ] ),
         g_pace=float( row[ 'G_PACE' ] ),
         a_pace=float( row[ 'A_PACE' ] ),
         p_pace=float( row[ 'P_PACE' ] ),
         gp_share=None if gp_share is None else float( gp_share ) )


   def key( self ) -> SkaterSeasonKey:
      return SkaterSeasonKey( self.player_id, self.season_id )
