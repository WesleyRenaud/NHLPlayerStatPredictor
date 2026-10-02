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


def Test_Fit_TestMultiplicativePim_ExpectAgeMultipliers() -> None:
   annual_multiplier = 2
   seasons = [
      _season( player_id, year, 18.4 + year - 2020, player_id * annual_multiplier ** ( year - 2020 ) )
      for player_id in range( 1, 31 )
      for year in range( 2020, 2023 )
   ]

   model = PimRegressionFitter.fit( seasons )
   coefficients = model.coefficients

   assert next( coefficient for coefficient in coefficients if coefficient.from_age == 18 and coefficient.to_age == 19 ).multiplier == pytest.approx( annual_multiplier )
   assert next( coefficient for coefficient in coefficients if coefficient.from_age == 18 and coefficient.to_age == 20 ).weight == pytest.approx( 1.0 )


def Test_Fit_TestNoPairs_ExpectEmptyModel() -> None:
   assert PimRegressionFitter.fit( [] ).coefficients == []
