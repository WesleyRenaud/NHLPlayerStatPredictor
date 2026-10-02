from __future__ import annotations

import pytest

from api.skaters.skater_stat_rates import SkaterStatRates
from api.time import Time


@pytest.mark.parametrize( 'unit_scale', [ 1.0, Time.SECONDS_PER_MINUTE ] )
def Test_TimeOnIcePerGame_TestWeightedIce_ExpectInputUnitPreserved( unit_scale: float ) -> None:
   first_games = 50
   second_games = 22
   first_ice = 18.5 * unit_scale
   second_ice = 21.0 * unit_scale
   games = first_games + second_games
   total_ice = first_ice * first_games + second_ice * second_games

   assert SkaterStatRates.time_on_ice_per_game( total_ice, games ) == pytest.approx( total_ice / games )


@pytest.mark.parametrize( 'shots', [ None, 0 ] )
def Test_ShootingPercentage_TestUnavailableShots_ExpectNone( shots: int | None ) -> None:
   assert SkaterStatRates.shooting_percentage( 0, shots ) is None


@pytest.mark.parametrize( 'goals, shots', [ ( 0, 100 ), ( 30, 200 ) ] )
def Test_ShootingPercentage_TestRecordedShots_ExpectRatio( goals: int, shots: int ) -> None:
   assert SkaterStatRates.shooting_percentage( goals, shots ) == pytest.approx( 100 * goals / shots )


def Test_ShootingPercentageFromPaces_TestProjectedRates_ExpectUnroundedRatio() -> None:
   goals_pace = 30.4
   shots_pace = 200.6

   assert SkaterStatRates.shooting_percentage_from_paces( goals_pace, shots_pace ) == pytest.approx(
      100 * goals_pace / shots_pace )


@pytest.mark.parametrize( 'shots_pace', [ None, 0.0 ] )
def Test_ShootingPercentageFromPaces_TestUnavailableShots_ExpectNone( shots_pace: float | None ) -> None:
   assert SkaterStatRates.shooting_percentage_from_paces( 0.0, shots_pace ) is None
