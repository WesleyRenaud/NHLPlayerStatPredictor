from __future__ import annotations

from dataclasses import dataclass

from .skater_group import SkaterGroup
from .types import Types


@dataclass( frozen=True )
class TeamFactorSkater():
   player_id: int
   contribution: float
   skater_group: SkaterGroup
   availability: float
   extra: bool
   prior_availability: float | None


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> TeamFactorSkater:
      return cls(
         player_id=int( row[ 'player_id' ] ),
         contribution=float( row[ 'contribution' ] ),
         skater_group=SkaterGroup( str( row[ 'skater_group' ] ) ),
         availability=float( row[ 'availability' ] ),
         extra=bool( row[ 'extra' ] ),
         prior_availability=float( row[ 'prior_availability' ] )
            if row.get( 'prior_availability' ) is not None else None )


   def to_dict( self ) -> dict[ str, int | float | bool | str | None ]:
      return {
         'player_id': self.player_id,
         'contribution': self.contribution,
         'skater_group': self.skater_group.value,
         'availability': self.availability,
         'extra': self.extra,
         'prior_availability': self.prior_availability,
      }
