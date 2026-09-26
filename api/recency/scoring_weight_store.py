from __future__ import annotations

import json
from pathlib import Path

from .age_recency_weights import AgeRecencyWeights
from ..paths import Paths


class ScoringWeightStore():
   FILE_NAME = 'scoring_weights.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, weights: list[ AgeRecencyWeights ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ weight.to_dict() for weight in weights ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ AgeRecencyWeights ]:
      rows = json.loads( cls.path().read_text() )
      return [ AgeRecencyWeights.from_row( row ) for row in rows ]
