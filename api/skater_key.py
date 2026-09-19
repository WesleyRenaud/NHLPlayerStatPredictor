from __future__ import annotations

from dataclasses import dataclass

from .skater_season import SkaterSeason


@dataclass( frozen=True )
class SkaterKey():
   player_id: int
   player_name: str


   @classmethod
   def from_row( cls, row: SkaterSeason ) -> SkaterKey:
      return cls( row.player_id, row.player_name )
