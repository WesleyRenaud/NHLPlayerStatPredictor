from __future__ import annotations

from .club_ice import ClubIce
from ..skaters.team import Team


class IceClaim():
   @classmethod
   def resolve(
         cls,
         clubs: list[ ClubIce ],
         rates: dict[ Team, float ] ) -> float:
      weighted = 0.0
      games = 0

      for club in clubs:
         weighted += club.toi * rates.get( club.team, 1.0 ) * club.games
         games += club.games

      return weighted / games
