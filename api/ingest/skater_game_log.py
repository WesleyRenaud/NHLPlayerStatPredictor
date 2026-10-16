from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..iso_date import IsoDate
from ..types import Types


@dataclass( frozen=True )
class SkaterGameLog():
   player_id: int
   played_on: date
   points: int


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> SkaterGameLog | None:
      player_id = row.get( 'playerId' )
      played_on = row.get( 'gameDate' )
      points = row.get( 'points' )

      if player_id is None or played_on is None or points is None:
         return None

      return cls(
         int( player_id ),
         IsoDate.parse( str( played_on ) ),
         int( points ) )


   @classmethod
   def in_played_order( cls, logs: list[ SkaterGameLog ] ) -> list[ SkaterGameLog ]:
      first_on_date: dict[ date, SkaterGameLog ] = {}

      for log in logs:
         first_on_date.setdefault( log.played_on, log )

      return [ first_on_date[ played_on ] for played_on in sorted( first_on_date ) ]
