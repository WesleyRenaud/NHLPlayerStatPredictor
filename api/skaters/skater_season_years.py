from __future__ import annotations

from .nhl_skater_season import NhlSkaterSeason
from ..season import Season


class SkaterSeasonYears():
   @classmethod
   def by_player(
         cls,
         seasons: list[ NhlSkaterSeason ] ) -> dict[ int, list[ NhlSkaterSeason ] ]:
      by_player: dict[ int, list[ NhlSkaterSeason ] ] = {}

      for season in seasons:
         by_player.setdefault( season.player_id, [] ).append( season )

      return by_player


   @classmethod
   def at_year(
         cls,
         seasons: list[ NhlSkaterSeason ],
         year: int ) -> NhlSkaterSeason | None:
      for season in seasons:
         if Season.start_year( season.season_id ) == year:
            return season

      return None


   @classmethod
   def consecutive(
         cls,
         seasons: list[ NhlSkaterSeason ] ) -> list[ tuple[ NhlSkaterSeason, NhlSkaterSeason ] ]:
      pairs: list[ tuple[ NhlSkaterSeason, NhlSkaterSeason ] ] = []

      for player_seasons in cls.by_player( seasons ).values():
         for current in player_seasons:
            following = cls.at_year(
               player_seasons,
               Season.start_year( current.season_id ) + 1 )

            if following is None:
               continue

            pairs.append( ( current, following ) )

      return pairs
