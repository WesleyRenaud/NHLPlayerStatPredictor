from __future__ import annotations

import json
from pathlib import Path

from .paths import Paths
from .slot_average import SlotAverage


class SlotAverageStore():
   FILE_NAME = 'slot_averages.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, slots: list[ SlotAverage ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ slot.to_dict() for slot in slots ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ SlotAverage ]:
      if not cls.path().exists():
         return []

      rows = json.loads( cls.path().read_text() )
      return [ SlotAverage.from_row( row ) for row in rows ]
