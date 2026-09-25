from __future__ import annotations

from dataclasses import replace

from .games_share import GamesShare
from .nhl_skater_season import NhlSkaterSeason
from .other_league_skater_season import OtherLeagueSkaterSeason
from .skater_season_key import SkaterSeasonKey


class MixedSeasonShareBinder():
   @classmethod
   def bind(
         cls,
         nhl: list[ NhlSkaterSeason ],
         other: list[ OtherLeagueSkaterSeason ] ) -> list[ NhlSkaterSeason ]:
      mixed = {
         SkaterSeasonKey( season.player_id, season.season_id )
         for season in other
         if season.games_played
      }
      return [
         replace( season, gp_share=GamesShare.FULL )
         if season.key() in mixed else season
         for season in nhl
      ]
