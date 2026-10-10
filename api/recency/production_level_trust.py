from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class ProductionLevelTrust():
   age: int
   trust: float


   @classmethod
   def given_back( cls, age: int, kept: float ) -> ProductionLevelTrust:
      returned = 1.0 - kept

      if returned < 0.0:
         returned = 0.0

      if returned > 1.0:
         returned = 1.0

      return cls( age, returned )
