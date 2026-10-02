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


   def full_season_pace( self, games_remaining: int ) -> Types.JsonObject | None:
      if not self.games_played:
         return None

      if not games_remaining:
         return self.stats_dict()

      games = self.games_played + games_remaining
      scale = games / self.games_played
      even_strength_goals = round( self.even_strength_goals * scale )
      even_strength_assists = round( ( self.even_strength_points - self.even_strength_goals ) * scale )
      power_play_goals = round( self.power_play_goals * scale )
      power_play_assists = round( ( self.power_play_points - self.power_play_goals ) * scale )
      short_handed_goals = round( self.short_handed_goals * scale )
      short_handed_assists = round( ( self.short_handed_points - self.short_handed_goals ) * scale )
      goals = even_strength_goals + power_play_goals + short_handed_goals
      assists = even_strength_assists + power_play_assists + short_handed_assists
      return {
         **self.stats_dict(),
         'gamesPlayed': games,
         'goals': goals,
         'assists': assists,
         'points': goals + assists,
         'penaltyMinutes': round( self.penalty_minutes * scale ),
         'evenStrengthGoals': even_strength_goals,
         'evenStrengthPoints': even_strength_goals + even_strength_assists,
         'powerPlayGoals': power_play_goals,
         'powerPlayPoints': power_play_goals + power_play_assists,
         'shortHandedGoals': short_handed_goals,
         'shortHandedPoints': short_handed_goals + short_handed_assists,
         'shots': round( self.shots * scale ),
      }
