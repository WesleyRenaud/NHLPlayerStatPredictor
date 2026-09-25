from __future__ import annotations

from api.recency.prior_season_weight_fitter import PriorSeasonWeightFitter
from api.recency.recency_weight import RecencyWeight
from api.shared.enums.position import Position


def _identity_samples( window: int ) -> list[ list[ float ] ]:
   samples: list[ list[ float ] ] = []

   for years_ago in range( window ):
      row = [ 0.0 ] * window
      row[ years_ago ] = float( window )
      samples.append( [ 1.0, *row ] )

   return samples


def Test_Fit_TestLastYearIsTarget_ExpectFirstWeightOne() -> None:
   window = 4
   samples: list[ list[ float ] ] = []

   for years_ago in range( window ):
      row = [ 0.0 ] * window
      row[ Position.FIRST ] = 10.0 * ( years_ago + 1 )

      if years_ago:
         row[ years_ago ] = 5.0

      samples.append( [ row[ Position.FIRST ], *row ] )

   assert PriorSeasonWeightFitter.fit( samples ) == [
      RecencyWeight( years_ago, 1.0 if years_ago == Position.FIRST else 0.0 )
      for years_ago in range( window )
   ]


def Test_Fit_TestMeanOfPriors_ExpectEqualWeights() -> None:
   window = 4
   weight = 1.0 / window
   assert PriorSeasonWeightFitter.fit( _identity_samples( window ) ) == [
      RecencyWeight( years_ago, weight )
      for years_ago in range( window )
   ]


def Test_Fit_TestEightPriors_ExpectEqualWeights() -> None:
   window = 8
   weight = 1.0 / window
   assert PriorSeasonWeightFitter.fit( _identity_samples( window ) ) == [
      RecencyWeight( years_ago, weight )
      for years_ago in range( window )
   ]


def Test_Fit_TestNegativeCoefficient_ExpectClipped() -> None:
   window = 4
   samples: list[ list[ float ] ] = []
   last = window - 1

   for years_ago in range( window ):
      row = [ 0.0 ] * window
      row[ years_ago ] = 1.0
      target = 1.0

      if years_ago == last:
         target = -1.0
      elif years_ago:
         target = 0.0

      samples.append( [ target, *row ] )

   assert PriorSeasonWeightFitter.fit( samples ) == [
      RecencyWeight( years_ago, 1.0 if years_ago == Position.FIRST else 0.0 )
      for years_ago in range( window )
   ]
