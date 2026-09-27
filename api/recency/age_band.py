from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class AgeBand():
   first_age: int
   last_age: int


   def contains( self, age: int ) -> bool:
      return self.first_age <= age <= self.last_age
