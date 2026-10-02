from __future__ import annotations

from dataclasses import dataclass

from ..season import Season
from ..skaters.skater_stat_rates import SkaterStatRates
from ..types import Types


@dataclass( frozen=True )
class PlayerHistorySeason():
   season_id: int
   league: str
   team: str
   games_played: int
   goals: int
   assists: int
   points: int
   penalty_minutes: int | None
   shots: int | None
   power_play_goals: int | None
   power_play_points: int | None
   short_handed_goals: int | None
   short_handed_points: int | None
   time_on_ice_per_game: str | None


   @property
   def shooting_percentage( self ) -> float | None:
      return SkaterStatRates.shooting_percentage( self.goals, self.shots )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'seasonLabel': Season.label( self.season_id ),
         'seasonId': self.season_id,
         'league': self.league,
         'team': self.team,
         'gamesPlayed': self.games_played,
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'penaltyMinutes': self.penalty_minutes,
         'shots': self.shots,
         'powerPlayGoals': self.power_play_goals,
         'powerPlayPoints': self.power_play_points,
         'shortHandedGoals': self.short_handed_goals,
         'shortHandedPoints': self.short_handed_points,
         'timeOnIcePerGame': self.time_on_ice_per_game,
         'shootingPercentage': self.shooting_percentage,
      }
