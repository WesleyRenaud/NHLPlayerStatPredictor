from __future__ import annotations

from unittest.mock import Mock

import pytest

from api.recency.production_coefficient_fitter import ProductionCoefficientFitter
from api.recency.production_pair import ProductionPair
from api.shared.enums.position import Position


def Test_Fit_TestMultiplicativePairs_ExpectGrowthAndNormalizedWeight() -> None:
   multiplier = 1.5
   pairs = [ ProductionPair( 18, 19, float( value ), multiplier * value, 82.0 ) for value in range( 1, 31 ) ]

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == pytest.approx( multiplier )
   assert coefficient.weight == 1.0
   assert coefficient.samples == len( pairs )


def Test_Fit_TestOffsetPairs_ExpectMatchedCohortGrowth() -> None:
   pairs = [ ProductionPair( 18, 19, float( value ), 5.0 + value, 82.0 ) for value in range( 1, 31 ) ]
   expected = sum( pair.following_pace for pair in pairs ) / sum( pair.prior_pace for pair in pairs )

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == pytest.approx( expected )


def Test_Fit_TestSinglePositiveSample_ExpectOmittedTransition() -> None:
   pairs = [ ProductionPair( 18, 19, 0.0, 0.0, 82.0 ) ] * 91 + [ ProductionPair( 18, 19, 1.235, 12.0, 28.0 ) ]

   assert ProductionCoefficientFitter.fit( pairs ) == []
   assert ProductionCoefficientFitter.fit_growth( pairs ) == []
   assert ProductionCoefficientFitter.fit_weights( pairs ) == []


def Test_Fit_TestSparseAge_ExpectNoNeighborOrAllAgePooling() -> None:
   pairs = [ ProductionPair( 18, 19, 1.0, 100.0, 1.0 ) ]
   pairs.extend( ProductionPair( 19, 20, float( value ), float( value ), 82.0 ) for value in range( 1, 31 ) )
   pairs.append( ProductionPair( 42, 43, 1.0, 100.0, 1.0 ) )

   coefficients = ProductionCoefficientFitter.fit( pairs )

   assert len( coefficients ) == 1
   coefficient = coefficients[ Position.FIRST ]
   assert ( coefficient.from_age, coefficient.to_age ) == ( 19, 20 )
   assert coefficient.samples == 30
   assert coefficient.multiplier == 1.0


@pytest.mark.parametrize( 'sample_count', [ 19, 20 ] )
def Test_FitGrowth_TestSupportThreshold_ExpectOnlySupportedTransitions( sample_count: int ) -> None:
   pairs = [ ProductionPair( 42, 43, 10.0, 9.0, 82.0 ) ] * sample_count

   growth = ProductionCoefficientFitter.fit_growth( pairs )

   assert len( growth ) == ( 1 if sample_count == 20 else 0 )
   if growth:
      assert growth[ 0 ].samples == sample_count
      assert growth[ 0 ].multiplier == pytest.approx( 0.9 )


def Test_Fit_TestConstantAndReversedRelationship_ExpectNormalizedWeights() -> None:
   constant = [ ProductionPair( 18, 19, 2.0, 3.0, 82.0 ) ] * 30
   negative = [ ProductionPair( 18, 19, float( value ), 31.0 - value, 82.0 ) for value in range( 1, 31 ) ]

   for pairs in ( constant, negative ):
      assert ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ].weight == 1.0


def Test_Fit_TestUnequalGames_ExpectGamesWeightedGrowth() -> None:
   pairs = [ ProductionPair( 18, 19, 1.0, 1.0, 82.0 ) ] * 20 + [ ProductionPair( 18, 19, 4.0, 10.0, 20.0 ) ]
   expected = sum( pair.games * pair.following_pace for pair in pairs ) / sum(
      pair.games * pair.prior_pace for pair in pairs )

   assert ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ].multiplier == pytest.approx( expected )


def Test_Fit_TestNoisyStableCohort_ExpectNeutralGrowthAndNormalizedWeight() -> None:
   pairs = [
      ProductionPair( 28, 29, float( value ), float( value + 1 if value % 2 else value - 1 ), 82.0 )
      for value in range( 1, 31 )
   ]
   prior_mean = sum( pair.prior_pace for pair in pairs ) / len( pairs )
   following_mean = sum( pair.following_pace for pair in pairs ) / len( pairs )
   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert following_mean == prior_mean
   assert coefficient.multiplier == pytest.approx( 1.0 )
   assert coefficient.weight == 1.0


