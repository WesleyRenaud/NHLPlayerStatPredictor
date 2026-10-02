from __future__ import annotations

from dataclasses import dataclass

from .scoring_paces import ScoringPaces
from ..types import Types


@dataclass( frozen=True )
class ScoringComponentShares():
   age: int
   even_strength_goals: float
   even_strength_assists: float
   power_play_goals: float
   power_play_assists: float
   short_handed_goals: float
   short_handed_assists: float


   def split( self, goals: float, assists: float ) -> ScoringPaces:
      return ScoringPaces(
         even_strength_goals=goals * self.even_strength_goals,
         even_strength_assists=assists * self.even_strength_assists,
         power_play_goals=goals * self.power_play_goals,
         power_play_assists=assists * self.power_play_assists,
         short_handed_goals=goals * self.short_handed_goals,
         short_handed_assists=assists * self.short_handed_assists )


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> ScoringComponentShares:
      return cls(
         age=int( row[ 'age' ] ),
         even_strength_goals=float( row[ 'even_strength_goals' ] ),
         even_strength_assists=float( row[ 'even_strength_assists' ] ),
         power_play_goals=float( row[ 'power_play_goals' ] ),
         power_play_assists=float( row[ 'power_play_assists' ] ),
         short_handed_goals=float( row[ 'short_handed_goals' ] ),
         short_handed_assists=float( row[ 'short_handed_assists' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'age': self.age,
         'even_strength_goals': self.even_strength_goals,
         'even_strength_assists': self.even_strength_assists,
         'power_play_goals': self.power_play_goals,
         'power_play_assists': self.power_play_assists,
         'short_handed_goals': self.short_handed_goals,
         'short_handed_assists': self.short_handed_assists,
      }
