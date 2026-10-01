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
   short_handed_goals: int
   short_handed_points: int
   projected_toi: float | None = None


   def __post_init__( self ) -> None:
      power_play_assists = self.power_play_points - self.power_play_goals
      special_teams_goals = self.power_play_goals + self.short_handed_goals
      special_teams_assists = (
         power_play_assists
         + self.short_handed_points
         - self.short_handed_goals )
      special_teams_points = self.power_play_points + self.short_handed_points

      if (
            special_teams_goals > self.goals
            or special_teams_assists > self.assists
            or special_teams_points > self.points ):
         raise ValueError( 'Special-teams projection exceeds total scoring projection' )


   def to_dict( self ) -> dict[ str, int | str | None ]:
      payload = {
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'gamesPlayed': self.games_played,
         'powerPlayGoals': self.power_play_goals,
         'powerPlayPoints': self.power_play_points,
         'shortHandedGoals': self.short_handed_goals,
         'shortHandedPoints': self.short_handed_points,
         'projectedToi': (
            None if self.projected_toi is None
            else Time.clock_string( self.projected_toi ) ),
      }

      return payload
