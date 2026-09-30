from __future__ import annotations

from dataclasses import dataclass

from ..time import Time

@dataclass( frozen=True )
class Projection():
   goals: int
   assists: int
   points: int
   games_played: int
   power_play_goals: int
   power_play_points: int
   projected_toi: float | None = None


   def __post_init__( self ) -> None:
      power_play_assists = self.power_play_points - self.power_play_goals

      if (
            self.power_play_goals < 0
            or self.power_play_goals > self.goals
            or power_play_assists < 0
            or power_play_assists > self.assists
            or self.power_play_points > self.points ):
         raise ValueError( 'Power-play projection exceeds total scoring projection' )


   def to_dict( self ) -> dict[ str, int | str | None ]:
      payload = {
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'gamesPlayed': self.games_played,
         'powerPlayGoals': self.power_play_goals,
         'powerPlayPoints': self.power_play_points,
         'projectedToi': (
            None if self.projected_toi is None
            else Time.clock_string( self.projected_toi ) ),
      }

      return payload
