from __future__ import annotations

from dataclasses import dataclass

from .skater_position import SkaterPosition
from .team import Team
from ..time import Time
from ..types import Types


@dataclass( frozen=True )
class SkaterSummary():
   player_id: int
   player_name: str
   position: SkaterPosition
   team_abbrevs: list[ Team ]
   games_played: int
   goals: int
   assists: int
   points: int
   penalty_minutes: int
   power_play_goals: int
   power_play_points: int
   short_handed_goals: int
   short_handed_points: int
   even_strength_goals: int
   even_strength_points: int
   shots: int
   time_on_ice_per_game: float


   @classmethod
   def from_rows( cls, rows: Types.JsonObjectList ) -> list[ SkaterSummary ]:
      return [ cls.from_row( raw ) for raw in rows ]


   @classmethod
   def from_row( cls, raw: Types.JsonObject ) -> SkaterSummary:
      return cls(
         int( raw[ 'playerId' ] ),
         str( raw[ 'skaterFullName' ] ),
         SkaterPosition( str( raw[ 'positionCode' ] ) ),
         [ Team( part ) for part in str( raw[ 'teamAbbrevs' ] ).split( ',' ) ],
         int( raw[ 'gamesPlayed' ] ),
         int( raw[ 'goals' ] ),
         int( raw[ 'assists' ] ),
         int( raw[ 'points' ] ),
         int( raw[ 'penaltyMinutes' ] ),
         int( raw[ 'ppGoals' ] ),
         int( raw[ 'ppPoints' ] ),
         int( raw[ 'shGoals' ] ),
         int( raw[ 'shPoints' ] ),
         int( raw[ 'evGoals' ] ),
         int( raw[ 'evPoints' ] ),
         int( raw[ 'shots' ] ),
         float( raw[ 'timeOnIcePerGame' ] ) )


   @property
   def shooting_percentage( self ) -> float | None:
      return None if not self.shots else 100 * self.goals / self.shots


   def stats_dict( self ) -> Types.JsonObject:
      return {
         'goals': self.goals,
         'assists': self.assists,
         'points': self.points,
         'gamesPlayed': self.games_played,
         'penaltyMinutes': self.penalty_minutes,
         'evenStrengthGoals': self.even_strength_goals,
         'evenStrengthPoints': self.even_strength_points,
         'powerPlayGoals': self.power_play_goals,
         'powerPlayPoints': self.power_play_points,
         'shortHandedGoals': self.short_handed_goals,
         'shortHandedPoints': self.short_handed_points,
         'shots': self.shots,
         'shootingPercentage': self.shooting_percentage,
         'timeOnIcePerGame': Time.clock_string( Time.minutes( self.time_on_ice_per_game ) ),
      }
