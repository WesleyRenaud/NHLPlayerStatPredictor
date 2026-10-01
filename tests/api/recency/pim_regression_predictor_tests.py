from __future__ import annotations

from datetime import date

import pytest

from api.recency.pim_regression_fitter import PimRegressionFitter
from api.recency.pim_regression_model import PimRegressionModel
from api.recency.pim_regression_predictor import PimRegressionPredictor
from api.shared.enums.position import Position
from api.skaters.nhl_skater_season import NhlSkaterSeason
from api.skaters.skater_position import SkaterPosition
from api.skaters.team import Team


def _season( player_id: int, year: int, age: float, pim: int ) -> NhlSkaterSeason:
   return NhlSkaterSeason(
      player_id=player_id,
      season_id=year * 10000 + year + 1,
      player_name='Stub Skater',
      position=SkaterPosition( 'C' ),
      birth_date=date( 1997, 1, 13 ),
      age=age,
      team=list( Team )[ Position.FIRST ],
      games_played=82,
      goals=0,
      assists=0,
      points=0,
      schedule_games=82,
      pace_games=82,
      g_pace=0.0,
      a_pace=0.0,
      p_pace=0.0,
      penalty_minutes=pim,
      gp_share=1.0,
      playoff_games=0,
      playoff_goals=0,
      playoff_assists=0,
      power_play_goals=0,
      power_play_points=0 )


def _model() -> PimRegressionModel:
   seasons = [
      _season( player_id, 2020, 18.4 + player_id % 30, ( player_id % 12 + 1 ) * 5 )
      for player_id in range( 60 )
   ]
   seasons.extend(
      _season(
         player_id,
         2021,
         19.4 + player_id % 30,
         ( player_id % 12 + 1 ) * 10 )
      for player_id in range( 60 ) )
   return PimRegressionFitter.fit( seasons )


def Test_Pace_TestPreviousSeason_ExpectPimProjection() -> None:
   model = _model()
   history = [ _season( 100, 2020, 43.7, 25 ) ]
   regression = model.regressions[ Position.FIRST ]
   prior_pim_pace = history[ Position.FIRST ].penalty_minutes_pace()
   expected = regression.constant + sum(
      weight * prior_pim_pace
      for weight in regression.weights )

   pim_pace = PimRegressionPredictor.pace( model, history, 20212022 )

   assert pim_pace == pytest.approx( expected )


def Test_Pace_TestMissedSeason_ExpectGapScaleApplied() -> None:
   seasons: list[ NhlSkaterSeason ] = []

   for player_id in range( 60 ):
      prior_pim = ( player_id % 12 + 1 ) * 5
      age = 18.4 + player_id % 30
      seasons.append( _season( player_id, 2020, age, prior_pim ) )
      seasons.append( _season( player_id, 2021, age + 1.0, prior_pim * 2 ) )
      returning_id = player_id + 60
      seasons.append( _season( returning_id, 2020, age, prior_pim ) )
      seasons.append( _season( returning_id, 2022, age + 2.0, int( prior_pim * 1.6 ) ) )

   model = PimRegressionFitter.fit( seasons )
   history = [ _season( 100, 2020, 43.7, 25 ) ]
   regression = model.regressions[ Position.FIRST ]
   prior_pim_pace = history[ Position.FIRST ].penalty_minutes_pace()
   expected = (
      regression.constant
      + sum( weight * prior_pim_pace for weight in regression.weights )
   ) * model.nhl_gap_scale

   pim_pace = PimRegressionPredictor.pace( model, history, 20222023 )

   assert pim_pace == pytest.approx( expected )


def Test_Pace_TestNoHistory_ExpectNone() -> None:
   assert PimRegressionPredictor.pace( _model(), [], 20212022 ) is None