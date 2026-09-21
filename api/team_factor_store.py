from __future__ import annotations

import json
from pathlib import Path

from .paths import Paths
from .team_factor import TeamFactor


class TeamFactorStore():
   FILE_NAME = 'team_factors.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, factors: list[ TeamFactor ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text(
         json.dumps( [ factor.to_dict() for factor in factors ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ TeamFactor ]:
      rows = json.loads( cls.path().read_text() )
      return [ TeamFactor.from_row( row ) for row in rows ]
