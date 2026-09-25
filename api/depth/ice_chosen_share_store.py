from __future__ import annotations

import json
from pathlib import Path

from .ice_chosen_share import IceChosenShare
from ..paths import Paths


class IceChosenShareStore():
   FILE_NAME = 'ice_chosen_shares.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, shares: list[ IceChosenShare ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ share.to_dict() for share in shares ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ IceChosenShare ]:
      if not cls.path().exists():
         return []

      rows = json.loads( cls.path().read_text() )
      return [ IceChosenShare.from_row( row ) for row in rows ]
