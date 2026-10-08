from __future__ import annotations

import json
from pathlib import Path

from .league_arrival import LeagueArrival
from ..paths import Paths


class LeagueArrivalStore():
   FILE_NAME = 'league_arrivals.json'


   @classmethod
   def path( cls ) -> Path:
      return Paths.PROCESSED_DIR / cls.FILE_NAME


   @classmethod
   def write( cls, arrivals: list[ LeagueArrival ] ) -> None:
      path = cls.path()
      path.parent.mkdir( parents=True, exist_ok=True )
      path.write_text( json.dumps( [ arrival.to_dict() for arrival in arrivals ], indent=2 ) )


   @classmethod
   def read( cls ) -> list[ LeagueArrival ]:
      path = cls.path()

      if not path.exists():
         return []

      return [ LeagueArrival.from_row( row ) for row in json.loads( path.read_text() ) ]
