from __future__ import annotations

from .production_coefficient_fitter import ProductionCoefficientFitter
from .production_level_trust import ProductionLevelTrust
from .production_level_trust_total import ProductionLevelTrustTotal
from .production_trajectory_change import ProductionTrajectoryChange
from .production_trajectory_share import ProductionTrajectoryShare


class ProductionLevelTrustFitter():
   @classmethod
   def fit(
         cls,
         shares: list[ ProductionTrajectoryShare ],
         changes: list[ ProductionTrajectoryChange ],
         move: float ) -> list[ ProductionTrajectoryShare ]:
      """Fraction of a one-year dip off a level that was gone the next season.

      Neighboring ages share weight. The width is the one that best predicts
      a dip left out of the fit.
      """
      by_age = { share.age: share for share in shares }

      for trust in cls._trusts( changes, move ):
         current = by_age.get( trust.age )
         by_age[ trust.age ] = ProductionTrajectoryShare(
            trust.age,
            None if current is None else current.rise_share,
            None if current is None else current.drop_share,
            trust.trust )

      return [ by_age[ age ] for age in sorted( by_age ) ]


   @classmethod
   def _trusts(
         cls,
         changes: list[ ProductionTrajectoryChange ],
         move: float ) -> list[ ProductionLevelTrust ]:
      dips = [ change for change in changes if change.is_one_year_dip( move ) ]

      if len( dips ) < ProductionCoefficientFitter.MIN_SUPPORT:
         return []

      bandwidth = cls._bandwidth( dips )
      first = min( change.age for change in dips )
      last = max( change.age for change in dips )
      trusts: list[ ProductionLevelTrust ] = []

      for age in range( first, last + 1 ):
         if cls._nearby( dips, age, bandwidth ) < ProductionCoefficientFitter.MIN_SUPPORT:
            continue

         kept = cls._kernel_share( dips, age, bandwidth )

         if kept is None:
            continue

         trusts.append( ProductionLevelTrust.given_back( age, kept ) )

      return trusts


   @classmethod
   def _bandwidth( cls, dips: list[ ProductionTrajectoryChange ] ) -> int:
      span = max( change.age for change in dips ) - min( change.age for change in dips )
      best = 1
      best_error: float | None = None

      for bandwidth in range( 1, span + 2 ):
         error, weight = cls._bandwidth_error( dips, bandwidth )

         if weight <= 0.0:
            continue

         score = error / weight

         if best_error is None or score < best_error:
            best_error = score
            best = bandwidth

      return best


   @classmethod
   def _bandwidth_error(
         cls,
         dips: list[ ProductionTrajectoryChange ],
         bandwidth: int ) -> tuple[ float, float ]:
      totals = cls._totals( dips )
      error = 0.0
      weight = 0.0

      for change in dips:
         held_out = [
            total.excluding( change ) if total.age == change.age else total
            for total in totals
         ]
         kept = cls._kernel_share_from( held_out, change.age, bandwidth )
         pace_change = change.pace_change()

         if kept is None or pace_change == 0.0:
            continue

         observed = change.still_present() / pace_change
         error += change.games * ( kept - observed ) ** 2
         weight += change.games

      return error, weight


   @classmethod
   def _totals(
         cls,
         dips: list[ ProductionTrajectoryChange ] ) -> list[ ProductionLevelTrustTotal ]:
      totals: list[ ProductionLevelTrustTotal ] = []

      for change in dips:
         updated = cls._at( totals, change.age ).including( change )

         if any( total.age == change.age for total in totals ):
            totals = [
               updated if total.age == change.age else total
               for total in totals
            ]
         else:
            totals.append( updated )

      return totals


   @classmethod
   def _at(
         cls,
         totals: list[ ProductionLevelTrustTotal ],
         age: int ) -> ProductionLevelTrustTotal:
      for total in totals:
         if total.age == age:
            return total

      return ProductionLevelTrustTotal.empty( age )


   @classmethod
   def _kernel_share(
         cls,
         dips: list[ ProductionTrajectoryChange ],
         age: int,
         bandwidth: int ) -> float | None:
      return cls._kernel_share_from( cls._totals( dips ), age, bandwidth )


   @classmethod
   def _kernel_share_from(
         cls,
         totals: list[ ProductionLevelTrustTotal ],
         age: int,
         bandwidth: int ) -> float | None:
      if bandwidth <= 0:
         return None

      numerator = 0.0
      denominator = 0.0

      for total in totals:
         weight = 1.0 - abs( total.age - age ) / bandwidth

         if weight <= 0.0 or total.games <= 0.0:
            continue

         numerator += weight * total.still_present
         denominator += weight * total.pace_change

      if denominator == 0.0:
         return None

      return numerator / denominator


   @classmethod
   def _nearby(
         cls,
         dips: list[ ProductionTrajectoryChange ],
         age: int,
         bandwidth: int ) -> int:
      return sum( abs( change.age - age ) < bandwidth for change in dips )
