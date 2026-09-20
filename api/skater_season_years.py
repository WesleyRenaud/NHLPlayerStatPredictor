from __future__ import annotations

from .season import Season
from .skater_season import SkaterSeason


class SkaterSeasonYears():
   @classmethod
   def by_player(
         cls,
         seasons: list[ SkaterSeason ] ) -> dict[ int, dict[ int, SkaterSeason ] ]:
      by_player: dict[ int, dict[ int, SkaterSeason ] ] = {}

      for season in seasons:
         years = by_player.setdefault( season.player_id, {} )
         years[ Season.start_year( season.season_id ) ] = season

      return by_player


   @classmethod
   def consecutive(
         cls,
         seasons: list[ SkaterSeason ] ) -> list[ tuple[ SkaterSeason, SkaterSeason ] ]:
      pairs: list[ tuple[ SkaterSeason, SkaterSeason ] ] = []

      for years in cls.by_player( seasons ).values():
         for year, current in sorted( years.items() ):
            following = years.get( year + 1 )

            if following is None:
               continue

            pairs.append( ( current, following ) )

      return pairs
