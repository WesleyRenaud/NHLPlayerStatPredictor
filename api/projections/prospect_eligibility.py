from __future__ import annotations

from .prospect_profile import ProspectProfile
from ..recency.prior_year import PriorYear


class ProspectEligibility():
   MAX_AGE = 25
   MAX_NHL_GAMES = 25


   @classmethod
   def eligible(
         cls, profile: ProspectProfile, target_season_id: int,
         age: float ) -> bool:
      return (
         age <= cls.MAX_AGE
         and profile.prior_games( target_season_id ) <= cls.MAX_NHL_GAMES )


   @classmethod
   def pre_nhl( cls, age: float, nhl_games: int, prior_nhl_games: int ) -> bool:
      return (
         nhl_games == 0
         and int( age ) <= cls.MAX_AGE
         and prior_nhl_games <= cls.MAX_NHL_GAMES )


   @classmethod
   def short_nhl(
         cls, age: float, nhl_games: int, other_games: int, prior_nhl_games: int ) -> bool:
      return (
         0 < nhl_games < PriorYear.MIN_GAMES
         and other_games >= PriorYear.MIN_GAMES
         and int( age ) <= cls.MAX_AGE
         and prior_nhl_games <= cls.MAX_NHL_GAMES )


   @classmethod
   def rookie_nhl( cls, age: float, nhl_games: int, prior_nhl_games: int ) -> bool:
      return (
         nhl_games >= PriorYear.MIN_GAMES
         and int( age ) <= cls.MAX_AGE
         and prior_nhl_games <= cls.MAX_NHL_GAMES )
