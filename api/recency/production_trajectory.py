from __future__ import annotations

from .prior_year import PriorYear
from .production_season import ProductionSeason
from .production_trajectory_fit import ProductionTrajectoryFit
from .production_trajectory_share import ProductionTrajectoryShare
from ..shared.enums.position import Position


class ProductionTrajectory():
   @classmethod
   def shares(
         cls,
         history: list[ ProductionSeason ],
         bases: list[ float ],
         fit: ProductionTrajectoryFit,
         curve: list[ ProductionSeason ] | None = None ) -> list[ float ]:
      latest_share = cls._latest_share( history, bases, fit, curve )

      if latest_share is None:
         return bases

      return cls._allocate( bases, latest_share )


   @classmethod
   def _latest_share(
         cls,
         history: list[ ProductionSeason ],
         bases: list[ float ],
         fit: ProductionTrajectoryFit,
         curve: list[ ProductionSeason ] | None ) -> float | None:
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

      retained = cls._retained( fit, latest.age, move > 0.0 )

      if retained is None:
         return None

      raw = bases[ Position.FIRST ] / total
      target = cls._target( raw, retained )
      is_drop = move < 0.0
      extra_on_latest = target > raw

      if is_drop and extra_on_latest:
         level_curve = curve if curve is not None else history
         given_back = cls._level_pull( level_curve, fit )
         remaining = 1.0 - given_back
         target = target * remaining

      if target == raw:
         return None

      return target


   @classmethod
   def _level_pull( cls, curve: list[ ProductionSeason ], fit: ProductionTrajectoryFit ) -> float:
      if fit.move <= 0.0 or not cls._has_season_before_the_drop( curve ):
         return 0.0

      latest = curve[ Position.FIRST ]
      trust = cls._level_trust( fit, latest.age )

      if trust <= 0.0:
         return 0.0

      prior = curve[ Position.SECOND ]
      peak = max( latest.pace, prior.pace )

      if peak <= 0.0 or latest.pace >= prior.pace:
         return 0.0

      if ( prior.pace - latest.pace ) / peak < fit.move:
         return 0.0

      return trust * cls._curve_flatness( curve, fit.move )


   @classmethod
   def _has_season_before_the_drop( cls, curve: list[ ProductionSeason ] ) -> bool:
      seasons_in_the_level = ( Position.FIRST, Position.SECOND, Position.THIRD )
      return len( curve ) >= len( seasons_in_the_level )


   @classmethod
   def _curve_flatness( cls, curve: list[ ProductionSeason ], move_threshold: float ) -> float:
      widest = 0.0
      seasons_before_the_drop = curve[ Position.SECOND : ]
      one_season_older = curve[ Position.THIRD : ]

      for newer, older in zip( seasons_before_the_drop, one_season_older ):
         peak = max( newer.pace, older.pace )

         if peak <= 0.0:
            return 0.0

         widest = max( widest, abs( newer.pace - older.pace ) / peak )

      return max( 0.0, 1.0 - widest / move_threshold )


   @classmethod
   def _allocate( cls, bases: list[ float ], latest_share: float ) -> list[ float ]:
      total = sum( bases )
      older = total - bases[ Position.FIRST ]

      if older <= 0.0:
         return bases

      rest = total - latest_share * total
      return [ latest_share * total ] + [ rest * base / older for base in bases[ 1 : ] ]


   @classmethod
   def _retained( cls, fit: ProductionTrajectoryFit, age: int, rising: bool ) -> float | None:
      usable = [
         share for share in fit.by_age
         if ( share.rise_share if rising else share.drop_share ) is not None
      ]

      if not usable:
         return None

      nearest = min( usable, key=lambda share: abs( share.age - age ) )
      return nearest.rise_share if rising else nearest.drop_share


   @classmethod
   def _level_trust( cls, fit: ProductionTrajectoryFit, age: int ) -> float:
      fitted = sorted(
         ( share for share in fit.by_age if share.level_trust is not None ),
         key=lambda share: share.age )

      if not fitted:
         return 0.0

      youngest = fitted[ 0 ]
      oldest = fitted[ -1 ]

      if age <= youngest.age:
         return cls._recorded_trust( youngest )

      if age >= oldest.age:
         return cls._recorded_trust( oldest )

      return cls._trust_between( fitted, age )


   @classmethod
   def _trust_between(
         cls,
         fitted: list[ ProductionTrajectoryShare ],
         age: int ) -> float:
      next_older_age = fitted[ 1 : ]

      for younger, older in zip( fitted, next_older_age ):
         if younger.age <= age <= older.age:
            span = older.age - younger.age
            younger_trust = cls._recorded_trust( younger )
            older_trust = cls._recorded_trust( older )
            return younger_trust + ( older_trust - younger_trust ) * ( age - younger.age ) / span

      return 0.0


   @classmethod
   def _recorded_trust( cls, share: ProductionTrajectoryShare ) -> float:
      if share.level_trust is None:
         return 0.0

      return share.level_trust


   @classmethod
   def _target( cls, raw: float, retained: float ) -> float:
      # Mostly kept next season: do not put less than that on the latest season.
      # Mostly given back: do not put more than that on it.
      if retained >= 0.5:
         return max( raw, retained )

      return min( raw, retained )
