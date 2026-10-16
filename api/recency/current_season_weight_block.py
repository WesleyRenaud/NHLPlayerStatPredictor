from __future__ import annotations

from dataclasses import dataclass

from .current_season_block_moments import CurrentSeasonBlockMoments


@dataclass( frozen=True )
class CurrentSeasonWeightBlock():
   intervals: list[ int ]
   total: float
   mass: float


   @classmethod
   def from_moments( cls, moments: CurrentSeasonBlockMoments ) -> CurrentSeasonWeightBlock:
      share = moments.numerator / moments.denominator
      weight = min( 1.0, max( 0.0, share ) )
      return cls( [ moments.interval ], weight * moments.denominator, moments.denominator )


   def weight( self ) -> float:
      return self.total / self.mass


   def merging( self, later: CurrentSeasonWeightBlock ) -> CurrentSeasonWeightBlock:
      return CurrentSeasonWeightBlock(
         self.intervals + later.intervals,
         self.total + later.total,
         self.mass + later.mass )
