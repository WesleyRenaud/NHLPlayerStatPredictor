from __future__ import annotations


class GamesShare():
   FULL = 1.0


   @classmethod
   def resolve( cls, games: int, season_length: int ) -> float:
      return games / season_length
