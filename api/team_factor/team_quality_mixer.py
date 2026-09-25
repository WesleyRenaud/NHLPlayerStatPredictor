from __future__ import annotations

from .club_games import ClubGames
from .team_factor import TeamFactor


class TeamQualityMixer():
   @classmethod
   def resolve(
         cls,
         factors: list[ TeamFactor ],
         season: int,
         player_id: int,
         clubs: list[ ClubGames ] ) -> float:
      weighted = 0.0
      games = 0

      for club in clubs:
         weighted += TeamFactor.teammate_rate(
            factors,
            season,
            club.team,
            player_id ) * club.games
         games += club.games

      return weighted / games
