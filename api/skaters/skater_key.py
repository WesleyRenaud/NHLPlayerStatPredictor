from __future__ import annotations

from dataclasses import dataclass

from .nhl_skater_season import NhlSkaterSeason


@dataclass( frozen=True )
class SkaterKey():
   player_id: int
   player_name: str


   @classmethod
   def from_row( cls, row: NhlSkaterSeason ) -> SkaterKey:
      return cls( row.player_id, row.player_name )
