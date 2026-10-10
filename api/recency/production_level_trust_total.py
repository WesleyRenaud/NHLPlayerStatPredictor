from __future__ import annotations

from dataclasses import dataclass

from .production_trajectory_change import ProductionTrajectoryChange


@dataclass( frozen=True )
class ProductionLevelTrustTotal():
   age: int
   games: float
   still_present: float
   pace_change: float


   @classmethod
   def empty( cls, age: int ) -> ProductionLevelTrustTotal:
      return cls( age, 0.0, 0.0, 0.0 )


   def including( self, change: ProductionTrajectoryChange ) -> ProductionLevelTrustTotal:
      return self._shifted( change, 1.0 )


   def excluding( self, change: ProductionTrajectoryChange ) -> ProductionLevelTrustTotal:
      return self._shifted( change, -1.0 )


   def _shifted( self, change: ProductionTrajectoryChange, direction: float ) -> ProductionLevelTrustTotal:
      games = direction * float( change.games )
      return ProductionLevelTrustTotal(
         self.age,
         self.games + games,
         self.still_present + games * change.still_present(),
         self.pace_change + games * change.pace_change() )
