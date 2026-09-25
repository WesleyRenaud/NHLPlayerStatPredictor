from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, replace

from .skater import Skater
from .skater_position import SkaterPosition
from .skater_season import SkaterSeason
from .team import Team
from ..types import Types


@dataclass( frozen=True )
class RosterSkater():
   player_id: int
   player_name: str
   position: SkaterPosition
   team: Team
   last_played_season_id: int | None = field( default=None, kw_only=True )


   @classmethod
   def from_row( cls, row: Types.JsonObject | Types.Row ) -> RosterSkater:
      return cls(
         player_id=int( row[ 'PLAYER_ID' ] ),
         player_name=str( row[ 'PLAYER_NAME' ] ),
         position=SkaterPosition( str( row[ 'POSITION' ] ) ),
         team=Team( str( row[ 'TEAM' ] ) ) )


   @classmethod
   def with_last_played(
         cls,
         roster: list[ RosterSkater ],
         seasons: list[ SkaterSeason ] ) -> list[ RosterSkater ]:
      by_id: dict[ int, list[ SkaterSeason ] ] = defaultdict( list )

      for season in seasons:
         by_id[ season.player_id ].append( season )

      return [
         replace(
            row,
            last_played_season_id=Skater( by_id[ row.player_id ] ).last_played_season_id() )
         for row in roster
      ]
