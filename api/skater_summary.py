from __future__ import annotations

from dataclasses import dataclass

from .skater_position import SkaterPosition
from .team import Team
from .types import Types


@dataclass( frozen=True )
class SkaterSummary():
   player_id: int
   player_name: str
   position: SkaterPosition
   team_abbrevs: list[ Team ]
   games_played: int
   goals: int
   assists: int
   points: int


   @classmethod
   def from_rows( cls, rows: Types.JsonObjectList ) -> list[ SkaterSummary ]:
      return [ cls.from_row( raw ) for raw in rows ]


   @classmethod
   def from_row( cls, raw: Types.JsonObject ) -> SkaterSummary:
      return cls(
         int( raw[ 'playerId' ] ),
         str( raw[ 'skaterFullName' ] ),
         SkaterPosition( str( raw[ 'positionCode' ] ) ),
         [ Team( part ) for part in str( raw[ 'teamAbbrevs' ] ).split( ',' ) ],
         int( raw[ 'gamesPlayed' ] ),
         int( raw[ 'goals' ] ),
         int( raw[ 'assists' ] ),
         int( raw[ 'points' ] ) )
