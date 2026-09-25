from __future__ import annotations

from .club_ice import ClubIce
from ..ingest.club_ice_parser import ClubIceParser
from ..types import Types
from .usable_nhl_ice import UsableNhlIce


class UsableNhlIceResolver():
   MIN_GAMES = 8


   @classmethod
   def resolve( cls, landing: Types.JsonObject ) -> UsableNhlIce | None:
      for season_id in ClubIceParser.season_ids( landing ):
         clubs = ClubIceParser.parse( landing, season_id )
         games = sum( club.games for club in clubs )

         if games < cls.MIN_GAMES:
            continue

         return UsableNhlIce(
            season_id,
            cls._toi( clubs, games ),
            clubs )

      return None


   @classmethod
   def _toi( cls, clubs: list[ ClubIce ], games: int ) -> float:
      return sum( club.toi * club.games for club in clubs ) / games
