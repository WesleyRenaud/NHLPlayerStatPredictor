from __future__ import annotations

import pytest

from api.projections.scoring_paces import ScoringPaces
from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_year import PriorYear
from api.recency.production_growth import ProductionGrowth
from api.recency.production_weight import ProductionWeight


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
      ProductionGrowth( 18, 19, AGE_18_TO_19_MULTIPLIER, 100 ),
      ProductionGrowth( 19, 20, AGE_19_TO_20_MULTIPLIER, 100 ),
      ProductionGrowth( 18, 20, AGE_18_TO_19_MULTIPLIER * AGE_19_TO_20_MULTIPLIER, 100 )
   ], history_weights=[
      ProductionWeight( 18, 19, 0.8, 100 ),
      ProductionWeight( 19, 20, LATEST_RELATIONSHIP_WEIGHT, 100 ),
      ProductionWeight( 18, 20, OLDER_RELATIONSHIP_WEIGHT, 100 )
   ] )


def Test_Paces_TestWeightedHistory_ExpectAverageThenAgeGrowth() -> None:
   priors = [ _prior( 2024, 19, 20.0 ), _prior( 2023, 18, 10.0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   latest_weight = latest.games * LATEST_RELATIONSHIP_WEIGHT
   older_weight = older.games * OLDER_RELATIONSHIP_WEIGHT
   weighted_goals = (
      latest.scoring.goals * latest_weight + older.scoring.goals * older_weight
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


def Test_Paces_TestMixedSources_ExpectSameWeightsAndGrowthAsNhlHistory() -> None:
   nhl_multiplier = 1.2
   latest_reliability = 1.0
   older_reliability = 0.5
   model = PaceRegressionModel( [
      ProductionGrowth( 18, 19, nhl_multiplier, 100 ),
      ProductionGrowth( 19, 20, nhl_multiplier, 100 ),
      ProductionGrowth( 18, 20, nhl_multiplier ** 2, 100 )
   ], history_weights=[ ProductionWeight( 19, 20, latest_reliability, 100 ),
      ProductionWeight( 18, 20, older_reliability, 100 ) ] )
   priors = [ _prior( 2024, 19, 10.0 ), _prior( 2023, 18, 5.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   latest_weight = latest.games * latest_reliability
   older_weight = older.games * older_reliability
   expected_goals = (
      latest.scoring.goals * latest_weight + older.scoring.goals * older_weight
   ) / ( latest_weight + older_weight ) * nhl_multiplier
   assert paced.goals == pytest.approx( expected_goals )
   nhl_priors = [ _prior( prior.year, int( prior.age ), prior.scoring.goals ) for prior in priors ]
   assert paced == PaceRegressionPredictor.paces( model, nhl_priors, 20252026, [] )


def Test_Paces_TestTranslatedMultiYearHistory_ExpectSameGrowthAsNhlHistory() -> None:
   annual_multiplier = 2.0
   model = PaceRegressionModel( [
      ProductionGrowth( 18, 19, annual_multiplier, 100 ),
      ProductionGrowth( 19, 20, annual_multiplier, 100 ),
      ProductionGrowth( 18, 20, annual_multiplier ** 2, 100 )
   ], history_weights=_model().history_weights )
   priors = [ _prior( 2024, 19, 20.0, nhl_games=0 ), _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   latest_weight = latest.games * LATEST_RELATIONSHIP_WEIGHT
   older_weight = older.games * OLDER_RELATIONSHIP_WEIGHT
   expected = (
      latest.scoring.goals * latest_weight + older.scoring.goals * older_weight
   ) / ( latest_weight + older_weight ) * annual_multiplier
   assert paced.goals == pytest.approx( expected )
   nhl_priors = [ _prior( prior.year, int( prior.age ), prior.scoring.goals ) for prior in priors ]
   assert paced == PaceRegressionPredictor.paces( model, nhl_priors, 20252026, [] )


def Test_Paces_TestTranslatedMissedSeason_ExpectSharedAnnualAgeGrowth() -> None:
   annual_multiplier = 2.0
   model = PaceRegressionModel( [
      ProductionGrowth( 18, 19, annual_multiplier, 100 ),
      ProductionGrowth( 19, 20, annual_multiplier, 100 ),
      ProductionGrowth( 18, 20, annual_multiplier ** 2, 100 )
   ], history_weights=[ ProductionWeight( 18, 20, 1.0, 100 ) ] )
   priors = [ _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( priors[ 0 ].scoring.goals * annual_multiplier ** 2 )


def Test_Paces_TestYoungTranslatedHistory_ExpectLatestAgeGrowthOnly() -> None:
   annual_multiplier = 1.2
   prior_ages = ( 15, 16, 17 )
   model = PaceRegressionModel( [
      ProductionGrowth( age, age + 1, annual_multiplier, 100 )
      for age in prior_ages
   ], history_weights=[
      ProductionWeight( age, 18, 1.0, 100 ) for age in prior_ages
   ] )
   priors = [
      _prior( 2025, 17, 20.0, nhl_games=0 ),
      _prior( 2024, 16, 15.0, nhl_games=0 ),
      _prior( 2023, 15, 10.0, nhl_games=0 )
   ]

   paced = PaceRegressionPredictor.paces( model, priors, 20262027, [] )

   assert paced is not None
   expected = sum(
      prior.scoring.goals * prior.games
      for prior in priors ) / sum( prior.games for prior in priors ) * annual_multiplier
   assert paced.goals == pytest.approx( expected )


def Test_Paces_TestAllScoringComponents_ExpectSharedGrowthAndHistoryBlend() -> None:
   latest_scoring = ScoringPaces( 20.0, 30.0, 5.0, 10.0, 1.0, 2.0 )
   older_scoring = ScoringPaces( 10.0, 15.0, 4.0, 8.0, 2.0, 1.0 )
   priors = [ PriorYear( 2024, latest_scoring, 0.0, 82, 82, 19.4 ),
      PriorYear( 2023, older_scoring, 0.0, 41, 0, 18.4 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   latest_weight = LATEST_RELATIONSHIP_WEIGHT
   older_weight = OLDER_RELATIONSHIP_WEIGHT

   for stat in ScoringStat:
      expected = (
         getattr( latest_scoring, stat.value ) * latest_weight
         + getattr( older_scoring, stat.value ) * older_weight
      ) / ( latest_weight + older_weight ) * AGE_19_TO_20_MULTIPLIER
      assert getattr( paced, stat.value ) == pytest.approx( expected )

   latest_points = latest_scoring.goals + latest_scoring.assists
   older_points = older_scoring.goals + older_scoring.assists
   expected_points = (
      latest_points * latest_weight + older_points * older_weight
   ) / ( latest_weight + older_weight ) * AGE_19_TO_20_MULTIPLIER
   assert paced.goals + paced.assists == pytest.approx( expected_points )
