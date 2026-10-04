from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True, init=False )
class DraftPick():
   value: int | None


   def __init__( self, value: int | None ) -> None:
      if value is not None and (
            isinstance( value, bool ) or not isinstance( value, int )
            or value < 1 ):
         raise ValueError( 'Draft pick must be a positive integer or None for undrafted.' )
      object.__setattr__( self, 'value', value )
