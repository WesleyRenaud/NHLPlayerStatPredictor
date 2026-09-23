from __future__ import annotations

import json
from pathlib import Path

from .paths import Paths
from .recency_weight import RecencyWeight


class AvailabilityWeightStore():
   FILE_NAME = 'availability_weights.json'

   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, weights: list[ RecencyWeight ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ weight.to_dict() for weight in weights ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ RecencyWeight ]:
      rows = json.loads( cls.path().read_text() )
      return [ RecencyWeight.from_row( row ) for row in rows ]
