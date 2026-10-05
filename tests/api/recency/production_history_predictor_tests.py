from __future__ import annotations

import pytest

from api.recency.prior_year import PriorYear
from api.recency.production_growth import ProductionGrowth
from api.recency.production_history_predictor import ProductionHistoryPredictor
from api.recency.production_season import ProductionSeason
from api.recency.production_trajectory_fit import ProductionTrajectoryFit
from api.recency.production_weight import ProductionWeight


ANNUAL_MULTIPLIER = 2.0
LATEST_WEIGHT = 1.0
OLDER_WEIGHT = 0.5
EMPTY = ProductionTrajectoryFit.empty()


def _season( age: int, pace: float, games: int ) -> ProductionSeason:
   return ProductionSeason( age, pace, games )


def _lookup( from_age: int, to_age: int ) -> ProductionGrowth:
   return ProductionGrowth( from_age, to_age, ANNUAL_MULTIPLIER, 100 )


def _weight_lookup( from_age: int, to_age: int ) -> ProductionWeight:
   weight = LATEST_WEIGHT if from_age == 20 else OLDER_WEIGHT
   return ProductionWeight( from_age, to_age, weight, 100 )


def Test_Pace_TestHistory_ExpectRawAverageThenLatestAgeMultiplier() -> None:
   history = [ _season( 20, 20.0, 80 ), _season( 19, 5.0, 40 ) ]

   pace = ProductionHistoryPredictor.pace( history, 21, _lookup, _weight_lookup, EMPTY )

   latest, older = history
   latest_weight = PriorYear.reliability( latest.games ) * LATEST_WEIGHT
   older_weight = PriorYear.reliability( older.games ) * OLDER_WEIGHT
   weighted_average = (
      latest.pace * latest_weight + older.pace * older_weight
   ) / ( latest_weight + older_weight )
   assert pace == pytest.approx( weighted_average * ANNUAL_MULTIPLIER )


@pytest.mark.parametrize( 'latest_games, older_games', [
   ( 20, 20 ),
   ( 20, 60 ),
   ( 35, 61 ),
   ( 82, 20 ),
] )
def Test_Pace_TestQualifiedSeasonLengths_ExpectSameProjection(
      latest_games: int,
      older_games: int ) -> None:
   history = [ _season( 20, 20.0, latest_games ), _season( 19, 5.0, older_games ) ]

   pace = ProductionHistoryPredictor.pace( history, 21, _lookup, _weight_lookup, EMPTY )

   assert pace == pytest.approx(
      ( 20.0 * LATEST_WEIGHT + 5.0 * OLDER_WEIGHT )
      / ( LATEST_WEIGHT + OLDER_WEIGHT ) * ANNUAL_MULTIPLIER )


@pytest.mark.parametrize( 'games', [ 0, 5, 10, 19 ] )
def Test_Pace_TestSmallSample_ExpectReducedSeasonWeight( games: int ) -> None:
   history = [ _season( 20, 20.0, 60 ), _season( 19, 5.0, games ) ]
   latest_weight = PriorYear.reliability( 60 ) * LATEST_WEIGHT
   older_weight = PriorYear.reliability( games ) * OLDER_WEIGHT

   pace = ProductionHistoryPredictor.pace( history, 21, _lookup, _weight_lookup, EMPTY )

   assert pace == pytest.approx(
      ( 20.0 * latest_weight + 5.0 * older_weight )
      / ( latest_weight + older_weight ) * ANNUAL_MULTIPLIER )


def Test_Pace_TestMissedSeason_ExpectCompoundedAgeMultipliers() -> None:
   prior_age = 19
   prior_pace = 5.0
   target_age = 22
   pace = ProductionHistoryPredictor.pace( [ _season( prior_age, prior_pace, 82 ) ], target_age, _lookup, _weight_lookup, EMPTY )

   assert pace == pytest.approx( prior_pace * ANNUAL_MULTIPLIER ** ( target_age - prior_age ) )


def Test_Pace_TestZeroProduction_ExpectZeroProjection() -> None:
   assert ProductionHistoryPredictor.pace( [ _season( 20, 0.0, 82 ), _season( 19, 0.0, 82 ) ], 21, _lookup, _weight_lookup, EMPTY ) == 0.0


def Test_Pace_TestUnsupportedWeights_ExpectLatestSeasonFallback() -> None:
   annual_multiplier = 1.2
   latest_pace = 10.0

   def lookup( from_age: int, to_age: int ) -> ProductionGrowth:
      return ProductionGrowth( from_age, to_age, annual_multiplier, 0 )

   def weight_lookup( from_age: int, to_age: int ) -> ProductionWeight:
      return ProductionWeight( from_age, to_age, 0.0, 0 )

   history = [ _season( 20, latest_pace, 82 ), _season( 19, 100.0, 82 ) ]
   assert ProductionHistoryPredictor.pace( history, 21, lookup, weight_lookup, EMPTY ) == pytest.approx( latest_pace * annual_multiplier )


def Test_Coefficient_TestUnknownAge_ExpectNearestAgeForSameLag() -> None:
   coefficients = [ ProductionGrowth( 18, 19, 1.2, 100 ) ]

   coefficient = ProductionHistoryPredictor.coefficient( coefficients, 19, 20 )
   missing = ProductionHistoryPredictor.coefficient( coefficients, 19, 22 )

   assert coefficient == coefficients[ 0 ]
   assert missing.multiplier == 1.0
   assert isinstance( missing, ProductionGrowth )


def Test_Coefficient_TestUnsupportedOldAge_ExpectClosestSupportedAge() -> None:
   coefficients = [
      ProductionGrowth( 25, 26, 0.99, 100 ),
      ProductionGrowth( 40, 41, 0.87, 36 ),
      ProductionGrowth( 41, 42, 0.83, 20 ),
   ]

   assert ProductionHistoryPredictor.coefficient( coefficients, 42, 43 ) == coefficients[ 2 ]
   assert ProductionHistoryPredictor.coefficient( coefficients, 45, 46 ) == coefficients[ 2 ]


def Test_Weight_TestUnknownAge_ExpectNearestAgeForSameLag() -> None:
   weights = [ ProductionWeight( 18, 19, 0.8, 100 ) ]

   weight = ProductionHistoryPredictor.weight( weights, 19, 20 )
   missing = ProductionHistoryPredictor.weight( weights, 19, 22 )

   assert weight == weights[ 0 ]
   assert missing.weight == 0.0
   assert isinstance( missing, ProductionWeight )


def Test_Pace_TestSeparateUnsupportedWeights_ExpectLatestNhlGrowthFallback() -> None:
   annual_multiplier = 1.2
   latest_pace = 10.0

   def lookup( from_age: int, to_age: int ) -> ProductionGrowth:
      return ProductionGrowth( from_age, to_age, annual_multiplier, 100 )

   def weight_lookup( from_age: int, to_age: int ) -> ProductionWeight:
      return ProductionWeight( from_age, to_age, 0.0, 100 )

   history = [ _season( 18, latest_pace, 82 ), _season( 17, 100.0, 82 ) ]
   pace = ProductionHistoryPredictor.pace( history, 20, lookup, weight_lookup, EMPTY )

   assert pace == pytest.approx( latest_pace * annual_multiplier ** ( 20 - history[ 0 ].age ) )
