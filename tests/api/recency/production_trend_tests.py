from __future__ import annotations

from datetime import date

import pytest

from api.projections.scoring_paces import ScoringPaces
from api.recency.pace_regression_model import PaceRegressionModel
from api.recency.pace_regression_predictor import PaceRegressionPredictor
from api.recency.prior_year import PriorYear
from api.recency.production_growth import ProductionGrowth
from api.recency.production_keep_fit import ProductionKeepFit
from api.recency.production_trend import ProductionTrend
from api.recency.production_trend_line import ProductionTrendLine
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _line( paces: list[ float ] ) -> ProductionTrendLine:
   return ProductionTrendLine.fit( paces )


def _nhl( year: int, age: int, pace: int, games: int = 82 ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=1,
      season_id=year * 10000 + year + 1,
      age=age,
      games_played=games,
      goals=pace,
      assists=0,
      points=pace,
      g_pace=float( pace ),
      a_pace=0.0,
      position=SkaterPosition.CENTER,
      player_name='Trend',
      birth_date=date( 1990, 1, 1 ),
      team=Team.NEW_YORK_RANGERS,
      schedule_games=82,
      pace_games=82,
      p_pace=float( pace ),
      penalty_minutes=0,
      gp_share=None,
      power_play_goals=0,
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0,
      even_strength_goals=pace,
      even_strength_points=pace,
      shots=0 )


def _prior( year: int, age: int, pace: float ) -> PriorYear:
   return PriorYear(
      year,
      ScoringPaces( pace, 0.0, 0.0, 0.0, 0.0, 0.0 ),
      0.0,
      82,
      82,
      age )


def _kept_pace(
      prior_paces: list[ int ],
      latest_pace: int,
      growth: float,
      keep: ProductionKeepFit ) -> float:
   line = _line( [ float( pace ) for pace in prior_paces ] )
   at_latest_age = ProductionTrend.at_latest( line.level, float( latest_pace ), keep.kept_above )

   return at_latest_age * growth


def Test_Fit_TestEvenSteps_ExpectNewestPaceAndStepOverLevel() -> None:
   paces = [ 10.0, 20.0, 30.0, 40.0, 50.0 ]
   line = ProductionTrendLine.fit( paces )
   mean_pace = sum( paces ) / len( paces )
   step = paces[ 1 ] - paces[ 0 ]
   half_span = ( len( paces ) - 1 ) / 2.0

   assert line.level == pytest.approx( paces[ -1 ] )
   assert line.level == pytest.approx( mean_pace + step * half_span )


def Test_Seasons_TestSixFullYears_ExpectOldestToNewest() -> None:
   seasons = [ _nhl( year, 20 + year - 2020, 40 ) for year in range( 2020, 2026 ) ]

   assert ProductionTrend.seasons( list( reversed( seasons ) ), 2026 ) == seasons


def Test_Seasons_TestMissingYear_ExpectNone() -> None:
   seasons = [ _nhl( year, 20, 40 ) for year in range( 2020, 2026 ) if year != 2022 ]

   assert ProductionTrend.seasons( seasons, 2026 ) is None


def Test_FullSeason_TestOneFullSeason_ExpectThatSeason() -> None:
   season = _nhl( 2025, 32, 40 )

   assert ProductionTrend.full_season( [ season ] ) is season


def Test_FullSeason_TestShortSeason_ExpectNone() -> None:
   short = _nhl( 2025, 32, 10, games=PriorYear.MIN_GAMES - 1 )

   assert ProductionTrend.full_season( [ short ] ) is None


def Test_FullSeason_TestTwoFullSeasons_ExpectNone() -> None:
   first = _nhl( 2025, 32, 40 )
   second = _nhl( 2025, 32, 50 )

   assert ProductionTrend.full_season( [ first, second ] ) is None


def Test_AtLatest_TestPartialKeep_ExpectLevelPlusKeptGap() -> None:
   level = 94.0
   latest_pace = 66.0
   kept = 0.5
   gap = latest_pace - level

   assert ProductionTrend.at_latest( level, latest_pace, kept ) == pytest.approx(
      level + kept * gap )


def Test_Paces_TestFivePriorSeasons_ExpectKeptGapThenAgeGrowth() -> None:
   prior_paces = [ 72, 74, 97, 93, 90 ]
   latest_pace = 67
   growth = 0.9
   kept = 0.5
   keep = ProductionKeepFit( kept_above=kept )
   seasons = [
      _nhl( year, age, pace )
      for year, age, pace in zip(
         range( 2020, 2026 ),
         range( 27, 33 ),
         prior_paces + [ latest_pace ],
         strict=True )
   ]
   model = PaceRegressionModel( [ ProductionGrowth( 32, 33, growth, 20 ) ], keep=keep )

   paced = PaceRegressionPredictor.paces(
      model,
      [ _prior( 2025, 32, float( latest_pace ) ) ],
      20262027,
      seasons )

   assert paced is not None
   assert paced.even_strength_goals == pytest.approx(
      _kept_pace( prior_paces, latest_pace, growth, keep ) )


def Test_Paces_TestThreeSeasons_ExpectBlend() -> None:
   priors = [ _prior( 2025, 32, 60.0 ), _prior( 2024, 31, 88.0 ), _prior( 2023, 30, 90.0 ) ]
   seasons = [
      _nhl( prior.year, prior.age, int( prior.scoring.even_strength_goals ) )
      for prior in priors
   ]
   model = PaceRegressionModel( [] )

   paced = PaceRegressionPredictor.paces( model, priors, 20262027, seasons )
   blended = PaceRegressionPredictor.paces( model, priors, 20262027, [] )

   assert paced is not None and blended is not None
   assert paced.even_strength_goals == pytest.approx( blended.even_strength_goals )


def Test_Paces_TestShortLatestSeason_ExpectBlend() -> None:
   full = [ _nhl( year, 30 + index, 40 + index ) for index, year in enumerate( range( 2020, 2025 ) ) ]
   short = _nhl( 2025, 35, 10, games=10 )
   priors = [ _prior( 2025, 35, 10.0 ), _prior( 2024, 34, 44.0 ), _prior( 2023, 33, 43.0 ) ]
   model = PaceRegressionModel( [] )

   paced = PaceRegressionPredictor.paces( model, priors, 20262027, full + [ short ] )
   blended = PaceRegressionPredictor.paces( model, priors, 20262027, [] )

   assert paced is not None and blended is not None
   assert paced.even_strength_goals == pytest.approx( blended.even_strength_goals )
