from __future__ import annotations

from datetime import date

import pytest

from api.recency.prior_year import PriorYear
from api.recency.production_growth import ProductionGrowth
from api.recency.production_keep_fit import ProductionKeepFit
from api.recency.production_keep_fitter import ProductionKeepFitter
from api.recency.production_keep_sample import ProductionKeepSample
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _sample(
      relative_slope: float,
      level: float,
      latest_pace: float,
      adjusted_following: float,
      games: int = 10 ) -> ProductionKeepSample:
   return ProductionKeepSample(
      relative_slope, level, latest_pace, adjusted_following, games )


def _share( samples: list[ ProductionKeepSample ] ) -> float:
   numerator = 0.0
   denominator = 0.0

   for sample in samples:
      gap = sample.latest_pace - sample.level

      if gap == 0.0:
         continue

      numerator += sample.games * ( sample.adjusted_following - sample.level ) * gap
      denominator += sample.games * gap * gap

   return min( 1.0, max( 0.0, numerator / denominator ) )


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
      player_name='Keep',
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


def _window( following_games: int = 82, following_pace: int = 80 ) -> list[ NhlSkaterSeason ]:
   seasons = [
      _nhl( year, 25 + year - 2018, 40 )
      for year in range( 2018, 2023 )
   ]
   seasons.append( _nhl( 2023, 30, 60 ) )
   seasons.append( _nhl( 2024, 31, following_pace, games=following_games ) )

   return seasons


def Test_Fit_TestKnownGaps_ExpectOneLeastSquaresShare() -> None:
   samples = [
      _sample( -0.5, 80.0, 40.0, 60.0, 10 ),
      _sample( -0.2, 50.0, 30.0, 40.0, 20 ),
      _sample( -0.1, 40.0, 40.0, 10.0, 30 ),
      _sample( 0.0, 40.0, 55.0, 46.0, 40 ),
      _sample( 0.2, 40.0, 70.0, 60.0, 15 ),
      _sample( 0.4, 40.0, 90.0, 50.0, 25 ),
   ]
   share = _share( samples )
   decline = samples[ 0 ]
   rise = samples[ -1 ]

   fit = ProductionKeepFitter.fit( samples )

   assert fit.bands == []
   assert fit.kept_above == pytest.approx( share )
   assert fit.kept( decline.relative_slope ) == pytest.approx( share )
   assert fit.kept( rise.relative_slope ) == pytest.approx( share )


def Test_Fit_TestNoGap_ExpectEmpty() -> None:
   samples = [
      _sample( slope, 40.0, 40.0, 50.0 )
      for slope in ( -0.5, -0.2, -0.1, 0.0, 0.2, 0.4 )
   ]

   assert ProductionKeepFitter.fit( samples ) == ProductionKeepFit.empty()


def Test_Observe_TestSevenFullSeasons_ExpectAgeAdjustedFollowing() -> None:
   latest_pace = 60.0
   following_pace = 80.0
   following_games = 40
   multiplier = 2.0
   seasons = _window( following_games, int( following_pace ) )
   growth = ProductionGrowth( 30, 31, multiplier, 10 )

   samples = ProductionKeepFitter.observe( seasons, [ growth ] )

   assert len( samples ) == 1
   sample = samples[ 0 ]
   assert sample.level == pytest.approx( 40.0 )
   assert sample.relative_slope == pytest.approx( 0.0 )
   assert sample.latest_pace == pytest.approx( latest_pace )
   assert sample.adjusted_following == pytest.approx( following_pace / multiplier )
   assert sample.games == min( 82, following_games )


def Test_Observe_TestMissingYear_ExpectNoSample() -> None:
   missing_season_id = 2021 * 10000 + 2022
   seasons = [ season for season in _window() if season.season_id != missing_season_id ]

   assert ProductionKeepFitter.observe( seasons, [] ) == []


def Test_Observe_TestShortSeason_ExpectNoSample() -> None:
   seasons = _window()
   seasons[ 2 ] = _nhl( 2020, 27, 40, games=PriorYear.MIN_GAMES - 1 )

   assert ProductionKeepFitter.observe( seasons, [] ) == []


def Test_Observe_TestZeroMultiplier_ExpectNoSample() -> None:
   growth = ProductionGrowth( 30, 31, 0.0, 10 )

   assert ProductionKeepFitter.observe( _window(), [ growth ] ) == []
