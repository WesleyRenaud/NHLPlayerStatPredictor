from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass( frozen=True )
class DraftPickModifier():
   intercept: float
   log_pick_coefficient: float


   def factor( self, draft_pick: int | None ) -> float:
      if draft_pick is None:
         return 1.0
      return self.intercept + self.log_pick_coefficient * math.log( draft_pick )
