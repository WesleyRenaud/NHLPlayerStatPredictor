from __future__ import annotations

from dataclasses import dataclass

from .player_history_season import PlayerHistorySeason
from ..skaters.skater_summary import SkaterSummary
from ..time import Time
from ..types import Types


@dataclass( frozen=True )
class NhlHistorySeason( PlayerHistorySeason ):
   penalty_minutes: int
   shots: int
   even_strength_goals: int
   even_strength_points: int
   power_play_goals: int
   power_play_points: int
   short_handed_goals: int
   short_handed_points: int
   time_on_ice_per_game: str


   @classmethod
   def from_summary( cls, season_id: int, summary: SkaterSummary ) -> NhlHistorySeason:
      return cls(
         season_id=season_id,
         league='NHL',
         team=', '.join( team.value for team in summary.team_abbrevs ),
         games_played=summary.games_played,
         goals=summary.goals,
         assists=summary.assists,
         points=summary.points,
         penalty_minutes=summary.penalty_minutes,
         shots=summary.shots,
         even_strength_goals=summary.even_strength_goals,
         even_strength_points=summary.even_strength_points,
         power_play_goals=summary.power_play_goals,
         power_play_points=summary.power_play_points,
         short_handed_goals=summary.short_handed_goals,
         short_handed_points=summary.short_handed_points,
         time_on_ice_per_game=Time.clock_string_from_seconds( summary.time_on_ice_per_game ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         **super().to_dict(),
         'evenStrengthGoals': self.even_strength_goals,
         'evenStrengthPoints': self.even_strength_points,
      }
