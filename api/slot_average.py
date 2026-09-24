from __future__ import annotations

from dataclasses import dataclass

from .types import Types


@dataclass( frozen=True )
class SlotAverage():
   slot: int
   toi: float
   goals: float
   assists: float


   @property
   def contribution( self ) -> float:
      return self.goals + self.assists


   @classmethod
   def from_row( cls, row: Types.JsonObject ) -> SlotAverage:
      return cls(
         slot=int( row[ 'slot' ] ),
         toi=float( row[ 'toi' ] ),
         goals=float( row[ 'goals' ] ),
         assists=float( row[ 'assists' ] ) )


   def to_dict( self ) -> Types.JsonObject:
      return {
         'slot': self.slot,
         'toi': round( self.toi, 2 ),
         'goals': round( self.goals, 2 ),
         'assists': round( self.assists, 2 ),
         'points': round( self.contribution, 2 ),
      }
