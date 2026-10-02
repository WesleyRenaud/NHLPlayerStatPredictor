from __future__ import annotations

import pytest

from api.recency.production_coefficient import ProductionCoefficient
from api.recency.production_history_predictor import ProductionHistoryPredictor


ANNUAL_MULTIPLIER = 2.0
LATEST_WEIGHT = 1.0
OLDER_WEIGHT = 0.5


def _lookup( from_age: int, to_age: int ) -> ProductionCoefficient:
   weight = LATEST_WEIGHT if from_age == 20 else OLDER_WEIGHT
   return ProductionCoefficient( from_age, to_age, ANNUAL_MULTIPLIER, weight, 100 )


def Test_Pace_TestAgeNormalizedHistory_ExpectAverageThenMultiplier() -> None:
   history = [ ( 20, 20.0, 80 ), ( 19, 5.0, 40 ) ]

   pace = ProductionHistoryPredictor.pace( history, 21, _lookup )

   latest_age, latest_pace, latest_games = history[ 0 ]
   older_age, older_pace, older_games = history[ 1 ]
   normalized_older_pace = older_pace * ANNUAL_MULTIPLIER ** ( latest_age - older_age )
   latest_weight = latest_games * LATEST_WEIGHT
   older_weight = older_games * OLDER_WEIGHT
   weighted_average = (
      latest_pace * latest_weight + normalized_older_pace * older_weight
   ) / ( latest_weight + older_weight )
   assert pace == pytest.approx( weighted_average * ANNUAL_MULTIPLIER )


def Test_Pace_TestMissedSeason_ExpectCompoundedAgeMultipliers() -> None:
   prior_age = 19
   prior_pace = 5.0
   target_age = 22
   pace = ProductionHistoryPredictor.pace( [ ( prior_age, prior_pace, 82 ) ], target_age, _lookup )

   assert pace == pytest.approx( prior_pace * ANNUAL_MULTIPLIER ** ( target_age - prior_age ) )


def Test_Pace_TestZeroProduction_ExpectZeroProjection() -> None:
   assert ProductionHistoryPredictor.pace( [ ( 20, 0.0, 82 ), ( 19, 0.0, 82 ) ], 21, _lookup ) == 0.0


def Test_Pace_TestUnsupportedWeights_ExpectLatestSeasonFallback() -> None:
   annual_multiplier = 1.2
   latest_pace = 10.0

   def lookup( from_age: int, to_age: int ) -> ProductionCoefficient:
      return ProductionCoefficient( from_age, to_age, annual_multiplier, 0.0, 0 )

   history = [ ( 20, latest_pace, 82 ), ( 19, 100.0, 82 ) ]
   assert ProductionHistoryPredictor.pace( history, 21, lookup ) == pytest.approx( latest_pace * annual_multiplier )


def Test_Coefficient_TestUnknownAge_ExpectNearestAgeForSameLag() -> None:
   coefficients = [ ProductionCoefficient( 18, 19, 1.2, 0.8, 100 ) ]

   coefficient = ProductionHistoryPredictor.coefficient( coefficients, 19, 20 )
   missing = ProductionHistoryPredictor.coefficient( coefficients, 19, 22 )

   assert coefficient == coefficients[ 0 ]
   assert missing.multiplier == 1.0
   assert missing.weight == 0.0
