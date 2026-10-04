from __future__ import annotations

from .club_ice import ClubIce


class IceClaim():
   @classmethod
   def resolve(
         cls,
         clubs: list[ ClubIce ] ) -> float:
      weighted = 0.0
      games = 0

      for club in clubs:
         weighted += club.toi * club.games
         games += club.games

      return weighted / games