def Test_Fit_TestZeroFollowingProduction_ExpectZeroGrowthAndWeight() -> None:
   pairs = [ ProductionPair( 28, 29, float( value ), 0.0, 82.0 ) for value in range( 1, 31 ) ]

   coefficient = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]

   assert coefficient.multiplier == 0.0
   assert coefficient.weight == 0.0


def Test_FitGrowth_TestSupportedPairs_ExpectNoReliabilityCalculation(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   multiplier = 1.5
   pairs = [ ProductionPair( 18, 19, float( value ), multiplier * value, 82.0 ) for value in range( 1, 31 ) ]
   weight = Mock( side_effect=AssertionError( 'Growth fitting must not calculate reliability' ) )
   monkeypatch.setattr( ProductionCoefficientFitter, '_weight', weight )

   growth = ProductionCoefficientFitter.fit_growth( pairs )[ Position.FIRST ]

   assert growth.multiplier == pytest.approx( multiplier )
   assert growth.samples == len( pairs )
   weight.assert_not_called()


def Test_FitWeights_TestSupportedPairs_ExpectNoGrowthCalculation(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   pairs = [ ProductionPair( 18, 19, float( value ), 2.0 * value, 82.0 ) for value in range( 1, 31 ) ]
   multiplier = Mock( side_effect=AssertionError( 'Reliability fitting must not calculate growth' ) )
   monkeypatch.setattr( ProductionCoefficientFitter, '_multiplier', multiplier )

   weight = ProductionCoefficientFitter.fit_weights( pairs )[ Position.FIRST ]

   assert weight.weight == 1.0
   assert weight.samples == len( pairs )
   multiplier.assert_not_called()


@pytest.mark.parametrize( 'sample_count', [ 20, 30 ] )
def Test_Fit_TestSeparateGrowthFit_ExpectSameGrowthAsCombinedFit( sample_count: int ) -> None:
   pairs = [ ProductionPair( 18, 19, float( value ), 2.0 * value + 1, float( value ) )
      for value in range( 1, sample_count + 1 ) ]

   combined = ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ]
   growth = ProductionCoefficientFitter.fit_growth( pairs )[ Position.FIRST ]
   weight = ProductionCoefficientFitter.fit_weights( pairs )[ Position.FIRST ]

   assert growth.multiplier == pytest.approx( combined.multiplier )
   assert weight.weight == pytest.approx( combined.weight )
   if sample_count < ProductionCoefficientFitter.MIN_SUPPORT:
      assert weight.weight == 0.0
   else:
      assert weight.weight == 1.0
   assert growth.samples == weight.samples == combined.samples


def Test_FitWeights_TestDifferentTransitions_ExpectTargetAgeThenPriorAgeOrder() -> None:
   transitions = [ ( 18, 21 ), ( 19, 20 ), ( 17, 20 ), ( 18, 19 ) ]
   pairs = [ ProductionPair( from_age, to_age, float( value ), 2.0 * value, 82.0 )
      for from_age, to_age in transitions for value in range( 1, 31 ) ]

   weights = ProductionCoefficientFitter.fit_weights( pairs )

   assert [ ( weight.from_age, weight.to_age ) for weight in weights ] == sorted(
      transitions, key=lambda transition: ( transition[ 1 ], transition[ 0 ] ) )
   assert sum( weight.weight for weight in weights if weight.to_age == 20 ) == pytest.approx( 1.0 )
   assert sum( weight.weight for weight in weights if weight.to_age == 19 ) == pytest.approx( 1.0 )
   assert sum( weight.weight for weight in weights if weight.to_age == 21 ) == pytest.approx( 1.0 )


def Test_FitWeights_TestIdenticalRates_ExpectFullSimilarityWithoutVariance() -> None:
   pairs = [ ProductionPair( 18, 19, 20.0, 20.0, 82.0 ) ] * 30

   assert ProductionCoefficientFitter.fit_weights( pairs )[ Position.FIRST ].weight == 1.0


def Test_FitWeights_TestReciprocalChanges_ExpectNormalizedWeights() -> None:
   multiplier = 2.0
   growth = [ ProductionPair( 18, 19, float( value ), multiplier * value, 82.0 ) for value in range( 1, 31 ) ]
   decline = [ ProductionPair( 18, 19, pair.following_pace, pair.prior_pace, pair.games ) for pair in growth ]

   assert ProductionCoefficientFitter.fit_weights( growth )[ Position.FIRST ].weight == 1.0
   assert ProductionCoefficientFitter.fit_weights( decline )[ Position.FIRST ].weight == 1.0


def Test_FitWeights_TestChangesCancelInMean_ExpectReducedSimilarity() -> None:
   prior_rate = 20.0
   multiplier = 2.0
   pairs = [ ProductionPair( 18, 19, prior_rate, prior_rate * multiplier, 82.0 ) ] * 20
   pairs.extend( [ ProductionPair( 18, 19, prior_rate * multiplier, prior_rate, 82.0 ) ] * 20 )

   growth = ProductionCoefficientFitter.fit_growth( pairs )[ Position.FIRST ]
   weight = ProductionCoefficientFitter.fit_weights( pairs )[ Position.FIRST ]

   assert growth.multiplier == 1.0
   assert weight.weight == 1.0


def Test_FitWeights_TestZeroRates_ExpectNoFalseSimilarityOrDivisionByZero() -> None:
   uninformative = [ ProductionPair( 18, 19, 0.0, 0.0, 82.0 ) ] * 30
   disappearing = [ ProductionPair( 18, 19, 20.0, 0.0, 82.0 ) ] * 30

   assert ProductionCoefficientFitter.fit_weights( uninformative ) == []
   assert ProductionCoefficientFitter.fit_weights( disappearing )[ Position.FIRST ].weight == 0.0


def Test_Fit_TestUnequalGames_ExpectMeasuredSimilarityInBothFits() -> None:
   stable = ProductionPair( 18, 19, 20.0, 20.0, 82.0 )
   changed = ProductionPair( 18, 19, 20.0, 40.0, 20.0 )
   pairs = [ stable ] * ProductionCoefficientFitter.MIN_SUPPORT + [ changed ]
   assert ProductionCoefficientFitter.fit( pairs )[ Position.FIRST ].weight == 1.0
   assert ProductionCoefficientFitter.fit_weights( pairs )[ Position.FIRST ].weight == 1.0


def Test_FitWeights_TestDifferentReliabilityAtSameTargetAge_ExpectNormalizedSimilarityShares() -> None:
   pairs = [
      ProductionPair( 16, 18, 10.0, 20.0, 82.0 ),
      ProductionPair( 17, 18, 10.0, 10.0, 82.0 ),
   ] * 20

   weights = ProductionCoefficientFitter.fit_weights( pairs )

   by_from_age = { weight.from_age: weight.weight for weight in weights }
   assert by_from_age[ 16 ] == pytest.approx( 1 / 17 )
   assert by_from_age[ 17 ] == pytest.approx( 16 / 17 )


def Test_FitGrowth_TestUnsortedTransitions_ExpectTargetAgeThenSourceAgeOrder() -> None:
   transitions = [ ( 20, 21 ), ( 19, 20 ), ( 17, 18 ), ( 18, 19 ) ]
   pairs = [
      ProductionPair( from_age, to_age, float( value ), float( value ), 82.0 )
      for from_age, to_age in transitions
      for value in range( 1, 31 )
   ]

   growth = ProductionCoefficientFitter.fit_growth( pairs )

   assert [ ( coefficient.from_age, coefficient.to_age ) for coefficient in growth ] == sorted(
      transitions, key=lambda transition: ( transition[ 1 ], transition[ 0 ] ) )


def Test_FitGrowth_TestContradictoryMultiYearPairs_ExpectOnlyAnnualFits() -> None:
   annual_pairs = [
      ProductionPair( 25, 26, 100.0, 90.0, 82.0 ),
      ProductionPair( 26, 27, 100.0, 80.0, 82.0 ),
      ProductionPair( 27, 28, 100.0, 70.0, 82.0 ),
   ] * ProductionCoefficientFitter.MIN_SUPPORT
   longer_pairs = [
      ProductionPair( 25, 27, 100.0, 200.0, 82.0 ),
      ProductionPair( 25, 28, 100.0, 300.0, 82.0 ),
   ] * ProductionCoefficientFitter.MIN_SUPPORT

   growth = ProductionCoefficientFitter.fit_growth( annual_pairs + longer_pairs )

   assert growth == ProductionCoefficientFitter.fit_growth( annual_pairs )
   assert [ coefficient.multiplier for coefficient in growth ] == pytest.approx( [ 0.9, 0.8, 0.7 ] )
   assert ProductionCoefficientFitter.fit_growth( longer_pairs ) == []
