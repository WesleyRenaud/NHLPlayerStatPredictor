from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionTrajectoryChange():
   age: int
   prior_pace: float
   latest_pace: float
   following_pace: float
   multiplier: float
   games: int


   def relative( self ) -> float:
      peak = max( self.latest_pace, self.prior_pace )

      if peak == 0.0:
         return 0.0

      return abs( self.latest_pace - self.prior_pace ) / peak
