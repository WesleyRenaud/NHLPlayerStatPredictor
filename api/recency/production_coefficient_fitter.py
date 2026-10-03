from __future__ import annotations

from functools import partial

from .production_coefficient import ProductionCoefficient
from .production_growth import ProductionGrowth
from .production_history_predictor import ProductionHistoryPredictor
from .production_pair import ProductionPair
from .production_weight import ProductionWeight


class ProductionCoefficientFitter():
   MIN_SUPPORT = 20


   @classmethod
   def fit(
         cls,
         pairs: list[ ProductionPair ] ) -> list[ ProductionCoefficient ]:
      """Keep history weights at every lag, but derive growth from annual fits."""
      groups = cls._training_groups( pairs )
      weights = cls._normalized_weights( groups )
      growth = cls.fit_growth( pairs )
      lookup = partial( ProductionHistoryPredictor.coefficient, growth )

      coefficients = [
         ProductionCoefficient( from_age, to_age,
            ProductionHistoryPredictor.multiplier( lookup, from_age, to_age ),
            weights[ ( from_age, to_age ) ].weight, len( selected ) )
         for ( from_age, to_age ), selected in groups.items()
      ]
      return sorted( coefficients, key=lambda coefficient: ( coefficient.to_age, coefficient.from_age ) )


   @classmethod
   def fit_growth( cls, pairs: list[ ProductionPair ] ) -> list[ ProductionGrowth ]:
      """Fit annual growth only; the predictor compounds longer transitions."""
      annual_pairs = [ pair for pair in pairs if pair.to_age == pair.from_age + 1 ]
      growth = [
         ProductionGrowth( from_age, to_age, cls._multiplier( selected ), len( selected ) )
         for ( from_age, to_age ), selected in cls._training_groups( annual_pairs ).items()
      ]
      return sorted( growth, key=lambda coefficient: ( coefficient.to_age, coefficient.from_age ) )


   @classmethod
   def fit_weights(
         cls,
         pairs: list[ ProductionPair ] ) -> list[ ProductionWeight ]:
      weights = list( cls._normalized_weights( cls._training_groups( pairs ) ).values() )
      return sorted( weights, key=lambda weight: ( weight.to_age, weight.from_age ) )


   @classmethod
   def _normalized_weights(
         cls,
         groups: dict[ tuple[ int, int ], list[ ProductionPair ] ] ) -> dict[ tuple[ int, int ], ProductionWeight ]:
      weights = {
         transition: ProductionWeight(
            *transition, cls._weight( selected ), len( selected ) )
         for transition, selected in groups.items()
      }
      totals_by_target_age: dict[ int, float ] = {}

      for weight in weights.values():
         totals_by_target_age[ weight.to_age ] = (
            totals_by_target_age.get( weight.to_age, 0.0 ) + weight.weight )

      return {
         transition: ProductionWeight(
            weight.from_age,
            weight.to_age,
            weight.weight / totals_by_target_age[ weight.to_age ]
            if totals_by_target_age[ weight.to_age ] > 0.0 else weight.weight,
            weight.samples )
         for transition, weight in weights.items()
      }


   @classmethod
   def _training_groups(
         cls,
         pairs: list[ ProductionPair ] ) -> dict[ tuple[ int, int ], list[ ProductionPair ] ]:
      """Omit unsupported exact-age transitions instead of pooling other ages."""
      samples_by_age_transition: dict[ tuple[ int, int ], list[ ProductionPair ] ] = {}

      for from_age, to_age in sorted( { ( pair.from_age, pair.to_age ) for pair in pairs } ):
         selected = [
            pair for pair in pairs
            if pair.from_age == from_age and pair.to_age == to_age
         ]

         if cls._support( selected ) < cls.MIN_SUPPORT:
            continue

         samples_by_age_transition[ ( from_age, to_age ) ] = selected

      return samples_by_age_transition


   @classmethod
   def _support( cls, pairs: list[ ProductionPair ] ) -> int:
      return sum( pair.prior_pace > 0.0 for pair in pairs )


   @classmethod
   def _multiplier( cls, pairs: list[ ProductionPair ] ) -> float:
      if cls._support( pairs ) < cls.MIN_SUPPORT:
         return 1.0

      return sum( pair.following_pace * pair.games for pair in pairs ) / sum(
         pair.prior_pace * pair.games for pair in pairs )


   @classmethod
   def _weight( cls, pairs: list[ ProductionPair ] ) -> float:
      informative = [ pair for pair in pairs if max( pair.prior_pace, pair.following_pace ) > 0.0 ]

      if len( informative ) < cls.MIN_SUPPORT:
         return 0.0

      return sum(
         pair.games * (
            min( pair.prior_pace, pair.following_pace ) /
            max( pair.prior_pace, pair.following_pace )
         ) ** 4
         for pair in informative
      ) / sum( pair.games for pair in informative )
