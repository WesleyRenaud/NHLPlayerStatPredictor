from __future__ import annotations

from .other_league_season_builder import OtherLeagueSeasonBuilder
from .other_league_skater_season import OtherLeagueSkaterSeason
from .season_length import SeasonLength
from .types import Types


class OtherLeagueSeasonIngester():
   @classmethod
   def build_rows(
         cls,
         player_ids: list[ int ],
         landings: dict[ int, Types.JsonObject ],
         seasons: list[ SeasonLength ],
         pace_games: int ) -> list[ OtherLeagueSkaterSeason ]:
      rows: list[ OtherLeagueSkaterSeason ] = []

      for player_id in player_ids:
         if player_id not in landings:
            continue

         rows.extend(
            OtherLeagueSeasonBuilder.build(
               landings[ player_id ],
               seasons,
               pace_games ) )

      return rows
