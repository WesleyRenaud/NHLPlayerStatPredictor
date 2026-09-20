from __future__ import annotations

from .nhl_skater_season import NhlSkaterSeason
from .season import Season


class SkaterSeasonYears():
   @classmethod
   def by_player(
         cls,
         seasons: list[ NhlSkaterSeason ] ) -> dict[ int, dict[ int, NhlSkaterSeason ] ]:
      by_player: dict[ int, dict[ int, NhlSkaterSeason ] ] = {}

      for season in seasons:
         years = by_player.setdefault( season.player_id, {} )
         years[ Season.start_year( season.season_id ) ] = season

      return by_player


   @classmethod
   def consecutive(
         cls,
         seasons: list[ NhlSkaterSeason ] ) -> list[ tuple[ NhlSkaterSeason, NhlSkaterSeason ] ]:
      pairs: list[ tuple[ NhlSkaterSeason, NhlSkaterSeason ] ] = []

      for years in cls.by_player( seasons ).values():
         for year, current in sorted( years.items() ):
            following = years.get( year + 1 )

            if following is None:
               continue

            pairs.append( ( current, following ) )

      return pairs
