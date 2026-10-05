from __future__ import annotations

from .prior_year import PriorYear
from .production_season import ProductionSeason
from .production_trajectory_fit import ProductionTrajectoryFit
from ..shared.enums.position import Position


class ProductionTrajectory():
   @classmethod
   def shares(
         cls,
         history: list[ ProductionSeason ],
         bases: list[ float ],
         fit: ProductionTrajectoryFit ) -> list[ float ]:
      latest_share = cls._latest_share( history, bases, fit )

      if latest_share is None:
         return bases

      return cls._allocate( bases, latest_share )


   @classmethod
   def _latest_share(
         cls,
         history: list[ ProductionSeason ],
         bases: list[ float ],
         fit: ProductionTrajectoryFit ) -> float | None:
      total = sum( bases )

      if not fit.by_age or len( history ) < 2 or total <= 0.0:
         return None

      latest = history[ Position.FIRST ]
      prior = history[ Position.SECOND ]

      if min( latest.games, prior.games ) < PriorYear.MIN_GAMES:
         return None

      peak = max( latest.pace, prior.pace )
      move = latest.pace - prior.pace

      if peak == 0.0 or abs( move ) / peak < fit.move:
         return None

      retained = fit.retained( latest.age, move > 0.0 )

      if retained is None:
         return None

      raw = bases[ Position.FIRST ] / total
      target = cls._target( raw, retained )

      if target == raw:
         return None

      return target


   @classmethod
   def _allocate( cls, bases: list[ float ], latest_share: float ) -> list[ float ]:
      total = sum( bases )
      older = total - bases[ Position.FIRST ]

      if older <= 0.0:
         return bases

      rest = total - latest_share * total
      return [ latest_share * total ] + [ rest * base / older for base in bases[ 1 : ] ]


   @classmethod
   def _target( cls, raw: float, retained: float ) -> float:
      # Mostly kept next season: do not put less than that on the latest season.
      # Mostly given back: do not put more than that on it.
      if retained >= 0.5:
         return max( raw, retained )

      return min( raw, retained )
