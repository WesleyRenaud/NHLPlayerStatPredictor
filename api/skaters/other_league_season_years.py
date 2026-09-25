from __future__ import annotations

from .other_league_skater_season import OtherLeagueSkaterSeason
from ..season import Season


class OtherLeagueSeasonYears():
   @classmethod
   def by_player_league(
         cls,
         seasons: list[ OtherLeagueSkaterSeason ] ) -> dict[
            int,
            dict[ str, dict[ int, OtherLeagueSkaterSeason ] ] ]:
      by_player: dict[ int, dict[ str, dict[ int, OtherLeagueSkaterSeason ] ] ] = {}

      for season in seasons:
         leagues = by_player.setdefault( season.player_id, {} )
         years = leagues.setdefault( season.league, {} )
         years[ Season.start_year( season.season_id ) ] = season

      return by_player


   @classmethod
   def consecutive(
         cls,
         seasons: list[ OtherLeagueSkaterSeason ] ) -> list[
            tuple[ OtherLeagueSkaterSeason, OtherLeagueSkaterSeason ] ]:
      pairs: list[ tuple[ OtherLeagueSkaterSeason, OtherLeagueSkaterSeason ] ] = []

      for leagues in cls.by_player_league( seasons ).values():
         for years in leagues.values():
            for year, current in sorted( years.items() ):
               following = years.get( year + 1 )

               if following is None:
                  continue

               pairs.append( ( current, following ) )

      return pairs
