from __future__ import annotations

from dataclasses import replace

import pytest

from api.projections.scoring_paces import ScoringPaces
from api.projections.scoring_stat import ScoringStat
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_year import PriorYear
from api.recency.production_growth import ProductionGrowth
from api.recency.production_season import ProductionSeason
from api.recency.production_trajectory import ProductionTrajectory
from api.recency.production_trajectory_fit import ProductionTrajectoryFit
from api.recency.production_trajectory_share import ProductionTrajectoryShare
from api.recency.production_weight import ProductionWeight


AGE_18_TO_19_MULTIPLIER = 1.2
AGE_19_TO_20_MULTIPLIER = 1.1
LATEST_RELATIONSHIP_WEIGHT = 0.9
OLDER_RELATIONSHIP_WEIGHT = 0.5


def _prior( year: int, age: int, goals: float, nhl_games: int = 82 ) -> PriorYear:
   return PriorYear(
      year, ScoringPaces( goals, goals, 0.0, 0.0, 0.0, 0.0 ),
      0.0, 82, nhl_games, age + 0.4 )


def _fit() -> ProductionTrajectoryFit:
   return ProductionTrajectoryFit( 0.15, [
      ProductionTrajectoryShare( age, 0.65, 0.40 ) for age in range( 15, 35 )
   ] )


def _model() -> PaceRegressionModel:
   return PaceRegressionModel( [
      ProductionGrowth( 18, 19, AGE_18_TO_19_MULTIPLIER, 100 ),
      ProductionGrowth( 19, 20, AGE_19_TO_20_MULTIPLIER, 100 ),
      ProductionGrowth( 18, 20, AGE_18_TO_19_MULTIPLIER * AGE_19_TO_20_MULTIPLIER, 100 )
   ], history_weights=[
      ProductionWeight( 18, 19, 0.8, 100 ),
      ProductionWeight( 19, 20, LATEST_RELATIONSHIP_WEIGHT, 100 ),
      ProductionWeight( 18, 20, OLDER_RELATIONSHIP_WEIGHT, 100 )
   ], trajectory=_fit() )


def _trajectory_average(
      latest: PriorYear,
      older: PriorYear,
      latest_weight: float,
      older_weight: float,
      latest_value: float,
      older_value: float,
      fit: ProductionTrajectoryFit ) -> float:
   history = [
      ProductionSeason( int( latest.age ), latest_value, latest.games ),
      ProductionSeason( int( older.age ), older_value, older.games ),
   ]
   bases = [
      latest_weight * PriorYear.reliability( latest.games ),
      older_weight * PriorYear.reliability( older.games ),
   ]
   shares = ProductionTrajectory.shares( history, bases, fit )
   return ( latest_value * shares[ 0 ] + older_value * shares[ 1 ] ) / sum( shares )


def Test_Paces_TestWeightedHistory_ExpectAverageThenAgeGrowth() -> None:
   priors = [ _prior( 2024, 19, 20.0 ), _prior( 2023, 18, 10.0 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   latest, older = priors
   weighted_goals = _trajectory_average(
      latest, older, LATEST_RELATIONSHIP_WEIGHT, OLDER_RELATIONSHIP_WEIGHT,
      latest.scoring.goals, older.scoring.goals, _fit() )
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
   expected = _trajectory_average(
      latest, older, LATEST_RELATIONSHIP_WEIGHT, OLDER_RELATIONSHIP_WEIGHT,
      latest.scoring.goals, older.scoring.goals, model.trajectory ) * annual_multiplier
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


def Test_Paces_TestSteadyIncline_ExpectOldestSeasonFaded() -> None:
   annual_multiplier = 1.2
   prior_ages = ( 15, 16, 17 )
   rise = 0.65
   model = PaceRegressionModel( [
      ProductionGrowth( age, age + 1, annual_multiplier, 100 )
      for age in prior_ages
   ], history_weights=[
      ProductionWeight( age, 18, 1.0, 100 ) for age in prior_ages
   ], trajectory=ProductionTrajectoryFit( 0.15, [
      ProductionTrajectoryShare( age, rise, None ) for age in prior_ages
   ] ) )
   priors = [
      _prior( 2025, 17, 20.0, nhl_games=0 ),
      _prior( 2024, 16, 15.0, nhl_games=0 ),
      _prior( 2023, 15, 10.0, nhl_games=0 )
   ]

   paced = PaceRegressionPredictor.paces( model, priors, 20262027, [] )

   assert paced is not None
   rest = ( 1.0 - rise ) / 2.0
   expected = ( 20.0 * rise + 15.0 * rest + 10.0 * rest ) * annual_multiplier
   assert paced.goals == pytest.approx( expected )


def Test_Paces_TestAllScoringComponents_ExpectSharedGrowthAndHistoryBlend() -> None:
   latest_scoring = ScoringPaces( 20.0, 30.0, 5.0, 10.0, 1.0, 2.0 )
   older_scoring = ScoringPaces( 10.0, 15.0, 4.0, 8.0, 2.0, 1.0 )
   priors = [ PriorYear( 2024, latest_scoring, 0.0, 82, 82, 19.4 ),
      PriorYear( 2023, older_scoring, 0.0, 41, 0, 18.4 ) ]

   paced = PaceRegressionPredictor.paces( _model(), priors, 20252026, [] )

   assert paced is not None
   expected_by_stat = {}

   for stat in ScoringStat:
      expected_by_stat[ stat ] = _trajectory_average(
         priors[ 0 ], priors[ 1 ], LATEST_RELATIONSHIP_WEIGHT, OLDER_RELATIONSHIP_WEIGHT,
         getattr( latest_scoring, stat.value ), getattr( older_scoring, stat.value ), _fit()
      ) * AGE_19_TO_20_MULTIPLIER
      assert getattr( paced, stat.value ) == pytest.approx( expected_by_stat[ stat ] )

   assert paced.goals + paced.assists == pytest.approx( sum( expected_by_stat.values() ) )


def Test_Paces_TestDebutRise_ExpectLatestSeasonKept() -> None:
   debut = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), debut_trajectory=debut )
   priors = [ _prior( 2024, 19, 40.0, nhl_games=0 ), _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( 40.0 * AGE_19_TO_20_MULTIPLIER )


def Test_Paces_TestShortNhlRise_ExpectLatestSeasonKept() -> None:
   short = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), short_nhl_trajectory=short )
   priors = [ _prior( 2024, 19, 40.0, nhl_games=9 ), _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( 40.0 * AGE_19_TO_20_MULTIPLIER )


def Test_Paces_TestRookieRise_ExpectLatestSeasonKept() -> None:
   rookie = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), rookie_trajectory=rookie )
   priors = [ _prior( 2024, 19, 40.0 ), _prior( 2023, 18, 10.0, nhl_games=0 ) ]

   paced = PaceRegressionPredictor.paces( model, priors, 20252026, [] )

   assert paced is not None
   assert paced.goals == pytest.approx( 40.0 * AGE_19_TO_20_MULTIPLIER )


