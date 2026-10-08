from __future__ import annotations

from dataclasses import dataclass

from .scoring_paces import ScoringPaces


@dataclass( frozen=True )
class WeightedScoring():
   games: int
   scoring: ScoringPaces


   @classmethod
   def empty( cls ) -> WeightedScoring:
      return cls( 0, ScoringPaces.zero() )


   def adding( self, played: int, paces: ScoringPaces | None ) -> WeightedScoring:
      if paces is None:
         return self

      return WeightedScoring(
         self.games + played,
         self.scoring.adding( paces.scaled( played ) ) )


   def per_game( self ) -> ScoringPaces | None:
      if not self.games:
         return None

      return self.scoring.per_game( self.games )
