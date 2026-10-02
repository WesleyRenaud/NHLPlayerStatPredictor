from __future__ import annotations

from math import sqrt

from .production_coefficient import ProductionCoefficient
from .production_pair import ProductionPair


class ProductionCoefficientFitter():
   MIN_SUPPORT = 20


   @classmethod
   def fit(
         cls,
         pairs: list[ ProductionPair ] ) -> list[ ProductionCoefficient ]:
      coefficients: list[ ProductionCoefficient ] = []

      for from_age, to_age in sorted( { ( pair.from_age, pair.to_age ) for pair in pairs } ):
         lag = to_age - from_age
         same_lag = [ pair for pair in pairs if pair.to_age - pair.from_age == lag ]
         selected = [ pair for pair in same_lag if pair.from_age == from_age ]

         if cls._support( selected ) < ProductionCoefficientFitter.MIN_SUPPORT:
            selected = [ pair for pair in same_lag if abs( pair.from_age - from_age ) <= 1 ]

         if cls._support( selected ) < ProductionCoefficientFitter.MIN_SUPPORT:
            selected = same_lag

         coefficients.append( cls._coefficient( from_age, to_age, selected ) )

      return coefficients


   @classmethod
   def _support( cls, pairs: list[ ProductionPair ] ) -> int:
      return sum( pair.prior_pace > 0.0 for pair in pairs )


   @classmethod
   def _coefficient(
         cls,
         from_age: int,
         to_age: int,
         pairs: list[ ProductionPair ] ) -> ProductionCoefficient:
      support = cls._support( pairs )

      if support < ProductionCoefficientFitter.MIN_SUPPORT:
         return ProductionCoefficient( from_age, to_age, 1.0, 0.0, len( pairs ) )

      games = sum( pair.games for pair in pairs )
      prior_mean = sum( pair.prior_pace * pair.games for pair in pairs ) / games
      next_mean = sum( pair.following_pace * pair.games for pair in pairs ) / games
      prior_variance = sum( pair.games * ( pair.prior_pace - prior_mean ) ** 2 for pair in pairs )
      next_variance = sum( pair.games * ( pair.following_pace - next_mean ) ** 2 for pair in pairs )
      covariance = sum(
         pair.games * ( pair.prior_pace - prior_mean ) * ( pair.following_pace - next_mean )
         for pair in pairs )
      correlation = (
         0.0 if prior_variance <= 0.0 or next_variance <= 0.0
         else max( 0.0, min( 1.0, covariance / sqrt( prior_variance * next_variance ) ) ) )
      return ProductionCoefficient(
         from_age,
         to_age,
         next_mean / prior_mean,
         correlation ** 2,
         len( pairs ) )
