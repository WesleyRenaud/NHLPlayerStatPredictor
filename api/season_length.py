from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .shared.enums.position import Position
from .types import Types


@dataclass( frozen=True, order=True )
class SeasonLength():
   season_id: int
   number_of_games: int
   start_date: date
   regular_season_end_date: date


   @classmethod
   def from_rows( cls, rows: Types.JsonObjectList ) -> list[ SeasonLength ]:
      return [ cls.from_row( raw ) for raw in rows ]


   @classmethod
   def from_row( cls, raw: Types.JsonObject ) -> SeasonLength:
      return cls(
         int( raw[ 'id' ] ),
         int( raw[ 'numberOfGames' ] ),
         date.fromisoformat(
            str( raw[ 'startDate' ] ).split( 'T' )[ Position.FIRST ] ),
         date.fromisoformat(
            str( raw[ 'regularSeasonEndDate' ] ).split( 'T' )[ Position.FIRST ] ) )
