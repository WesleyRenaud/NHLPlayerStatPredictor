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


ANNUAL_PIM_MULTIPLIER = 2


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
      even_strength_goals=0,
      even_strength_points=0,
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
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0 )


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
         ( player_id % 12 + 1 ) * 5 * ANNUAL_PIM_MULTIPLIER )
      for player_id in range( 60 ) )
   return PimRegressionFitter.fit( seasons )


def Test_Pace_TestPreviousSeason_ExpectMultiplicativeProjection() -> None:
   model = _model()
   history = [ _season( 100, 2020, 43.7, 25 ) ]

   prior = history[ 0 ]
   expected_pim = prior.penalty_minutes * prior.pace_games / prior.games_played * ANNUAL_PIM_MULTIPLIER
   assert PimRegressionPredictor.pace( model, history, 20212022 ) == pytest.approx( expected_pim )


def Test_Pace_TestMissedSeason_ExpectCompoundedAgeGrowth() -> None:
   prior = _season( 100, 2020, 43.7, 25 )
   elapsed_seasons = 2022 - 2020
   expected_pim = (
      prior.penalty_minutes * prior.pace_games / prior.games_played
      * ANNUAL_PIM_MULTIPLIER ** elapsed_seasons )
   assert PimRegressionPredictor.pace( _model(), [ prior ], 20222023 ) == pytest.approx( expected_pim )


def Test_Pace_TestNoHistory_ExpectNone() -> None:
   assert PimRegressionPredictor.pace( _model(), [], 20212022 ) is None
