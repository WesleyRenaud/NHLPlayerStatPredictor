from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class DressedLineup():
   ice: list[ float ]


   @property
   def implied( self ) -> float:
      return sum( self.ice )
