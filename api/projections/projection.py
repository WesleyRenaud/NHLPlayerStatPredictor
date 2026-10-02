from __future__ import annotations

from dataclasses import dataclass

from ..time import Time

@dataclass( frozen=True )
class Projection():
   even_strength_goals: int
   even_strength_points: int
   penalty_minutes: int | None
   games_played: int
   power_play_goals: int
   power_play_points: int
   short_handed_goals: int
   short_handed_points: int
   projected_toi: float | None = None
   shots: int | None = None
   shooting_percentage: float | None = None


   @property
   def goals( self ) -> int:
      return self.even_strength_goals + self.power_play_goals + self.short_handed_goals


   @property
   def assists( self ) -> int:
      return self.points - self.goals


   @property
   def points( self ) -> int:
      return self.even_strength_points + self.power_play_points + self.short_handed_points


   def to_dict( self ) -> dict[ str, int | float | str | None ]:
      payload = {
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'penaltyMinutes': self.penalty_minutes,
         'gamesPlayed': self.games_played,
         'powerPlayGoals': self.power_play_goals,
         'powerPlayPoints': self.power_play_points,
         'shortHandedGoals': self.short_handed_goals,
         'shortHandedPoints': self.short_handed_points,
         'evenStrengthGoals': self.even_strength_goals,
         'evenStrengthPoints': self.even_strength_points,
         'shots': self.shots,
         'shootingPercentage': self.shooting_percentage,
         'projectedToi': (
            None if self.projected_toi is None
            else Time.clock_string( self.projected_toi ) ),
      }

      return payload
