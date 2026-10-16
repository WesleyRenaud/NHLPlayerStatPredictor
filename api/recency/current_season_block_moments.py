from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class CurrentSeasonBlockMoments():
   interval: int
   samples: int
   numerator: float
   denominator: float


   def adding( self, gap: float, season_gap: float ) -> CurrentSeasonBlockMoments:
      return CurrentSeasonBlockMoments(
         self.interval,
         self.samples + 1,
         self.numerator + season_gap * gap,
         self.denominator + gap * gap )
