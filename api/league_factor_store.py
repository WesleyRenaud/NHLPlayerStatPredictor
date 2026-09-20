from __future__ import annotations

import json
from pathlib import Path

from .league_factor import LeagueFactor
from .paths import Paths


class LeagueFactorStore():
   FILE_NAME = 'league_factors.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, factors: list[ LeagueFactor ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ factor.to_dict() for factor in factors ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ LeagueFactor ]:
      rows = json.loads( cls.path().read_text() )
      return [ LeagueFactor.from_row( row ) for row in rows ]
