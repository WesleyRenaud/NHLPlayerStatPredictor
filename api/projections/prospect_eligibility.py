from __future__ import annotations

from .prospect_profile import ProspectProfile


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
