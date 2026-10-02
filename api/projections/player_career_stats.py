from __future__ import annotations

from dataclasses import dataclass

from ..skaters.skater_stat_rates import SkaterStatRates
from ..skaters.skater_summary import SkaterSummary
from ..time import Time
from ..types import Types


@dataclass( frozen=True )
class PlayerCareerStats():
   games_played: int
   goals: int
   assists: int
   points: int
   penalty_minutes: int
   shots: int
   even_strength_goals: int
   even_strength_points: int
   power_play_goals: int
   power_play_points: int
   short_handed_goals: int
   short_handed_points: int
   total_ice_seconds: float


   @classmethod
   def from_summaries( cls, summaries: list[ SkaterSummary ] ) -> PlayerCareerStats:
      return cls(
         games_played=sum( season.games_played for season in summaries ),
         goals=sum( season.goals for season in summaries ),
         assists=sum( season.assists for season in summaries ),
         points=sum( season.points for season in summaries ),
         penalty_minutes=sum( season.penalty_minutes for season in summaries ),
         shots=sum( season.shots for season in summaries ),
         even_strength_goals=sum( season.even_strength_goals for season in summaries ),
         even_strength_points=sum( season.even_strength_points for season in summaries ),
         power_play_goals=sum( season.power_play_goals for season in summaries ),
         power_play_points=sum( season.power_play_points for season in summaries ),
         short_handed_goals=sum( season.short_handed_goals for season in summaries ),
         short_handed_points=sum( season.short_handed_points for season in summaries ),
         total_ice_seconds=sum( season.time_on_ice_per_game * season.games_played for season in summaries ) )


   @property
   def shooting_percentage( self ) -> float | None:
      return SkaterStatRates.shooting_percentage( self.goals, self.shots )


   @property
   def time_on_ice_per_game( self ) -> float:
      return SkaterStatRates.time_on_ice_per_game( self.total_ice_seconds, self.games_played )


   def to_dict( self ) -> Types.JsonObject:
      ice = self.time_on_ice_per_game
      return {
         'gamesPlayed': self.games_played,
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'penaltyMinutes': self.penalty_minutes,
         'shots': self.shots,
         'evenStrengthGoals': self.even_strength_goals,
         'evenStrengthPoints': self.even_strength_points,
         'powerPlayGoals': self.power_play_goals,
         'powerPlayPoints': self.power_play_points,
         'shortHandedGoals': self.short_handed_goals,
         'shortHandedPoints': self.short_handed_points,
         'shootingPercentage': self.shooting_percentage,
         'timeOnIcePerGame': Time.clock_string_from_seconds( ice ),
      }