def Test_Paces_TestSmallRookieStep_ExpectGeneralShareKept() -> None:
   rookie = ProductionTrajectoryFit( 0.40, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), rookie_trajectory=rookie )
   priors = [ _prior( 2024, 19, 40.0 ), _prior( 2023, 18, 25.0, nhl_games=0 ) ]

   assert PaceRegressionPredictor.paces( model, priors, 20252026, [] ) == (
      PaceRegressionPredictor.paces( _model(), priors, 20252026, [] ) )


def Test_Paces_TestRookieDrop_ExpectGeneralShareKept() -> None:
   rookie = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, 0.2 ) ] )
   model = replace( _model(), rookie_trajectory=rookie )
   priors = [ _prior( 2024, 19, 10.0 ), _prior( 2023, 18, 40.0, nhl_games=0 ) ]

   assert PaceRegressionPredictor.paces( model, priors, 20252026, [] ) == (
      PaceRegressionPredictor.paces( _model(), priors, 20252026, [] ) )


def Test_Paces_TestRookieGap_ExpectGeneralShareKept() -> None:
   rookie = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), rookie_trajectory=rookie )
   priors = [ _prior( 2024, 19, 40.0 ), _prior( 2022, 17, 10.0, nhl_games=0 ) ]

   assert PaceRegressionPredictor.paces( model, priors, 20252026, [] ) == (
      PaceRegressionPredictor.paces( _model(), priors, 20252026, [] ) )


def Test_Paces_TestEstablishedRookie_ExpectRookieShareUnused() -> None:
   rookie = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), rookie_trajectory=rookie )
   priors = [ _prior( 2024, 19, 40.0 ), _prior( 2023, 18, 10.0, nhl_games=26 ) ]

   assert PaceRegressionPredictor.paces( model, priors, 20252026, [] ) == (
      PaceRegressionPredictor.paces( _model(), priors, 20252026, [] ) )


def Test_Paces_TestEstablishedSeason_ExpectShortShareUnused() -> None:
   short = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), short_nhl_trajectory=short )
   priors = [ _prior( 2024, 19, 20.0 ), _prior( 2023, 18, 10.0 ) ]

   assert PaceRegressionPredictor.paces( model, priors, 20252026, [] ) == (
      PaceRegressionPredictor.paces( _model(), priors, 20252026, [] ) )


def Test_Paces_TestEstablishedSeason_ExpectDebutShareUnused() -> None:
   debut = ProductionTrajectoryFit( 0.15, [ ProductionTrajectoryShare( 19, 1.0, None ) ] )
   model = replace( _model(), debut_trajectory=debut )
   priors = [ _prior( 2024, 19, 20.0 ), _prior( 2023, 18, 10.0 ) ]

   assert PaceRegressionPredictor.paces( model, priors, 20252026, [] ) == (
      PaceRegressionPredictor.paces( _model(), priors, 20252026, [] ) )
