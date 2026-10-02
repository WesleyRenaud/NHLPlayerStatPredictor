from __future__ import annotations

import pytest

from api.projections.scoring_paces import ScoringPaces
from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression import PaceRegression
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_source import PriorSource
from api.recency.prior_year import PriorYear
from api.recency.production_coefficient import ProductionCoefficient


AGE_18_TO_19_MULTIPLIER = 1.2
AGE_19_TO_20_MULTIPLIER = 1.1
LATEST_RELATIONSHIP_WEIGHT = 0.9
OLDER_RELATIONSHIP_WEIGHT = 0.5


def _prior( year: int, age: int, goals: float, nhl_games: int = 82 ) -> PriorYear:
   return PriorYear(
      year, ScoringPaces( goals, goals, 0.0, 0.0, 0.0, 0.0 ),
      0.0, 82, nhl_games, age + 0.4 )


def _model() -> PaceRegressionModel:
   return PaceRegressionModel( [
      PaceRegression( source, stat, [
         ProductionCoefficient( 18, 19, AGE_18_TO_19_MULTIPLIER, 0.8, 100 ),
         ProductionCoefficient( 19, 20, AGE_19_TO_20_MULTIPLIER, LATEST_RELATIONSHIP_WEIGHT, 100 ),
         ProductionCoefficient( 18, 20, AGE_18_TO_19_MULTIPLIER * AGE_19_TO_20_MULTIPLIER, OLDER_RELATIONSHIP_WEIGHT, 100 )
      ] )
      for source in PriorSource
      for stat in ( ScoringStat.EVEN_STRENGTH_GOALS, ScoringStat.EVEN_STRENGTH_ASSISTS )
   ] )


def Test_Paces_TestWeightedHistory_ExpectAverageThenAgeGrowth() -> None:
   priors = [ _prior( 2024, 19, 20.0 ), _prior( 2023, 18, 10.0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   normalized_older_goals = older.scoring.goals * AGE_18_TO_19_MULTIPLIER
   latest_weight = latest.games * LATEST_RELATIONSHIP_WEIGHT
   older_weight = older.games * OLDER_RELATIONSHIP_WEIGHT
   weighted_goals = (
      latest.scoring.goals * latest_weight + normalized_older_goals * older_weight
   ) / ( latest_weight + older_weight )
   assert paced.goals == pytest.approx( weighted_goals * AGE_19_TO_20_MULTIPLIER )
   assert paced.power_play_goals == 0.0
   assert paced.penalty_minutes is None


def Test_Paces_TestMissedSeason_ExpectActualElapsedAgeGrowth() -> None:
   priors = [ _prior( 2023, 18, 10.0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx(
      priors[ 0 ].scoring.goals * AGE_18_TO_19_MULTIPLIER * AGE_19_TO_20_MULTIPLIER )


def Test_Paces_TestTranslatedHistory_ExpectSameMultiplicativeWorkflow() -> None:
   priors = [ _prior( 2024, 19, 20.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( priors[ 0 ].scoring.goals * AGE_19_TO_20_MULTIPLIER )


def Test_Paces_TestNoHistory_ExpectNone() -> None:
   assert PaceRegressionPredictor.paces( _model(), [], 20252026, [] ) is None


def Test_Paces_TestMixedSources_ExpectEachPriorUsesItsSource() -> None:
   nhl_multiplier = 1.0
   translated_multiplier = 2.0
   model = PaceRegressionModel( [
      PaceRegression( source, stat, [
         ProductionCoefficient( 18, 19, multiplier, 1.0, 100 ),
         ProductionCoefficient( 19, 20, multiplier, 1.0, 100 ),
         ProductionCoefficient( 18, 20, multiplier ** 2, 1.0, 100 )
      ] )
      for source, multiplier in ( ( PriorSource.NHL, nhl_multiplier ), ( PriorSource.TRANSLATED, translated_multiplier ) )
      for stat in ( ScoringStat.EVEN_STRENGTH_GOALS, ScoringStat.EVEN_STRENGTH_ASSISTS )
   ] )
   priors = [ _prior( 2024, 19, 10.0 ), _prior( 2023, 18, 5.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   normalized_older_goals = older.scoring.goals * translated_multiplier
   expected_goals = (
      latest.scoring.goals * latest.games + normalized_older_goals * older.games
   ) / ( latest.games + older.games ) * nhl_multiplier
   assert paced.goals == pytest.approx( expected_goals )
