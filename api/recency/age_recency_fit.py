from __future__ import annotations

from dataclasses import dataclass

from .age_recency_weights import AgeRecencyWeights
from .recency_weight import RecencyWeight


@dataclass( frozen=True )
class AgeRecencyFit():
   age: int
   weights: list[ RecencyWeight ]
   samples: int


   def row( self ) -> AgeRecencyWeights:
      return AgeRecencyWeights( self.age, self.weights )
