from __future__ import annotations

from ..ingest.club_ice_parser import ClubIceParser
from ..skaters.skater_stat_rates import SkaterStatRates
from ..types import Types
from .usable_nhl_ice import UsableNhlIce


class UsableNhlIceResolver():
   @classmethod
   def resolve( cls, landing: Types.JsonObject ) -> UsableNhlIce | None:
      for season_id in ClubIceParser.season_ids( landing ):
         clubs = ClubIceParser.parse( landing, season_id )
         games = sum( club.games for club in clubs )

         if games < UsableNhlIce.MIN_GAMES:
            continue

         return UsableNhlIce(
            season_id,
            SkaterStatRates.time_on_ice_per_game( sum( club.toi * club.games for club in clubs ), games ),
            clubs )

      return None
