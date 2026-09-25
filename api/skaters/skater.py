from __future__ import annotations

from dataclasses import dataclass

from .nhl_skater_season import NhlSkaterSeason
from .skater_season import SkaterSeason


@dataclass( frozen=True )
class Skater():
   seasons: list[ SkaterSeason ]


   def nhl_seasons( self ) -> list[ NhlSkaterSeason ]:
      return [
         season
         for season in self.seasons
         if isinstance( season, NhlSkaterSeason )
      ]
