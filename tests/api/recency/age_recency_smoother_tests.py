from __future__ import annotations

from api.recency.age_recency_fit import AgeRecencyFit
from api.recency.age_recency_smoother import AgeRecencySmoother
from api.recency.age_recency_weights import AgeRecencyWeights
from api.recency.recency_decay_fitter import RecencyDecayFitter
from api.recency.recency_weight import RecencyWeight
from api.shared.enums.position import Position


def _first_weight_one() -> list[ RecencyWeight ]:
   return [
      RecencyWeight( lag, 1.0 if lag == Position.FIRST else 0.0 )
      for lag in range( RecencyDecayFitter.WINDOW )
   ]


def _equal_weights() -> list[ RecencyWeight ]:
   weight = 1.0 / RecencyDecayFitter.WINDOW
   return [
      RecencyWeight( lag, weight )
      for lag in range( RecencyDecayFitter.WINDOW )
   ]


def Test_Smooth_TestLastYearOnly_ExpectFirstWeightOne() -> None:
   rows = [ AgeRecencyFit( 19, _first_weight_one(), 1 ) ]

   smoothed = AgeRecencySmoother.smooth( rows )

   assert smoothed == [ AgeRecencyWeights( 19, _first_weight_one() ) ]


def Test_Smooth_TestEqualWeights_ExpectEvenMix() -> None:
   rows = [ AgeRecencyFit( 28, _equal_weights(), 1 ) ]

   smoothed = AgeRecencySmoother.smooth( rows )

   assert smoothed == [ AgeRecencyWeights( 28, _equal_weights() ) ]


def Test_Smooth_TestNeighborRates_ExpectHalfwayGeometric() -> None:
   nineteen = AgeRecencyFit( 19, _first_weight_one(), 1 )
   twenty = AgeRecencyFit( 20, _equal_weights(), 1 )
   total = 1.0 + 0.5 + 0.25 + 0.125

   smoothed = AgeRecencySmoother.smooth( [ nineteen, twenty ] )

   halfway = [
      RecencyWeight( 0, 1.0 / total ),
      RecencyWeight( 1, 0.5 / total ),
      RecencyWeight( 2, 0.25 / total ),
      RecencyWeight( 3, 0.125 / total )
   ]
   assert smoothed == [
      AgeRecencyWeights( 19, halfway ),
      AgeRecencyWeights( 20, halfway ),
   ]
