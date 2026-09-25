from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class DressedPoints():
   points: list[ float ]


   @property
   def total( self ) -> float:
      return sum( self.points )
