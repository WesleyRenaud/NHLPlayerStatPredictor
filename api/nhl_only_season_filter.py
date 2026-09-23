from __future__ import annotations

from .nhl_skater_season import NhlSkaterSeason
from .other_league_skater_season import OtherLeagueSkaterSeason
from .skater_season_key import SkaterSeasonKey


class NhlOnlySeasonFilter():
   @classmethod
   def keep(
         cls,
         nhl: list[ NhlSkaterSeason ],
         other: list[ OtherLeagueSkaterSeason ] ) -> list[ NhlSkaterSeason ]:
      other_years = cls._other_years( other )
      return [
         season for season in nhl
         if season.key() not in other_years
      ]


   @classmethod
   def _other_years(
         cls,
         other: list[ OtherLeagueSkaterSeason ] ) -> set[ SkaterSeasonKey ]:
      return {
         SkaterSeasonKey( season.player_id, season.season_id )
         for season in other
         if season.games_played
      }
