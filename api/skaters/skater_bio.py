from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..shared.enums.position import Position
from ..types import Types


@dataclass( frozen=True )
class SkaterBio():
   player_id: int
   birth_date: date


   @classmethod
   def from_rows( cls, rows: Types.JsonObjectList ) -> list[ SkaterBio ]:
      return [ cls.from_row( raw ) for raw in rows ]


   @classmethod
   def from_row( cls, raw: Types.JsonObject ) -> SkaterBio:
      return cls(
         int( raw[ 'playerId' ] ),
         date.fromisoformat(
            str( raw[ 'birthDate' ] ).split( 'T' )[ Position.FIRST ] ) )
