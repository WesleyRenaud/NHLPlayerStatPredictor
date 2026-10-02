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


def Test_Paces_TestTranslatedHistory_ExpectSharedNhlAgeGrowth() -> None:
   priors = [ _prior( 2024, 19, 20.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( priors[ 0 ].scoring.goals * AGE_19_TO_20_MULTIPLIER )


def Test_Paces_TestNoHistory_ExpectNone() -> None:
   assert PaceRegressionPredictor.paces( _model(), [], 20252026, [] ) is None


def Test_Paces_TestMixedSources_ExpectSharedGrowthAndSourceSpecificWeights() -> None:
   nhl_multiplier = 1.2
   translated_multiplier = 2.0
   nhl_weight = 1.0
   translated_weight = 0.5
   model = PaceRegressionModel( [
      PaceRegression( source, stat, [
         ProductionCoefficient( 18, 19, multiplier, weight, 100 ),
         ProductionCoefficient( 19, 20, multiplier, weight, 100 ),
         ProductionCoefficient( 18, 20, multiplier ** 2, weight, 100 )
      ] )
      for source, multiplier, weight in (
         ( PriorSource.NHL, nhl_multiplier, nhl_weight ),
         ( PriorSource.TRANSLATED, translated_multiplier, translated_weight ) )
      for stat in ( ScoringStat.EVEN_STRENGTH_GOALS, ScoringStat.EVEN_STRENGTH_ASSISTS )
   ] )
   priors = [ _prior( 2024, 19, 10.0 ), _prior( 2023, 18, 5.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   projected_older_goals = older.scoring.goals * nhl_multiplier ** 2
   latest_weight = latest.games * nhl_weight
   older_weight = older.games * translated_weight
   expected_goals = (
      latest.scoring.goals * nhl_multiplier * latest_weight + projected_older_goals * older_weight
   ) / ( latest_weight + older_weight )
   assert paced.goals == pytest.approx( expected_goals )


def Test_Paces_TestTranslatedMultiYearHistory_ExpectSameGrowthAsNhlHistory() -> None:
   annual_multiplier = 2.0
   two_year_transition = 3.0
   model = PaceRegressionModel( [
      PaceRegression( source, stat, [
         ProductionCoefficient( 18, 19, annual_multiplier, 1.0, 100 ),
         ProductionCoefficient( 19, 20, annual_multiplier, LATEST_RELATIONSHIP_WEIGHT, 100 ),
         ProductionCoefficient( 18, 20, two_year_multiplier, OLDER_RELATIONSHIP_WEIGHT, 100 )
      ] )
      for source, two_year_multiplier in (
         ( PriorSource.NHL, annual_multiplier ** 2 ),
         ( PriorSource.TRANSLATED, two_year_transition ) )
      for stat in ( ScoringStat.EVEN_STRENGTH_GOALS, ScoringStat.EVEN_STRENGTH_ASSISTS )
   ] )
   priors = [ _prior( 2024, 19, 20.0, nhl_games=0 ), _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   latest_weight = latest.games * LATEST_RELATIONSHIP_WEIGHT
   older_weight = older.games * OLDER_RELATIONSHIP_WEIGHT
   expected = (
      latest.scoring.goals * annual_multiplier * latest_weight
      + older.scoring.goals * annual_multiplier ** 2 * older_weight
   ) / ( latest_weight + older_weight )
   assert paced.goals == pytest.approx( expected )
   nhl_priors = [ _prior( prior.year, int( prior.age ), prior.scoring.goals ) for prior in priors ]
   assert paced == PaceRegressionPredictor.paces( model, nhl_priors, 20252026, [] )


def Test_Paces_TestTranslatedMissedSeason_ExpectSharedAnnualAgeGrowth() -> None:
   annual_multiplier = 2.0
   direct_multiplier = 3.0
   model = PaceRegressionModel( [
      PaceRegression( source, ScoringStat.EVEN_STRENGTH_GOALS, [
         ProductionCoefficient( 18, 19, annual_multiplier, 1.0, 100 ),
         ProductionCoefficient( 19, 20, annual_multiplier, 1.0, 100 ),
         ProductionCoefficient( 18, 20, two_year_multiplier, 1.0, 100 )
      ] )
      for source, two_year_multiplier in (
         ( PriorSource.NHL, annual_multiplier ** 2 ),
         ( PriorSource.TRANSLATED, direct_multiplier ) )
   ] )
   priors = [ _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( priors[ 0 ].scoring.goals * annual_multiplier ** 2 )


def Test_Paces_TestYoungTranslatedHistory_ExpectNoTransitionGrowth() -> None:
   annual_multiplier = 1.2
   transition_by_age = { 17: 1.5, 16: 2.0, 15: 2.5 }
   model = PaceRegressionModel( [
      PaceRegression( PriorSource.NHL, ScoringStat.EVEN_STRENGTH_GOALS, [
         ProductionCoefficient( age, age + 1, annual_multiplier, 1.0, 100 )
         for age in transition_by_age
      ] ),
      PaceRegression( PriorSource.TRANSLATED, ScoringStat.EVEN_STRENGTH_GOALS, [
         ProductionCoefficient( age, 18, multiplier, 1.0, 100 )
         for age, multiplier in transition_by_age.items()
      ] )
   ] )
   priors = [
      _prior( 2025, 17, 20.0, nhl_games=0 ),
      _prior( 2024, 16, 15.0, nhl_games=0 ),
      _prior( 2023, 15, 10.0, nhl_games=0 )
   ]

   paced = PaceRegressionPredictor.paces( model, priors, 20262027, [] )

   assert paced is not None
   expected = sum(
      prior.scoring.goals * annual_multiplier ** ( 18 - int( prior.age ) ) * prior.games
      for prior in priors ) / sum( prior.games for prior in priors )
   assert paced.goals == pytest.approx( expected )
