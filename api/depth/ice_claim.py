from __future__ import annotations

from ..skaters.team import Team


class IceClaim():
   @classmethod
   def resolve(
         cls,
         toi: float,
         team: Team,
         rates: dict[ Team, float ] ) -> float:
      return toi * rates.get( team, 1.0 )
