from __future__ import annotations

import json
from pathlib import Path

from .paths import Paths
from .skater_ice import SkaterIce


class SkaterIceStore():
   FILE_NAME = 'skater_ice.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, rows: list[ SkaterIce ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ row.to_dict() for row in rows ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ SkaterIce ]:
      if not cls.path().exists():
         return []

      return [
         SkaterIce.from_row( row )
         for row in json.loads( cls.path().read_text() )
      ]


   @classmethod
   def by_player( cls ) -> dict[ int, SkaterIce ]:
      return { row.player_id: row for row in cls.read() }
