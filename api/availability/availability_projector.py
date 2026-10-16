from __future__ import annotations

from .games_share import GamesShare
from ..season import Season
from ..skaters.nhl_skater_season import NhlSkaterSeason


class AvailabilityProjector():
   @classmethod
   def resolve(
         cls,
         player_seasons: list[ NhlSkaterSeason ],
         projection_season_id: int ) -> float:
      latest = cls._latest( player_seasons, projection_season_id )

      if latest is None or latest.gp_share is None:
         return GamesShare.FULL

      return latest.gp_share


   @classmethod
   def _latest(
         cls,
         player_seasons: list[ NhlSkaterSeason ],
         projection_season_id: int ) -> NhlSkaterSeason | None:
      season_before_projection = Season.season_before( projection_season_id )
      most_recent: NhlSkaterSeason | None = None

      for player_season in player_seasons:
         if player_season.gp_share is None:
            continue

         if player_season.season_id == season_before_projection:
            return player_season

         if most_recent is None or player_season.season_id > most_recent.season_id:
            most_recent = player_season

      return most_recent
