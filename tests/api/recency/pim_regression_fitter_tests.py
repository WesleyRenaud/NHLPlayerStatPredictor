from __future__ import annotations

from datetime import date

import pytest

from api.recency.pim_regression_fitter import PimRegressionFitter
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
      power_play_points=0,
      short_handed_goals=0,
      short_handed_points=0 )


def Test_Fit_TestPimRuleAcrossAges_ExpectAgeFreeRegression() -> None:
   seasons: list[ NhlSkaterSeason ] = []
   pim_constant = 4
   pim_weight = 2

   for player_id in range( 60 ):
      prior_pim = player_id % 12 * 5
      age = 18.4 + player_id % 30
      seasons.append( _season( player_id, 2020, age, prior_pim ) )
      seasons.append( _season( player_id, 2021, age + 1.0, pim_constant + pim_weight * prior_pim ) )

   model = PimRegressionFitter.fit( seasons )

   assert len( model.regressions ) == 1
   regression = model.regressions[ Position.FIRST ]
   assert regression.constant == pytest.approx( pim_constant )
   assert regression.weights == pytest.approx( [ pim_weight ] )


def Test_Fit_TestMissedSeason_ExpectPimGapScale() -> None:
   seasons: list[ NhlSkaterSeason ] = []
   consecutive_multiplier = 2
   returning_multiplier = 1.6

   for player_id in range( 60 ):
      prior_pim = ( player_id % 12 + 1 ) * 5
      age = 18.4 + player_id % 30
      seasons.append( _season( player_id, 2020, age, prior_pim ) )
      seasons.append( _season( player_id, 2021, age + 1.0, prior_pim * consecutive_multiplier ) )
      returning_id = player_id + 60
      seasons.append( _season( returning_id, 2020, age, prior_pim ) )
      seasons.append( _season( returning_id, 2022, age + 2.0, int( prior_pim * returning_multiplier ) ) )

   model = PimRegressionFitter.fit( seasons )

   assert model.regressions[ Position.FIRST ].constant == pytest.approx( 0.0 )
   assert model.regressions[ Position.FIRST ].weights == pytest.approx( [ consecutive_multiplier ] )
   assert model.nhl_gap_scale == pytest.approx( returning_multiplier / consecutive_multiplier )
