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
   earlier_pace: float | None = None


   def relative( self ) -> float:
      peak = max( self.latest_pace, self.prior_pace )

      if peak == 0.0:
         return 0.0

      return abs( self.latest_pace - self.prior_pace ) / peak


   def is_one_year_dip( self, move: float ) -> bool:
      if move <= 0.0:
         return False

      return self._is_drop_at_least( move ) and self._are_earlier_seasons_level( move )


   def _is_drop_at_least( self, move: float ) -> bool:
      fell = self.latest_pace < self.prior_pace
      swing = self.relative()
      return fell and swing >= move


   def _are_earlier_seasons_level( self, move: float ) -> bool:
      earlier = self.earlier_pace

      if earlier is None:
         return False

      peak = max( earlier, self.prior_pace )

      if peak <= 0.0:
         return False

      return abs( self.prior_pace - earlier ) / peak < move


   def aged_following_pace( self ) -> float:
      return self.following_pace / self.multiplier


   def still_present( self ) -> float:
      return self.aged_following_pace() - self.prior_pace


   def pace_change( self ) -> float:
      return self.latest_pace - self.prior_pace
