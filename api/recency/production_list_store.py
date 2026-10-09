from __future__ import annotations

import json
from pathlib import Path

from ..paths import Paths
from ..types import Types


class ProductionListStore():
   FILE_NAME: str
   FOLDER: str


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FOLDER / cls.FILE_NAME


   @classmethod
   def read_rows( cls ) -> Types.JsonObjectList:
      return json.loads( cls.path().read_text() )


   @classmethod
   def write_rows( cls, rows: Types.JsonObjectList ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text( json.dumps( rows, indent=2 ) )
