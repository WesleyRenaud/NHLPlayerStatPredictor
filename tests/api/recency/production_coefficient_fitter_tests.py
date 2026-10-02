from __future__ import annotations

import pytest

from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.recency.production_pair import ProductionPair
from api.shared.enums.position import Position


def Test_Fit_TestMultiplicativePairs_ExpectGrowthAndCorrelation() -> None:
   multiplier = 1.5
   pairs = [ ProductionPair( 18, 19, float( value ), multiplier * value, 82.0 ) for value in range( 1, 31 ) ]

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == pytest.approx( multiplier )
   # A positive exact linear relationship has correlation squared equal to one.
   assert coefficient.weight == pytest.approx( 1.0 )
   assert coefficient.samples == len( pairs )


def Test_Fit_TestOffsetPairs_ExpectMatchedCohortGrowth() -> None:
   pairs = [ ProductionPair( 18, 19, float( value ), 5.0 + value, 82.0 ) for value in range( 1, 31 ) ]
   expected = sum( pair.following_pace for pair in pairs ) / sum( pair.prior_pace for pair in pairs )

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == pytest.approx( expected )


def Test_Fit_TestSinglePositiveSample_ExpectNeutralFallback() -> None:
   pairs = [ ProductionPair( 18, 19, 0.0, 2.0, 82.0 ) ] * 91 + [ ProductionPair( 18, 19, 1.235, 12.0, 28.0 ) ]

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == 1.0
   assert coefficient.weight == 0.0


def Test_Fit_TestSparseAge_ExpectNeighborPooling() -> None:
   pairs = [ ProductionPair( 18, 19, 1.0, 100.0, 1.0 ) ]
   pairs.extend( ProductionPair( 19, 20, float( value ), float( value ), 82.0 ) for value in range( 1, 31 ) )

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   expected_multiplier = sum( pair.games * pair.following_pace for pair in pairs ) / sum(
      pair.games * pair.prior_pace for pair in pairs )
   assert coefficient.samples == len( pairs )
   assert coefficient.multiplier == pytest.approx( expected_multiplier )


def Test_Fit_TestConstantAndNegativeRelationship_ExpectZeroWeight() -> None:
   constant = [ ProductionPair( 18, 19, 2.0, 3.0, 82.0 ) ] * 30
   negative = [ ProductionPair( 18, 19, float( value ), 31.0 - value, 82.0 ) for value in range( 1, 31 ) ]

   assert ProductionCoefficientFitter.fit( constant )[ Position.FIRST ].weight == 0.0
   assert ProductionCoefficientFitter.fit( negative )[ Position.FIRST ].weight == 0.0


def Test_Fit_TestUnequalGames_ExpectGamesWeightedGrowth() -> None:
   pairs = [ ProductionPair( 18, 19, 1.0, 1.0, 82.0 ) ] * 20 + [ ProductionPair( 18, 19, 4.0, 10.0, 20.0 ) ]
   expected = sum( pair.games * pair.following_pace for pair in pairs ) / sum(
      pair.games * pair.prior_pace for pair in pairs )

   assert ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ].multiplier == pytest.approx( expected )


def Test_Fit_TestNoisyStableCohort_ExpectNeutralGrowthAndReducedReliability() -> None:
   pairs = [
      ProductionPair( 28, 29, float( value ), float( value + 1 if value % 2 else value - 1 ), 82.0 )
      for value in range( 1, 31 )
   ]
   prior_mean = sum( pair.prior_pace for pair in pairs ) / len( pairs )
   following_mean = sum( pair.following_pace for pair in pairs ) / len( pairs )
   covariance = sum( ( pair.prior_pace - prior_mean ) * ( pair.following_pace - following_mean ) for pair in pairs )
   prior_variance = sum( ( pair.prior_pace - prior_mean ) ** 2 for pair in pairs )
   following_variance = sum( ( pair.following_pace - following_mean ) ** 2 for pair in pairs )

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert following_mean == prior_mean
   assert coefficient.multiplier == pytest.approx( 1.0 )
   assert coefficient.weight == pytest.approx( covariance ** 2 / ( prior_variance * following_variance ) )
   assert 0.0 < coefficient.weight < 1.0


def Test_Fit_TestZeroFollowingProduction_ExpectZeroGrowthAndWeight() -> None:
   pairs = [ ProductionPair( 28, 29, float( value ), 0.0, 82.0 ) for value in range( 1, 31 ) ]

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == 0.0
   assert coefficient.weight == 0.0
